# Submission

## Submission Summary

* MDX Leaderboard A
	* Submission ID: 216209
	* Submitter: kim_min_seok
	* Final rank: 3rd place
	* Final scores:
	  |  SDR_song | SDR_bass | SDR_drums | SDR_other | SDR_vocals |
	  | :------: | :------: | :-------: | :-------: | :--------: |
	  |   6.513   |  6.707   |  6.712    |  4.816    |   7.816    |
	  	  
* MDX Leaderboard B
	* Submission ID: 216211
	* Submitter: kim_min_seok
	* Final rank: 1st place
	* Final scores:
	  |  SDR_song | SDR_bass | SDR_drums | SDR_other | SDR_vocals |
	  | :------: | :------: | :-------: | :-------: | :--------: |
	  |   6.581   |  6.975   |  6.646    |  4.962    |   7.741    |

## Model Summary

* Data
  * All 203 tracks of the Moises dataset was used for training (no validation split)
  * Augmentation
    * Random chunking and mixing sources from different tracks ([1])
* Model
  * A 'multi-source' version of TFC-TDF U-Net[2, 3] with some architectural improvements, including Channel-wise Subband[4]
  * Final submission is an ensemble of 3 models with identical architecture and training procedure but with different random seeds 
* Noise-robust Training
  * Leaderboard A: Loss masking
      * Intuitively, data with high training loss is likely to be audio chunks with labelnoise
	  * For each training batch, discard (=don't use for weight update) batch elements with higher loss than some quantile 
		  * ex) only use half of the training batch for each weight update
  * Leaderboard B: Loss masking (along temporal dimension)
      * Compared to labelnoise, data with bleeding seemed to vary less in terms of the amount of noise
      * A more fine-grained masking method performed better (discarding temporal bins with high loss) 

[1] S. Uhlich, et al., "Improving music source separation based on deep neural networks through data augmentation and network blending", ICASSP 2017.

[2] W. Choi, et al. "Investigating u-nets with various intermediate blocks for spectrogram-based singing voice separation", ISMIR 2020.

[3] M. Kim, et al. “Kuielab-mdx-net: A two-stream neural network for music demixing”, MDX Workshop at ISMIR 2021.

[4] H. Liu, et al. "Channel-wise Subband Input for Better Voice and Accompaniment Separation on High Resolution Music", INTERSPEECH 2020.


# Reproduction

## How to reproduce the submission
1. Download [mdx_AB.zip](https://drive.google.com/file/d/1fy3aIAYnDg8WJ35hMsBhVJFLbIbLo8Gv/view?usp=share_link), which contains all pretrained model checkpoints and config.yaml files needed for submission.
2. Create a 'ckpts' folder under [my_submission](my_submission). Unzip the downloaded zip file to 'my_submission/ckpts'.
3. Copy [my_submission](my_submission) and [requirements.txt](requirements.txt) to your [SDX 2023 Music Demixing Track Starter Kit](https://gitlab.aicrowd.com/aicrowd/challenges/sound-demixing-challenge-2023/sdx-2023-music-demixing-track-starter-kit/).
4. Run submit.sh after configuring [my_submission/user_config.py](my_submission/user_config.py)
	- for Leaderboard A, set ```MySeparationModel = A```
	- for Leaderboard B, set ```MySeparationModel = B```

## How to reproduce the training
- All code needed to reproduce training is in [my_submission/src](my_submission/src)
- See [HOW_TO_TRAIN.md](my_submission/src/HOW_TO_TRAIN.md)
