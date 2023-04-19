
# Submission

## Submission Summary

* MDX Leaderboard C
	* Submission ID: 000000
	* Submitter: kim_min_seok
	* Final rank: 
	* Final scores:
	  |  SDR_song | SDR_bass | SDR_drums | SDR_other | SDR_vocals |
	  | :------: | :------: | :-------: | :-------: | :--------: |
	  |   0.00   |   0.00   |   0.00   |   0.00    |    0.00    |

## Model Summary

* Data
  * All 150 tracks of MusdbHQ
  * Augmentation
    * Random chunking and mixing sources from different tracks ([1])
    * Pitch shift and time stretch ([2])
* Model
  * Ensemble of 5 models
	  * 2 x Hybrid Demucs[3, 4] 
		  * we used the pretrained weights (htdemucs_ft, hdemucs_mmi) from [github.com/facebookresearch/demucs](https://github.com/facebookresearch/demucs)
	  * 3 x TFC-TDF U-Net[5, 6]
		  * 'multi-source' version with some architectural improvements, including Channel-wise Subband[7]

[1] S. Uhlich et al., "Improving music source separation based on deep neural networks through data augmentation and network blending", ICASSP 2017.

[2] Cohen-Hadria, Alice, et al. "Improving singing voice separation using Deep U-Net and Wave-U-Net with data augmentation", EUSIPCO 2019.

[3] Defossez, Alexandre, "Hybrid Spectrogram and Waveform Source Separation", MDX Workshop at ISMIR 2021.

[4] Rouard, Simon, et al. "Hybrid Transformers for Music Source Separation". 

[5] Choi, Woosung, et al. "Investigating u-nets with various intermediate blocks for spectrogram-based singing voice separation", ISMIR 2020.

[6] Kim, Minseok, et al. “Kuielab-mdx-net: A two-stream neural network for music demixing”, MDX Workshop at ISMIR 2021.

[7] Liu, Haohe, et al. "Channel-wise Subband Input for Better Voice and Accompaniment Separation on High Resolution Music", INTERSPEECH 2020.
