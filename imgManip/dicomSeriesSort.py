# coding=utf-8
#----------------------------------------------------- 
# dicomSeriesSort.py
#
# Created by:   Michael Kuczynski
# Created on:   2019.08.09
#
# Description: Sorts all DICOMs in the provided directory into 
#              subdirectories based on the series description tag.
#----------------------------------------------------- 
#
# Requirements:
#   -Python 3.4 or later
#   -pydicom, GDCM, argparse, errno
#
# Notes:
#   -The newly created subdirectories are named based on the series description tag
#   -These new directories are placed in the same directory that is provided
#   -The DICOMs in the provided directory are not modified in any way, just copied
#
# Usage:
#   dicomSeriesSort.py DICOM_FOLDER
#----------------------------------------------------- 

import os
import sys
import gdcm
import errno
import pydicom
import argparse

from pydicom.errors import InvalidDicomError

# Just for fun :)
# Print iterations progress
def print_progress(iteration, total, prefix='', suffix='', decimals=1, bar_length=100):
    #
    # Call in a loop to create terminal progress bar
    # @params:
    #     iteration   - Required  : current iteration (Int)
    #     total       - Required  : total iterations (Int)
    #     prefix      - Optional  : prefix string (Str)
    #     suffix      - Optional  : suffix string (Str)
    #     decimals    - Optional  : positive number of decimals in percent complete (Int)
    #     bar_length  - Optional  : character length of bar (Int)
    #
    str_format = "{0:." + str(decimals) + "f}"
    percents = str_format.format(100 * (iteration / float(total)))
    filled_length = int(round(bar_length * iteration / float(total)))
    bar = '█' * filled_length + '-' * (bar_length - filled_length)

    sys.stdout.write('\r%s |%s| %s%s %s' % (prefix, bar, percents, '%', suffix)),

    if iteration == total:
        sys.stdout.write('\n')
    sys.stdout.flush()

# Parse input arguements
parser = argparse.ArgumentParser()
parser.add_argument("inputDirectory", type=str, help="The input DICOM directory (compressed files)")
args = parser.parse_args()

inputPath = args.inputDirectory

# Check if the provided directory exists
if not os.path.exists(inputPath):
    print ("Error: provided directory does not exist!")
    sys.exit(1)

# Get the absolute path of the directory provided. Use os.path.join() to avoid slash direction issues between Mac, Linux, and Windows
inputPathAbs = os.path.abspath(inputPath)

# Get the number of files in a directory for the progress bar
l = len( [ name for name in os.listdir(inputPathAbs) if os.path.isfile( os.path.join(inputPathAbs, name) ) ] )

# Counter for the progress bar
i = 0

# Loop through all DICOMs in the provided directory, rename, decompress, and copy to the appropriate directory
for file in os.listdir(inputPathAbs):
    filename = os.fsdecode(file)

    currentFilePath = os.path.join(inputPathAbs, filename)

    # Check if we have a file
    if os.path.isfile(currentFilePath):

        # Read the DICOM file. Make sure we have a valid DICOM file...
        try:
            dicom = pydicom.dcmread(currentFilePath)
        except InvalidDicomError:
            continue

        # Check transfer syntax tag in DICOM header to see if file is compressed or not
        # If the file is already decompressed, skip it
        tsUID = dicom.file_meta.TransferSyntaxUID

        # Get the file's tag and parse out the series description
        # Series description is located at [0x0008, 0x103e]
        # Use the instance number located at [0x0020, 0x0013] to rename the images
        seriesDescription = str(dicom[0x0008, 0x103e].value).upper()
        instanceNumber = dicom[0x0020, 0x0013].value

        # Make the instance number have the same number of digits for all images
        instanceNumberString = str(instanceNumber).rjust(4, '0')
        
        seriesFilePath = os.path.join(inputPathAbs, seriesDescription)
        newFileName = "IM_" + instanceNumberString + ".dcm"

        # Uncompressed Implicit VR Little-endian = 1.2.840.10008.1.2
        # Uncompressed Explicit VR Little-endian = 1.2.840.10008.1.2.1
        # Uncompressed Explicit VR Big-endian = 1.2.840.10008.1.2.2
        if not ( (tsUID == "1.2.840.10008.1.2") or (tsUID == "1.2.840.10008.1.2.1") or (tsUID == "1.2.840.10008.1.2.2") ):
            dicom.decompress()

        # If the series description directory doesn't already exist, create one
        if not os.path.exists(seriesFilePath):
            os.makedirs(seriesFilePath)

        outputFilePath = os.path.join(seriesFilePath, newFileName)

        # Save the decompressed file
        try:
            dicom.save_as(outputFilePath)
        except OSError as e:
            if e.errno != errno.ENOENT:     # No such file or directory error
                print ("ERROR: No such file or directory named " + outputFilePath)
                raise

        # Update progress bar
        print_progress(i + 1, l, prefix = 'Progress:', suffix = 'Complete', bar_length = 50)
        i = i + 1