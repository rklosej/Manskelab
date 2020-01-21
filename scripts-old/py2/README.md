# manskelab-py2
A collection of software to manipulate medical image files. All scripts/files in this directory require Python 2.

**The scripts in this directory are no longer updated and will eventually be integrated into the Python 3 scripts in Manskelab/scripts.**

Included file conversions:
- .AIM to .NIfTI
- .AIM to .MHA
- .AIM to .MHD/.RAW
- .NII to MHA
- .NII to MHD/.RAW
- DICOM image series to .NII
- DICOM image series to .MHA
- DICOM image series to .MHD/.RAW


## Requirements
- Python version 2.7
- vtkbone
- Anaconda 


## Anaconda Environment Setup
The software in this directory require Python 2.7 (or later, but not Python 3!) and Anaconda.

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

1. Activate the environment with the following command:
```
conda activate manskelab-py2
```

2. Run any script in this repository as follows:
```
python <PATH_TO_MANSKELAB_PYTHON_SCRIPT> <INPUT_PARAMETERS>
```

