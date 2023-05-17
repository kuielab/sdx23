

# Submission

## Submission Summary

* CDX Leaderboard A
	* Submission ID: 216962
	* Submitter: kim_min_seok
	* Final rank: 5th place
	* Final scores:
	  |  Mean SDR | SDR Dialog | SDR Effect | SDR Music | 
	  | :------: | :------: | :-------: | :-------: | 
	  |   3.787   |   7.870   |   1.286   |   2.204    |    
      

## Model Summary

* Data
	* DnR train split
	* Augmentation
		* Random chunking and mixing sources from different tracks ([1])
		* Mimic stereo tracks with mono tracks
            * When training, place two different chunks of the same track at left and right channels         
* Model
	* A 'multi-source' version of TFC-TDF U-Net[2, 3] with some architectural improvements, including Channel-wise Subband[4]
	* Final submission is an ensemble of 3 models with identical architecture and training procedure but with different random seeds

[1] S. Uhlich, et al., "Improving music source separation based on deep neural networks through data augmentation and network blending", ICASSP 2017.

[2] W. Choi, et al. "Investigating u-nets with various intermediate blocks for spectrogram-based singing voice separation", ISMIR 2020.

[3] M. Kim, et al. "Kuielab-mdx-net: A two-stream neural network for music demixing", MDX Workshop at ISMIR 2021.

[4] H. Liu, et al. "Channel-wise Subband Input for Better Voice and Accompaniment Separation on High Resolution Music", INTERSPEECH 2020.



# Reproduction

Download [cdx_A.zip](https://drive.google.com/file/d/1na3_3MISLGDg-7EjImU94yVgPxnPOfPv/view?usp=sharing), which contains 
  * pretrained model checkpoints 
  * config.yaml files (configurations for training and inference)

## How to reproduce the submission
1. Create a 'ckpts' folder under [my_submission](my_submission). Unzip the downloaded zip file to 'my_submission/ckpts'.
2. Copy [my_submission](my_submission) and [requirements.txt](requirements.txt) to your [SDX 2023 Music Demixing Track Starter Kit](https://gitlab.aicrowd.com/aicrowd/challenges/sound-demixing-challenge-2023/sdx-2023-music-demixing-track-starter-kit/).
3. Run submit.sh

## How to reproduce the training
- All code needed to reproduce training is in [my_submission/src](my_submission/src)
- See [HOW_TO_TRAIN.md](my_submission/src/HOW_TO_TRAIN.md)
