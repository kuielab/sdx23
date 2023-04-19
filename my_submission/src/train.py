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
from ema import EMAHelper
from dataset import DNRDataset

import warnings
warnings.filterwarnings("ignore")



def train():
    parser = argparse.ArgumentParser()    
    parser.add_argument("--seed", type=int, default=0, help="random seed")
    parser.add_argument("--device_ids", nargs='+', type=int, default=0, help='list of gpu ids')
    parser.add_argument("--model_path", type=str, help="path to model checkpoint folder (containing config.yaml)")
    parser.add_argument("--data_path", type=str, help="dataset path")    
    parser.add_argument("--num_workers", type=int, default=0, help="dataloader num_workers")
    parser.add_argument("--pin_memory", type=bool, default=False, help="dataloader pin_memory")         
    args = parser.parse_args()
    
    manual_seed(args.seed)
    torch.backends.cudnn.benchmark = True
    
    with open(args.model_path+'/config.yaml') as f:
        config = ConfigDict(yaml.load(f, Loader=yaml.FullLoader))
    
    trainset = DNRDataset(config, args.data_path)
    
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

    ema_helper = EMAHelper(mu=config.training.ema_momentum)
    ema_helper.register(model)
    
    print('Train Loop')
    scaler = GradScaler()  
    for batch in tqdm(train_loader):   

        y = batch.to(device)
        x = y.sum(1)  # mixture   

        with torch.cuda.amp.autocast():        
            y_ = model(x)   
            loss = nn.MSELoss()(y_, y)

        scaler.scale(loss).backward()
        if config.training.grad_clip:
            nn.utils.clip_grad_norm_(model.parameters(), config.training.grad_clip)  
        scaler.step(optimizer)
        scaler.update()
        optimizer.zero_grad(set_to_none=True)

        ema_helper.update(model)
        
    torch.save(ema_helper.state_dict(), 
               args.model_path+f'/step{config.training.num_steps}_seed{args.seed}.ckpt')


if __name__ == "__main__":
    train()
