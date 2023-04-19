import numpy as np
import torch
import yaml
from ml_collections import ConfigDict
from my_submission.src.tfc_tdf_v3 import TFC_TDF_net
import warnings
warnings.filterwarnings("ignore")

ckpt_path = 'my_submission/ckpts/tfc_tdf'

model_names = ['model1', 'model2', 'model3']



def load_model(path):
    with open(path+'/config.yaml') as f:
        config = ConfigDict(yaml.load(f, Loader=yaml.FullLoader))
    model = TFC_TDF_net(config).eval().cuda()
    model.load_state_dict(torch.load(path+'/ckpt'))
    return model


class MusicSeparationModel:
    
    def __init__(self):     
        self.models = [load_model(f'{ckpt_path}/{i}') for i in model_names[:-1]]
        self.voice_separator = load_model(f'{ckpt_path}/{model_names[-1]}')

    @property
    def instruments(self):
        """ DO NOT CHANGE """
        return ['bass', 'drums', 'other', 'vocals']

    def raise_aicrowd_error(self, msg):
        """ Will be used by the evaluator to provide logs, DO NOT CHANGE """
        raise NameError(msg)
    
    def separate_music_file(self, mixed_sound_array, sample_rate):

        mixture = torch.tensor(mixed_sound_array.T, dtype=torch.float32) 
        source_dicts = [self.demix(model, mixture) for model in self.models]
        
        separated_music_arrays = {}
        output_sample_rates = {}
        for instrument in self.instruments:
            source = np.mean([sources[instrument] for sources in source_dicts], 0)
            if instrument=='vocals':
                source = (source + self.demix(self.voice_separator, mixture))/2
            separated_music_arrays[instrument] = source.T
            output_sample_rates[instrument] = sample_rate
            
        return separated_music_arrays, output_sample_rates
    
    def demix(self, model, mix):  
        config = model.config
        
        S = model.num_target_instruments
        
        batch_size = config.inference.batch_size
        C = config.audio.hop_length*(config.inference.dim_t-1)
        N = config.inference.num_overlap
        
        H = C//N    
        L = mix.shape[1]    
        pad_size = H-(L-C)%H
        mix = torch.cat([torch.zeros(2,C-H), mix, torch.zeros(2,pad_size + C-H)], 1)
        mix = mix.cuda()

        chunks = []
        i = 0
        while i+C <= mix.shape[1]:
            chunks.append(mix[:, i:i+C])
            i += H
        chunks = torch.stack(chunks)

        batches = []
        i = 0
        while i < len(chunks):
            batches.append(chunks[i:i+batch_size])
            i = i + batch_size

        X = torch.zeros(S,2,C-H) if S > 1 else torch.zeros(2,C-H)
        X = X.cuda()
        with torch.cuda.amp.autocast():
            with torch.no_grad():
                for batch in batches:
                    x = model(batch) 
                    for w in x:
                        a = X[...,:-(C-H)]
                        b = X[...,-(C-H):] + w[...,:(C-H)]
                        c = w[...,(C-H):]
                        X = torch.cat([a,b,c], -1)
        
        estimated_sources = X[..., C-H:-(pad_size+C-H)]/N
        
        if S > 1:
            return {k:v for k,v in zip(config.training.instruments, estimated_sources.cpu().numpy())}
        else:
            return estimated_sources.cpu().numpy()