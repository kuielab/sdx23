import numpy as np
import torch
import yaml
from ml_collections import ConfigDict
from my_submission.src.tfc_tdf_v3 import TFC_TDF_net
import warnings
warnings.filterwarnings("ignore")


model_name = 'modelA'
ckpts = ['step100000_seed0', 'step100000_seed1', 'step100000_seed2']

model_path = f'my_submission/ckpts/{model_name}'
config_path = model_path+'/config.yaml'


class MusicSeparationModel:
    
    def __init__(self):     
        
        with open(config_path) as f:
            self.config = ConfigDict(yaml.load(f, Loader=yaml.FullLoader))
       
        self.model = TFC_TDF_net(self.config).eval().cuda()
               
    @property
    def instruments(self):
        """ DO NOT CHANGE """
        return ['bass', 'drums', 'other', 'vocals']

    def raise_aicrowd_error(self, msg):
        """ Will be used by the evaluator to provide logs, DO NOT CHANGE """
        raise NameError(msg)
    
    def separate_music_file(self, mixed_sound_array, sample_rate):
        
        mixture = torch.tensor(mixed_sound_array.T, dtype=torch.float32)
        source_dicts = []
        for ckpt in ckpts:
            self.model.load_state_dict(
                torch.load(model_path+f'/{ckpt}.ckpt')
            )
            source_dicts.append(self.demix(mixture))
        
        separated_music_arrays = {}
        output_sample_rates = {}
        for instrument in self.instruments:
            source = np.mean([sources[instrument] for sources in source_dicts], 0)
            separated_music_arrays[instrument] = source.T
            output_sample_rates[instrument] = sample_rate
                
        residual = mixed_sound_array - np.sum(list(separated_music_arrays.values()), 0)
        separated_music_arrays['other'] += residual/2
            
        return separated_music_arrays, output_sample_rates
    
    def demix(self, mix):  
        
        batch_size = self.config.inference.batch_size
        C = self.config.audio.hop_length * (self.config.inference.dim_t-1)
        N = self.config.inference.num_overlap
        
        H = C//N   # hop size 
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

        X = torch.zeros(len(self.instruments),2,C-H)
        X = X.cuda()
        with torch.cuda.amp.autocast():
            with torch.no_grad():
                for batch in batches:
                    x = self.model(batch) 
                    for w in x:
                        a = X[...,:-(C-H)]
                        b = X[...,-(C-H):] + w[...,:(C-H)]
                        c = w[...,(C-H):]
                        X = torch.cat([a,b,c], -1)

        estimated_sources = X[..., C-H:-(pad_size+C-H)]/N
        
        return {k:v for k,v in zip(self.config.training.instruments, estimated_sources.cpu().numpy())}
