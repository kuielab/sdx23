from my_submission.tfc_tdf import MusicSeparationModel as TFC_TDF
from my_submission.demucs import MusicSeparationModel as DEMUCS



blend_weights = [.2, .2, .6, .8]


class MusicSeparationModel:
    
    def __init__(self):     
        
        self.modelA = TFC_TDF()
        self.modelB = DEMUCS()
        self.blend_weights = {k:v for k,v in zip(self.instruments, blend_weights)}
               
    @property
    def instruments(self):
        """ DO NOT CHANGE """
        return ['bass', 'drums', 'other', 'vocals']

    def raise_aicrowd_error(self, msg):
        """ Will be used by the evaluator to provide logs, DO NOT CHANGE """
        raise NameError(msg)
    
    def separate_music_file(self, mixed_sound_array, sample_rate):
   
        a, sr = self.modelA.separate_music_file(mixed_sound_array, sample_rate)
        b, sr = self.modelB.separate_music_file(mixed_sound_array, sample_rate)
        
        sources = {i: a[i] * w + b[i] * (1-w) for i,w in self.blend_weights.items()} 
            
        return sources, sr
    
    
