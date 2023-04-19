## DO NOT CHANGE THIS FILE

import os
import numpy as np
import soundfile

from my_submission.user_config import MySeparationModel

class AIcrowdWrapper:
    """
        Entrypoint for the evaluator to connect to the user's agent
        Abstracts some operations that are done on client side
            - Reading sound files from shared disk
            - Checking predictions for basic issues
            - Writing predictions to shared disk
    """
    def __init__(self,
                 dataset_dir='./public_dataset/',
                 predictions_dir='./evaluator_outputs/'):
                 
        self.model = MySeparationModel()
        self.instruments = ['dialog', 'effect', 'music']
        shared_dir = os.getenv("AICROWD_PUBLIC_SHARED_DIR", None)
        if shared_dir is not None:
            self.predictions_dir = os.path.join(shared_dir, 'predictions')
        else:
            self.predictions_dir = predictions_dir
        assert os.path.exists(self.predictions_dir), f'{self.predictions_dir} - No such directory'
        self.dataset_dir = os.getenv("AICROWD_DATASET_DIR", dataset_dir)
        assert os.path.exists(self.dataset_dir), f'{self.dataset_dir} - No such directory'

    def raise_aicrowd_error(self, msg):
        """ Will be used by the evaluator to provide logs """
        raise NameError(msg)

    def check_output(self, separated_music_arrays, output_sample_rates):
        assert set(self.instruments) == set(separated_music_arrays.keys()), "All instrument not present"
    
    def save_prediction(self, foldername, separated_music_arrays, output_sample_rates):
        prediction_path = os.path.join(self.predictions_dir, foldername)
        if not os.path.exists(prediction_path):
            os.mkdir(prediction_path)
            
        for instrument in self.instruments:
            full_path = os.path.join(prediction_path, f'{foldername}_{instrument}.wav')
            soundfile.write(full_path, 
                            data=separated_music_arrays[instrument],
                            samplerate=output_sample_rates[instrument])

    
    def read_mixture_files(self, foldername):
        try:
            lt_path = os.path.join(self.dataset_dir, foldername, f'{foldername}_mixture_Lt.wav')
            rt_path = os.path.join(self.dataset_dir, foldername, f'{foldername}_mixture_Rt.wav')
            lt_array, lt_sr = soundfile.read(lt_path)
            rt_array, rt_sr = soundfile.read(rt_path)
        except soundfile.LibsndfileError:
            lt_path = os.path.join(self.dataset_dir, foldername, 'mix.wav')
            rt_path = os.path.join(self.dataset_dir, foldername, 'mix.wav')
            lt_array, lt_sr = soundfile.read(lt_path)
            rt_array, rt_sr = soundfile.read(rt_path)        
        assert lt_sr == rt_sr
        assert len(lt_array) == len(rt_array)

        mixed_sound_array = np.stack([lt_array, rt_array], axis=1)
        return mixed_sound_array, lt_sr

        

    def separate_music_file(self, foldername):
        mixed_sound_array, sample_rate = self.read_mixture_files(foldername)
        separated_music_arrays, output_sample_rates = self.model.separate_music_file(mixed_sound_array, sample_rate)
        self.check_output(separated_music_arrays, output_sample_rates)
        self.save_prediction(foldername, separated_music_arrays, output_sample_rates)

        return True
