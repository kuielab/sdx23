### Setup environment

```bash
conda env create -n mdx-net pip
conda activate mdx-net
pip install -r requirements.txt
```
### Training
- Run train.py **3 times** with different seeds (one of 0,1,2)
	- Leaderboard A
	    ```bash
	    python train.py --data_path path/to/labelnoise/dataset --model_path ../ckpts/modelA --device_ids 0 --seed 0
	    ```
	- Leaderboard B
	    ```bash
	    python train.py --data_path path/to/bleeding/dataset --model_path ../ckpts/modelB --device_ids 0 --seed 0
	    ```
	    - for multi-gpu
	        ```bash
	        --device_ids 0 1 2 3
	        ```
- You will need at least 22GB of GPU memory (we used one RTX3090)
