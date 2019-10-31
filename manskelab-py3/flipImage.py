# coding=utf-8
#-----------------------------------------------------
# flipImage.py
#
# Created by:   Michael Kuczynski
# Created on:   2019.08.26
#
# Description: Flips an image about a specified axis.
#-----------------------------------------------------
#
# Requirements:
#   -Python 3.4 or later
#
# Usage:
#   1. python flipImage.py <INPUT_IMAGE_DIRECTORY> <FLIP_AXIS>
#
#   2. python flipImage.py <INPUT_IMAGE_DIRECTORY> <OUTPUT_DIRECTORY> <FLIP_AXIS>
#
# Notes:
#   -Current accepted file formats: NIfTI (.nii), MHA (.mha), DICOM series (provide directory containing uncompressed .dcm files)
#   -All images are written out as MHA images.
#   -Note that there is currently no functionality to check if a valid DICOM directory has been provided. You MUST provide a DICOM
#    directory that contains only one series and no other files (ONLY uncompressed .dcm files).
#-----------------------------------------------------

import os
import sys
import vtk
import errno
import ntpath
import pydicom
import argparse
import platform

# Read in the input arguements
parser = argparse.ArgumentParser()

parser.add_argument("inputPath", type=str, nargs="?", help="The input image file path")
parser.add_argument("-o", "--outputPath", type=str, nargs="?", default=os.getcwd() , help="The output image file path")
parser.add_argument("flipAxis", type=str, nargs="?", help="The axis to flip the image about")

args = parser.parse_args()

inputPath = args.inputPath
outputPath = args.outputPath
flipAxis = str(args.flipAxis).lower()

assert flipAxis == "x" or flipAxis == "y" or flipAxis == "z" or flipAxis == "xy" or flipAxis == "yx" or flipAxis == "xz" or flipAxis == "zx" or flipAxis == "yz" or flipAxis == "zy"

# Get the absolute path for the input
inputPathAbs = os.path.abspath(inputPath)
outputPathAbs = os.path.abspath(outputPath)

# Check if the output directory exists
if not os.path.exists(outputPathAbs):
    print ("Error: output directory does not exist!")
    sys.exit(1)

# First determine the type of image being input (e.g. NIfTI, MHA, DICOM series, etc.)
# If the input is a directory, we are getting a DICOM series
if os.path.isdir(inputPathAbs) :
    if not os.path.exists(inputPathAbs):
        print ("Error: DICOM directory does not exist!")
        sys.exit(1)
    else:
        filename, fileExtension = os.path.splitext(inputPathAbs)
        
        imageReader = vtk.vtkDICOMImageReader()
        imageReader.SetDirectoryName(inputPathAbs) 
        imageReader.Update()  

# If the input is a file, check if it is NIfTI or MHA
elif os.path.isfile(inputPathAbs) :
    filename, fileExtension = os.path.splitext(inputPathAbs)
    outputPath, outputFile = ntpath.split(outputPathAbs)

    # Check if the provided file exists and is a valid format
    if not os.path.isfile(inputPathAbs) :
        print ("Error: provided file does not exist!")

    if str(fileExtension).lower() == ".nii" :
        imageReader = vtk.vtkNIFTIImageReader()  
        imageReader.SetFileName(inputPathAbs)
        imageReader.Update()  
    
    elif str(fileExtension).lower() == ".mha" :  
        imageReader = vtk.vtkMetaImageReader()
        imageReader.SetFileName(inputPathAbs)
        imageReader.Update()  

else :
    print ("Error: Unrecognized input file type.")
    sys.exit(1)

image = imageReader.GetOutput()

resliceFilter = vtk.vtkImageReslice()
resliceFilter.SetInputData(image)

print ("Flipping image: " + filename + fileExtension + " about axis: " + str(flipAxis).upper() + "...")

# Flip the image
if flipAxis == "x" :
    resliceFilter.SetResliceAxesDirectionCosines(-1,0,0, 0,1,0, 0,0,1)
elif flipAxis == "y" :
    resliceFilter.SetResliceAxesDirectionCosines(1,0,0, 0,-1,0, 0,0,1)
elif flipAxis == "z" :
    resliceFilter.SetResliceAxesDirectionCosines(1,0,0, 0,1,0, 0,0,-1)
elif flipAxis == "xy" or flipAxis == "yx":
    resliceFilter.SetResliceAxesDirectionCosines(-1,0,0, 0,-1,0, 0,0,1)
elif flipAxis == "xz" or flipAxis == "zx":
    resliceFilter.SetResliceAxesDirectionCosines(-1,0,0, 0,1,0, 0,0,-1)
elif flipAxis == "yz" or flipAxis == "zy":
    resliceFilter.SetResliceAxesDirectionCosines(1,0,0, 0,-1,0, 0,0,-1)

# Once the image is flipped, it needs to be moved back to the original image origin
resliceFilter.SetOutputOrigin(image.GetOrigin())
resliceFilter.Update()

# Get the new image and write it out as a MHA image
imageResampled = resliceFilter.GetOutput()

# Create the output file name (resliced)
outputFileName = os.path.join(outputPathAbs, filename + "_" + flipAxis + ".mha")

print ("Writing out flipped image as: " + outputFileName + "...")

writer = vtk.vtkMetaImageWriter()
writer.SetFileName( str(outputFileName) ) 
writer.SetInputData(imageResampled)
writer.Write()

print ("Done!")