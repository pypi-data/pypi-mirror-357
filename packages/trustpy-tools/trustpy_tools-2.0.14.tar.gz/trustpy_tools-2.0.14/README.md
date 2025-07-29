<div align="center">
  <img src="https://raw.githubusercontent.com/yaniker/TrustPy/main/assets/logo.jpeg" alt="TrustPy logo" width="300">

  <br>

  <a href="https://deepwiki.com/yaniker/TrustPy">
    <img src="https://deepwiki.com/badge.svg" alt="Ask DeepWiki">
  </a>
  <img src="https://static.pepy.tech/badge/trustpy-tools" alt="Downloads">
  <a href="https://anaconda.org/conda-forge/trustpy-tools">
    <img src="https://img.shields.io/conda/vn/conda-forge/trustpy-tools.svg" alt="Conda-Forge">
  </a>

  <br>

  <img src="https://img.shields.io/pypi/v/trustpy-tools" alt="PyPI">
  <img src="https://img.shields.io/pypi/l/trustpy-tools" alt="License">
  <img src="https://img.shields.io/pypi/pyversions/trustpy-tools" alt="Python">
</div>

 
# TrustPy - Trustworthiness Python

TrustPy is a lightweight, framework-agnostic Python library for assessing the reliability, calibration, and uncertainty of predictive models across the AI/ML lifecycle.
Designed with MLOps, model validation, and governance in mind, it enables teams to quantify trust before production rollout—ensuring models behave as expected under real-world conditions.

🔧 Works out-of-the-box with any ML framework
📦 Released on Conda-Forge and PyPI
🔁 Maintained with full CI/CD support and test coverage

###
**The implementation is flexible and works out-the-box with any AI/ML library.**
###

## Installation
### Recommended 1: Install via Conda-Forge
The easiest way to install trustpy-tools is via Conda-Forge, which handles all dependencies automatically. Run the following command:
```bash
conda install -c conda-forge trustpy-tools
```

### Recommended 2: Install via PyPI (pip install)
If you prefer using pip (PyPI), you can install directly:
```bash
pip install trustpy-tools
```

### Alternative: Manual Installation
If you prefer to install the package manually or are not using Conda, you can install the required dependencies and clone the repository.

Install Dependencies
- **NumPy**: For numerical calculations.
- **Matplotlib**: For plotting the trust spectrum.
- **Scikit-learn**: For Kernel Density Estimation (KDE) in trust density estimation.

Install them via conda:

```bash
conda install numpy matplotlib scikit-learn
```

or

Install them via pip:

```bash
pip install numpy matplotlib scikit-learn
```

Clone the Repository
```bash
git clone https://github.com/yaniker/TrustPy.git
cd TrustPy
```

You can verify installation by running:
```bash
python -c "from trustpy import NTS, CNTS; print('TrustPy is ready.')"
```

## Example Usage 
```python
from trustpy import NTS, CNTS #This is how the package is imported.
import numpy as np

# Example oracle and predictions
oracle = np.array([0, 0, 1, 2, 2, 0, 1])  # True labels
predictions = np.array([
    [0.8, 0.1, 0.1],  # Correct, high confidence
    [1.0, 0.0, 0.0],  # Correct, high confidence
    [0.2, 0.7, 0.1],  # Correct, high confidence
    [0.1, 0.2, 0.7],  # Correct, high confidence
    [0.1, 0.4, 0.5],  # Correct, lower confidence
    [0.1, 0.8, 0.1],  # Incorrect, high confidence
    [0.3, 0.3, 0.4]   # Incorrect, low confidence
]
) #Replace this with your model's predictions (`predictions = model.predict()`)

# FOR NETTRUSTSCORE #
# Initialize with default parameters
nts = NTS(oracle, predictions, show_summary=True, export_summary=True, trust_spectrum=True)
nts_scores_dict = nts.compute() # Computes trustworthiness for each class and overall.

# FOR CONDITIONAL NETTRUSTSCORE #
# Initialize with default parameters
cnts = CNTS(oracle, predictions, show_summary=True, export_summary=True, trust_spectrum=True)
cnts_scores_dict = cnts.compute() # Computes trustworthiness for each class and overall.

# Sets show_summary=True to print the results table.
# Sets export_summary=True to save the results.
# Sets trust_spectrum=True to generate plots.
# By default, results are saved to:
# - trustpy/nts/ (for NTS)
# - trustpy/cnts/ (for CNTS)
# You can override this using `output_dir=your_path`

```

Example Plot for Trust Spectrum (`trust_spectrum = True`)
![Alt text](./assets/trust_spectrum.png)

Example Plot for Conditional Trust Spectrum (`trust_spectrum = True`)
![Alt text](./assets/conditional_trust_densities.png)

I shared the codes for the plots [Python scripts for plots](./assets/plots.py) for users to modify as needed.

## Command Line Interface (CLI)
You can run TrustPy directly from the command line after installation. You can also optionally specify a custom output directory. Example:
```bash
python -m trustpy --oracle oracle.npy --pred preds.npy --mode cnts --trust_spectrum --output_dir ./my_results
```

For this you will need your actual/predicted results in `oracle.npy` and `preds.npy` format. You can generate test samples via:
```bash
import numpy as np

oracle = np.array([0, 2, 1, 0, 1])
np.save("oracle.npy", oracle)

predictions = np.array([
    [0.8, 0.1, 0.1],  # correct
    [0.0, 0.0, 1.0],  # correct
    [0.2, 0.7, 0.1],  # correct
    [0.1, 0.8, 0.1],  # wrong
    [0.3, 0.3, 0.4],  # wrong
])
np.save("preds.npy", predictions)
```

## Post Installation Testing
You can run this single command to verify that TrustPy runs correctly and can generate trust spectrum plots:  
For NTS:  
```bash
python -c "from trustpy import NTS; import numpy as np; NTS(np.array([0,1,1,0]), np.array([[0.8,0.2],[0.2,0.8],[0.4,0.6],[0.9,0.1]]), trust_spectrum=True, show_summary=False).compute()"
```

For CNTS:  
```bash
python -c "from trustpy import CNTS; import numpy as np; CNTS(np.array([0,1,1,0]), np.array([[0.8,0.2],[0.2,0.8],[0.4,0.6],[0.9,0.1]]), trust_spectrum=True, show_summary=False).compute()"
```

This will generate a test plot and save it to the default output directory:
```bash
./trustpy/nts/trust_spectrum.png
./trustpy/cnts/conditional_trust_densities.png
```


## Unit Testing
All unit tests were run using `pytest` with full coverage prior to release to ensure reliability and correctness.

After installation, you can run all tests to verify everything is working:

```bash
python -m pytest tests/
```

Make sure to install pytest first.
```bash
pip install pytest
```

## Licence
This project is licensed under the MIT License. See [LICENSE](./LICENSE) for details.

## Citations
For scholarly references and the origins of the techniques used in this package, please refer to the [CITATION](./CITATION.cff) file.
