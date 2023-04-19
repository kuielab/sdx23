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


def masked_loss(y_, y, q, coarse=True):
    loss = torch.nn.MSELoss(reduction='none')(y_, y).transpose(0,1)   # shape = [num_sources, batch_size, num_channels, chunk_size]
    if coarse:
        loss = torch.mean(loss, dim=(-1,-2))
    loss = loss.reshape(loss.shape[0], -1)
    L = loss.detach()
    quantile = torch.quantile(L, q, interpolation='linear', dim=1, keepdim=True)
    mask = L < quantile 
    return (loss * mask).mean()

