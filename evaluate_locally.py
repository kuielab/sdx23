import os
from tqdm.auto import tqdm
import numpy as np
import soundfile
from my_submission.aicrowd_wrapper import AIcrowdWrapper
from glob import glob

import warnings
warnings.filterwarnings("ignore")


def check_data(datafolder):
    """
    Checks if the data is downloaded and placed correctly
    """
    inputsfolder = datafolder
    groundtruthfolder = datafolder
    dl_text = ("Please download the public data from"
               "\n https://www.aicrowd.com/challenges/music-demixing-challenge-2023/problems/robust-music-separation/dataset_files"
               "\n And unzip it with ==> unzip <zip_name> -d public_dataset")
    if not os.path.exists(datafolder):
        raise NameError(f'No folder named {datafolder} \n {dl_text}')
    if not os.path.exists(groundtruthfolder):
        raise NameError(f'No folder named {groundtruthfolder} \n {dl_text}')

def evaluate(LocalEvalConfig):
    """
    Runs local evaluation for the model
    Final evaluation code is the same as the evaluator
    """
    datafolder = LocalEvalConfig.DATA_FOLDER
    
    check_data(datafolder)
    inputsfolder = datafolder
    groundtruthfolder = datafolder

    preds_folder = LocalEvalConfig.OUTPUTS_FOLDER

    model = AIcrowdWrapper(predictions_dir=preds_folder, dataset_dir=datafolder)
    
    folder_names = sorted(os.listdir(datafolder))
    folder_names = list(filter(lambda x: x[0]!='.' and os.path.isdir(datafolder+x), folder_names))
    
    all_metrics = {}
    for fname in tqdm(folder_names, desc="Demixing"):       
        print(fname)
        model.separate_music_file(fname)


if __name__ == "__main__":
    
    # change the local config as needed
    class LocalEvalConfig:
        DATA_FOLDER = '/home/ielab/demix/data/musdbHQ/test/'
        OUTPUTS_FOLDER = './my_submission/outputs/'

    outfolder=  LocalEvalConfig.OUTPUTS_FOLDER
    if not os.path.exists(outfolder):
        os.mkdir(outfolder)
    
    evaluate(LocalEvalConfig)
