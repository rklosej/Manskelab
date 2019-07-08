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
#   -gdcm, gdcm-applications
#
# Usage:
#   decompressDICOM.py DICOM_FOLDER
#----------------------------------------------------- 

#import gdcm
import os
import sys
import subprocess
import platform
import argparse
import errno

def dir_path(string):
    if os.path.isdir(string):
        return string
    else:
        raise NotADirectoryError(string)

# Check the OS type (to handle correct slash directions in file paths)
OS = platform.system()

# Read in the input DICOM directory
parser = argparse.ArgumentParser()
parser.add_argument("inputDirectory", type=dir_path, help="The input (compressed) DICOM directory")
parser.add_argument("outputDirectory", type=dir_path, default=os.getcwd() ,help="The output (decompressed) DICOM directory")
args = parser.parse_args()

# Make sure we use the absolute path!
inputDirectory = os.path.abspath(args.inputDirectory) + "/"
outputDirectory = os.path.abspath(args.outputDirectory) + "/"

# Try to create a directory for the decompressed DICOMs
# Directory location by default is the current working directory (where this python script is located),
# but it can also be set with an additional command line arguement
try:
    os.mkdir(outputDirectory + "decompressed_DICOMs")
except OSError as e:
    if e.errno != errno.EEXIST:     # Directory already exists error
        raise

print (inputDirectory)

for file in os.listdir(inputDirectory):
    filename = os.fsdecode(file)
    inputFile = os.path.join(inputDirectory, filename)

    # Check if we have a file
    if os.path.isfile(inputFile):

        # Decompress the DICOM files without a file extension
        if "." not in filename:
            outputFile = os.path.join(outputDirectory + "decompressed_DICOMs", filename + ".dcm")

            # Just run the gdcmconv command on each file
            command = "gdcmconv -w " + inputFile + " " + outputFile

            os.system(command)

        elif ".dcm" in filename:
            outputFile = os.path.join(outputDirectory + "decompressed_DICOMs", filename)

            # Just run the gdcmconv command on each file
            command = "gdcmconv -w " + inputFile + " " + outputFile

            os.system(command)

print ("Done!")
