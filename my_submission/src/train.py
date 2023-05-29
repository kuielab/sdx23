import argparse
import yaml
from ml_collections import ConfigDict
import os
import random
import numpy as np
from tqdm import tqdm
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.optim import Adam, RMSprop, AdamW
from torch.utils.data import DataLoader
from torch.cuda.amp.grad_scaler import GradScaler

from utils import manual_seed
from tfc_tdf_v3 import TFC_TDF_net, STFT
from dataset import MSSDatasets

import warnings
warnings.filterwarnings("ignore")



def train():
    parser = argparse.ArgumentParser()    
    parser.add_argument("--seed", type=int, default=0, help="random seed")
    parser.add_argument("--device_ids", nargs='+', type=int, default=0, help='list of gpu ids')
    parser.add_argument("--model_path", type=str, help="path to model checkpoint folder (containing config.yaml)")
    parser.add_argument("--data_root", type=str, help="path to folder containing all training datasets")    
    parser.add_argument("--num_workers", type=int, default=0, help="dataloader num_workers")
    parser.add_argument("--pin_memory", type=bool, default=False, help="dataloader pin_memory")     
    parser.add_argument("--num_steps", type=int, default=0, help="total number of training steps")
    args = parser.parse_args()
    
    manual_seed(args.seed)
    torch.backends.cudnn.benchmark = True
    
    with open(args.model_path+'/config.yaml') as f:
        config = ConfigDict(yaml.load(f, Loader=yaml.FullLoader))
    config.training.num_steps = args.num_steps
    
    trainset = MSSDatasets(config, args.data_root)
    
    train_loader = DataLoader(
        trainset, 
        batch_size=config.training.batch_size, 
        shuffle=True, 
        num_workers=args.num_workers, 
        pin_memory=args.pin_memory
    )

    model = TFC_TDF_net(config)
    model.train()
    
    device_ids = args.device_ids
    if type(device_ids)==int:
        device = torch.device(f'cuda:{device_ids}')
        model = model.to(device)
    else:
        device = torch.device(f'cuda:{device_ids[0]}')
        model = nn.DataParallel(model, device_ids=device_ids).to(device)

    optimizer = Adam(model.parameters(), lr=config.training.lr)
    
    print('Train Loop')
    scaler = GradScaler()    
    for batch in tqdm(train_loader):   

        y = batch.to(device)
        x = y.sum(1)  # mixture   
        if config.training.target_instrument is not None:
            i = config.training.instruments.index(config.training.target_instrument)
            y = y[:,i]
        with torch.cuda.amp.autocast():        
            y_ = model(x)   
            loss = nn.MSELoss()(y_, y) 

        scaler.scale(loss).backward()
        if config.training.grad_clip:
            nn.utils.clip_grad_norm_(model.parameters(), config.training.grad_clip)  
        scaler.step(optimizer)
        scaler.update()
        optimizer.zero_grad(set_to_none=True)
    
    
    state_dict = model.state_dict() if type(device_ids)==int else model.module.state_dict()
    
    torch.save(state_dict, args.model_path+'/ckpt')
               

if __name__ == "__main__":
    train()
