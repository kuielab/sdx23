import numpy as np
import torch
from demucs import pretrained
from demucs.apply import apply_model
import warnings
warnings.filterwarnings("ignore")

ckpt_path = 'my_submission/ckpts/demucs'

model_names = ['hdemucs_mmi', 'htdemucs_ft']

shifts = 2
overlap = 0.5


class MusicSeparationModel:
    
    def __init__(self):     
        
        # Load your model here and put it into `evaluation` mode
        torch.hub.set_dir('./my_submission/ckpts/demucs/')

        # Use a pre-trained model
        self.models = [pretrained.get_model(name=name).eval() for name in model_names]
               
    @property
    def instruments(self):
        """ DO NOT CHANGE """
        return ['bass', 'drums', 'other', 'vocals']

    def raise_aicrowd_error(self, msg):
        """ Will be used by the evaluator to provide logs, DO NOT CHANGE """
        raise NameError(msg)
    
    def separate_music_file(self, mixed_sound_array, sample_rate):
        """
        Implements the sound separation for a single sound file
        Inputs: Outputs from soundfile.read('mixture.wav')
            mixed_sound_array
            sample_rate

        Outputs:
            separated_music_arrays: Dictionary numpy array of each separated instrument
            output_sample_rates: Dictionary of sample rates separated sequence
        """
        
        mixture = torch.tensor(mixed_sound_array.T, dtype=torch.float32)
        source_dicts = [self.demix(model, mixture) for model in self.models]
        
        separated_music_arrays = {}
        output_sample_rates = {}
        for instrument in self.instruments:
            source = np.mean([sources[instrument] for sources in source_dicts], 0)
            separated_music_arrays[instrument] = source.T
            output_sample_rates[instrument] = sample_rate
            
        return separated_music_arrays, output_sample_rates
    
    def demix(self, model, mix):   
         
        # Normalize track
        mono = mix.mean(0)
        mean = mono.mean()
        std = mono.std()
        mix = (mix - mean) / std
        mix = mix.cuda()
        
        # Separate
        with torch.no_grad():
            estimates = apply_model(model, mix[None], shifts=shifts, overlap=overlap, split=True)[0]
        estimated_sources = estimates * std + mean
        
        return {k:v for k,v in zip(model.sources, estimated_sources.cpu().numpy())}
    
    


