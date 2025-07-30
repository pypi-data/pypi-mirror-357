# Full-DIA

Full-DIA is a partially open-source, free-to-use Python software that provides comprehensive peptide/protein identification and accurate quantification results for diaPASEF data.

---
### Contents
**[Installation](#installation)**<br>
**[Usage](#usage)**<br>
**[Output](#output)**<br>

---
### Installation

We recommend using [Conda](https://www.anaconda.com/) to create a Python environment for using Full-DIA, whether on Windows or Linux.

1. Create a Python environment with version 3.9.18.
    ```bash
    conda create -n full_env python=3.9.18 "numpy<2.0.0"
    conda activate full_env
    ```

2. Install the corresponding PyTorch and CuPy packages based on your CUDA version (which can be checked using the `nvidia-smi` command). Full-DIA requires GPUs with over 10 GB of VRAM to run.
  - CUDA-12
    ```bash
    pip install torch==2.3.1 --index-url https://download.pytorch.org/whl/cu121
    pip install cupy-cuda12x==13.3
    conda install cudatoolkit
    ```
  - CUDA-11
    ```bash
    pip install torch==2.3.1 --index-url https://download.pytorch.org/whl/cu118
    pip install cupy-cuda11x==13.3
    conda install cudatoolkit
    ```

3. Install Full-DIA
    ```bash
    pip install full_dia
    ```
   
---
### Usage
```bash
full_dia -lib "Absolute path of the spectral library" -ws "Absolute path of the .d folder or a folder containing multiple .d folders"
```
(Please note that the path needs to be enclosed in quotes if running on a Windows platform.)

- `-lib`<br>
This parameter is used to specify the absolute path of the spectral library.
Full-DIA currently supports the spectral library with the suffix .speclib predicted by DIA-NN (v1.9 and v1.9.1) or .parquet produced by DIA-NN (>= v1.9). 
It supports oxygen modifications on methionine (M) but does not include modifications such as phosphorylation or acetylation. 
Refer to [this](https://github.com/vdemichev/DiaNN) for instructions on how to generate prediction spectral libraries using DIA-NN. 
Full-DIA will develop its own predictor capable of forecasting the peptide retention time, ion mobility, and fragmentation pattern. 
It may also be compatible with other formats of spectral libraries based on requests.

- `-ws`<br>
This parameter is used to specify the .d folder or the folder containing multiple .d folders that need to be analyzed.

Other optional params are list below by entering `full_dia -h`:
```
       ******************
       * Full-DIA x.y.z *
       ******************
Usage: full_dia -ws WS -lib LIB

optional arguments for users:
  -h, --help           Show this help message and exit.
  -ws WS               Specify the folder that is .d or contains .d files.
  -lib LIB             Specify the absolute path of a .speclib or .parquet spectra library.
  -out_name OUT_NAME   Specify the folder name of outputs. Default: full_dia.
  -gpu_id GPU_ID       Specify the GPU-ID (e.g. 0, 1, 2) which will be used. Default: 0.
```