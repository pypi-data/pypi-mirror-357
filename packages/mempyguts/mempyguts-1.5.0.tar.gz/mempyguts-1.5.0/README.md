# memPyGUTS

memPyGUTS is a python package for fitting GUTS models to survival data, from ecotoxicology experiments, developed at the Osnabrück University, Germany

## Description
The small package is currently capable of calibrating various General Unified Threshold model of Survival (GUTS,[1]) models to exposure-survival datasets using a frequentist Nelder-Mead approach. Uncertainties can be additionally assessed using a Bayesian Monte-Carlo-Marrcov-Chain method (MCMC). It is based on the epytox package by Raymond Nepstad (github.com/nepstad/epytox).
Additional models for GUTS mixture toxicity [2] and BufferGUTS models [3] for above-ground invertebrates are also implemented.

## Installation

### Prerequisites

+ git https://git-scm.com/downloads
+ conda (miniconda3 recommended) https://docs.anaconda.com/miniconda/install/


Clone the repository and change into the directory:
```bash
git clone https://gitlab.uni-osnabrueck.de/memuos/mempyguts.git
cd mempyguts
```

Create a conda environment with Python 3.11 and activate:
```bash
conda create -n mempyguts -c conda-forge python=3.11 pandoc
conda activate mempyguts
```

Install the package into the activated environment with the package installer 
for python (pip) as an editable installation
```bash
pip install -e .[pymob]
```


## Usage

For usage of mempyguts, see the Jupyter notebook: notebooks/demo.ipynb 

## References
[1] Jager, T., Albert, C., Preuss, T. G., & Ashauer, R. (2011). General
        unified threshold model of survival - A toxicokinetic-toxicodynamic
        framework for ecotoxicology. Environmental Science and Technology, 45(7),
        2529–2540. 

[2] Bart, S., Jager, T., Robinson, A., Lahive, E., Spurgeon, D. J., & Ashauer, R. (2021). Predicting Mixture Effects over Time with Toxicokinetic–Toxicodynamic Models (GUTS): Assumptions, Experimental Testing, and Predictive Power. Environmental Science & Technology, 55(4), 2430–2439. https://doi.org/10.1021/acs.est.0c05282

[3] Bürger, L. U., & Focks, A. (2025). From water to land—Usage of Generalized Unified Threshold models of Survival (GUTS) in an above-ground terrestrial context exemplified by honeybee survival data. Environmental Toxicology and Chemistry, 44(2), 589–598. https://doi.org/10.1093/etojnl/vgae058


