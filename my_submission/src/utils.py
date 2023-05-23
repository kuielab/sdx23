import os
import random
import numpy as np
import torch
import soundfile as sf


def manual_seed(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)  # if multi-GPU
    torch.backends.cudnn.deterministic = True
    os.environ["PYTHONHASHSEED"] = str(seed)

    
def num_params(model):
    n = 0
    for param in model.parameters():
        if param.requires_grad:
            n += param.numel()
    return round(n/1e6, 2)
    

def load_chunk(path, length, chunk_size, offset=None):
    if chunk_size <= length:
        if offset is None:
            offset = np.random.randint(length - chunk_size + 1)
        x = sf.read(path, dtype='float32', start=offset, frames=chunk_size)[0]    
    else:
        x = sf.read(path, dtype='float32')[0]
        pad = np.zeros([chunk_size-length,2])
        x = np.concatenate([x, pad])
    return x.T

