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
#   python decompressDICOM.py <COMPRESSED_DICOM_FOLDER>
#
# Notes:
#   -The decompressed DICOM directory it will be created automatically
#    in the compressed DICOM folder and will be named: decompressedDICOMs
#-----------------------------------------------------

import pydicom
import argparse
import os
import sys
import errno
import platform

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

parser = argparse.ArgumentParser()
parser.add_argument("inputDirectory", type=str, help="The input DICOM directory (compressed files)")
args = parser.parse_args()

inputPath = args.inputDirectory

# Check if the provided directory exists
if not os.path.exists(inputPath):
    print ("Error: provided directory does not exist!")
    sys.exit(1)

# Get the current system (e.g. Windows =  Windows, Mac OSX = Darwin, Linux = Linux)
# Slashes in paths are different for Windows vs. Mac and Linux
system = platform.system()

# Get the absolute path of the directory provided
if system == "Windows":
    inputPathAbs = os.path.abspath(inputPath)
    outputPathAbs = inputPathAbs + "\\decompressedDICOMs"
else:
    inputPathAbs = os.path.abspath(inputPath)
    outputPathAbs = inputPathAbs + "/decompressedDICOMs"

# Create the directory for decompressed DICOMs inside the compressed DICOM folder
try:
    os.mkdir(outputPathAbs)
except OSError as e:
    if e.errno != errno.EEXIST:     # Directory already exists error
        raise

# Get the number of files in a directory for the progress bar
l = len( [ name for name in os.listdir(inputPathAbs) if os.path.isfile( os.path.join(inputPathAbs, name) ) ] )

# Counter for the progress bar
i = 0

# Loop through all DICOMs in the provided directory, rename and decompress
for file in os.listdir(inputPathAbs):
    filename = os.fsdecode(file)

    currentFilePath = os.path.join(inputPathAbs, filename)

    # Check if we have a file
    if os.path.isfile(currentFilePath):

        # Read the DICOM file. Make sure we have a valid DICOM file...
        try:
            dicom = pydicom.dcmread(currentFilePath)
        except InvalidDicomError:
            print ("File: " + currentFilePath + " is not a valid DICOM file. Skipping...")
            continue

        # Check transfer syntax tag in DICOM header to see if file is compressed or not
        # If the file is already decompressed, skip it
        tsUID = dicom.file_meta.TransferSyntaxUID

        # Uncompressed Implicit VR Little-endian = 1.2.840.10008.1.2
        # Uncompressed Explicit VR Little-endian = 1.2.840.10008.1.2.1
        # Uncompressed Explicit VR Big-endian = 1.2.840.10008.1.2.2
        if (tsUID == "1.2.840.10008.1.2") or (tsUID == "1.2.840.10008.1.2.1") or (tsUID == "1.2.840.10008.1.2.2"):
            print ("File " + filename + " is not compressed...")
            continue

        # Rename the DICOM file to include a file extension (if needed)
        if "." not in filename:
            outputFilePath = os.path.join(outputPathAbs, filename + ".dcm")

            dicom.decompress()

            # Save the decompressed file
            try:
                dicom.save_as(outputFilePath)
            except OSError as e:
                if e.errno != errno.ENOENT:     # No such file or directory error
                    print ("ERROR: No such file or directory named " + outputFilePath)
                    raise

        # For cases when we have compressed DICOMs with file extensions
        elif ".dcm" in filename:
            outputFilePath = os.path.join(outputPathAbs, filename)

            dicom.decompress()

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

print ("Done!")
