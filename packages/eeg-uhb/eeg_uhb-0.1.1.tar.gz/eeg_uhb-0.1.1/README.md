# EEG_UHB

Library for Electroencephalography (EEG) signal acquisition and processing using Unicorn Hybrid Black (UHB) commercial equipment using Lab Streaming Layer (LSL).

## Install

You can install the library directly from PyPI using pip:

```bash
pip install eeg-uhb
```

## Installation from GitHub (optional)

If you want to install the latest version directly from the repository, run:

```bash
pip install git+https://github.com/IngAmaury/EEG_UHB_LIBRARY.git
```

### Installation in a Python virtual environment

1. Open a terminal or Anaconda Prompt.
2. Create a new virtual environment (for example: myenv):
```bash
python -m venv myenv
```
   - Using Anaconda Prompt:
    ```bash
    conda create --name myenv python=3.8
    ```
3. Enable the virtual environment:
    - Windows:
    ```bash
    myenv\Scripts\activate
    ```
    - Anaconda Prompt:
    ```bash
    conda activate myenv
    ```
    - macOS/Linux::
    ```bash
    source myenv/bin/activate
    ```
4. Install the library inside the virtual environment:
```bash
(myenv) pip install eeg-uhb
```

> [!NOTE]
> It is recommended to install in a virtual environment to avoid conflicts with other system libraries.

## Dependencies

The library requires the following dependencies, which will be installed automatically with pip:
- numpy
- pylsl
- scipy
- scikit-fuzzy

## Use

```python
from eeg_uhb import EEGAcquisitionManager
import time

if __name__=='__main__':
    EEG = EEGAcquisitionManager()
    start_time = time.time()
    duration = 0.04  # segundos
    
    # the stream_name depends on the one you choose
    EEG.start_acquisition(stream_name='UN-2023.07.40')
    start = time.sleep(duration)
    print(EEG.data)
    print(f'Length: {len(EEG.data)}')
    EEG.stop_acquisition()
```

## License

This project is licensed under the Creative Commons Attribution-NonCommercial 4.0 International License.  
See the LICENSE file for details.

