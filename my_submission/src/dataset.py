import os
import random
import numpy as np
import torch
import soundfile as sf
import pickle
from tqdm import tqdm
from glob import glob

from utils import load_chunk


class MSSDataset(torch.utils.data.Dataset):
    def __init__(self, config, data_path):  
        self.config = config
        
        self.instruments = instruments = config.training.instruments
        
        metadata_path = data_path+'/metadata'
        try:
            metadata = pickle.load(open(metadata_path, 'rb'))
        except Exception:   
            print('Collecting metadata for', data_path)
            metadata = []
            track_paths = sorted(glob(data_path+'/*'))
            track_paths = [path for path in track_paths if os.path.basename(path)[0]!='.' and os.path.isdir(path)]
            for path in tqdm(track_paths):
                length = len(sf.read(path+f'/{instruments[0]}.wav')[0])
                metadata.append((path, length))
            pickle.dump(metadata, open(metadata_path, 'wb'))              
        
        self.metadata = metadata    
        self.chunk_size = config.audio.chunk_size 
        self.min_mean_abs = config.audio.min_mean_abs
               
    def __len__(self):
        return self.config.training.num_steps * self.config.training.batch_size
    
    def load_source(self, metadata, i):
        while True:
            track_path, track_length = random.choice(metadata)
            source = load_chunk(track_path+f'/{i}.wav', track_length, self.chunk_size)
            if np.abs(source).mean() >= self.min_mean_abs:  # remove quiet chunks
                break
        return torch.tensor(source, dtype=torch.float32)
    
    def __getitem__(self, index):
        return torch.stack([self.load_source(self.metadata, i) for i in self.instruments])

    
    
class DNRDataset(MSSDataset):
    def __init__(self, config, data_path):               
        super().__init__(config, data_path)
        
        self.stereo_prob = config.audio.stereo_prob
    
    def load_source(self, metadata, i):
        while True:
            track_path, track_length = random.choice(metadata)
            if np.random.random() < self.stereo_prob:                  
                x = load_chunk(track_path+f'/{i}.wav', track_length, self.chunk_size*2)
                source = x.reshape(2,-1)
            else:
                x = load_chunk(track_path+f'/{i}.wav', track_length, self.chunk_size)
                source = np.stack([x, x])
            if np.abs(source).mean() >= self.min_mean_abs:  # remove quiet chunks
                break
        return torch.tensor(source, dtype=torch.float32)