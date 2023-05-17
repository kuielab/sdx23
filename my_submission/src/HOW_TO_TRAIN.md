### Setup environment

```bash
conda create -n cdx-net pip
conda activate cdx-net
pip install -r requirements.txt
```
### Training
- Run train.py **3 times** with different seeds (one of 0,1,2)
    ```bash
    python train.py --data_path path/to/dnr/train/split --model_path ../ckpts/tfc_tdf --device_ids 0 --seed 0 
    ```
    - for multi-gpu
        ```bash
        --device_ids 0 1 2 3
        ```
