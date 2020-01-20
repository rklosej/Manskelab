# manskelab/setup
Instructions to setup anaconda environment and run scripts.

## Anaconda Environment Setup
The software in this directory require Python 3.6 and Anaconda. Python 3.7.x is currently not supported by all packages.

To setup a new environment with all packages needed for the software in this directory, run the command:
```
conda env create -f environment.yml
```

Note that the above command only needs to be run ONCE when you first download this repository.

## Issues Installing the Anaconda Environment
If you have a newer version of Anaconda, you may receive errors (e.g. "Solving environment: failed") when attempting to setup the Anaconda environment shown above. Follow these steps to resolve the errors:

1. Downgrade conda:

```
conda config --set allow_conda_downgrades true
conda install conda=4.6.11
```

2. Install the environment:
```
conda env create -f environment.yml
```

## Running a Script
To run any script in this repository, follow the steps below:

**ON WINDOWS:**
1. Activate the environment with the following command:
```
conda activate manskelab
```

2. Run any script in this repository as follows:
```
python <PATH_TO_MANSKELAB_PYTHON_SCRIPT> <INPUT_PARAMETERS>
```


**ON MAC:**
1. Activate the environment with the following command:
```
source activate manskelab
```

2. Run any script in this repository as follows:
```
python <PATH_TO_MANSKELAB_PYTHON_SCRIPT> <INPUT_PARAMETERS>
```
