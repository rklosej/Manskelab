# File Conversion
A collection of software to convert file types.

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


## Python Environment Setup
The software in this directory require Python 3.4 or later and Anaconda.

To setup a new environment with all packages needed for the software in this directory, run the command:
```
conda env create -f environment.yml
```

Note that the above command only needs to be run ONCE when you first download this repository.


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

