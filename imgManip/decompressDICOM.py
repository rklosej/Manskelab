# coding=utf-8
#----------------------------------------------------- 
# decompressDICOM.py
#
# Created by:   Michael Kuczynski
# Created on:   2019.07.07
#
# Description: Decompresses DICOM images.
#----------------------------------------------------- 
#
# Requirements:
#   -Python 3.4 or later
#   -gdcm, pydicom
#
# Usage:
#   decompressDICOM.py <COMPRESSED_DICOM_FOLDER>
#
# Notes:
#   -The decompressed DICOM directory it will be created automatically
#    in the compressed DICOM folder and will be named: decompressedDICOMs
#----------------------------------------------------- 

import pydicom
import os
import sys
import errno

inputPath = sys.argv[1]

# Check if the provided directory exists
if not os.path.exists(inputPath):
    print ("Error: provided directory does not exist!")
    sys.exit(1)

# Get the absolute path of the directory provided
inputPathAbs = os.path.abspath(inputPath)
outputPathAbs = inputPathAbs + "/decompressedDICOMs"

# Create the directory for decompressed DICOMs inside the compressed DICOM folder
try:
    os.mkdir(outputPathAbs)
except OSError as e:
    if e.errno != errno.EEXIST:     # Directory already exists error
        raise

# Loop through all DICOMs in the provided directory, rename and decompress
for file in os.listdir(inputPathAbs):
    filename = os.fsdecode(file)
    
    currentFilePath = os.path.join(inputPathAbs, filename)

    # TO-DO:
    # Check transfer syntax tag in DICOM header to see if file is compressed or not
    # If the file is already decompressed, skip it

    # Check if we have a file
    if os.path.isfile(currentFilePath):

        # Rename the DICOM file to include a file extension (if needed)
        if "." not in filename:
            outputFilePath = os.path.join(outputPathAbs, filename + ".dcm")

            print ("Decompressing file: " + filename)

            ds = pydicom.dcmread(currentFilePath)
            ds.decompress()

            # Save the decompressed file
            try:
                ds.save_as(outputFilePath)
            except OSError as e:
                if e.errno != errno.ENOENT:     # No such file or directory error
                    print ("ERROR: No such file or directory named " + outputFilePath)
                    raise

        # For cases when we have compressed DICOMs with file extensions
        elif ".dcm" in filename:
            outputFilePath = os.path.join(outputPathAbs, filename)

            print ("Decompressing file: " + filename)

            ds = pydicom.dcmread(currentFilePath)
            ds.decompress()

            # Save the decompressed file
            try:
                ds.save_as(outputFilePath)
            except OSError as e:
                if e.errno != errno.ENOENT:     # No such file or directory error
                    print ("ERROR: No such file or directory named " + outputFilePath)
                    raise

print ("Done!")
