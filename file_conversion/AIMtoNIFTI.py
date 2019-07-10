# coding: utf-8
#----------------------------------------------------- 
# AIMtoNIFTI.py
#
# Created by:   Andres Kroker
# Created on:   2016.08.18
#
# Modified by:  Sarah Manske | Scott Brunet
# Modified on:  2018.02.18   | 2018.07.17
#
# Adapted by:   Michael Kuczynski
# Adapted on:   2018.10.05
#
# Description: Converts AIM files to NIFTI files.
#----------------------------------------------------- 
#
# Requirements:
#   -Python 2.7
#   -numerics88 libraries (vtk and vtkbone)
#
# Usage:
#   First run the command:  source activate imgproc     (or "activate imgproc")
#   Next, run the script:   python Aim2MhaVtkBone.py inputImage.AIM outputImage.NII
#----------------------------------------------------- 

# Imports
import vtk
import vtkbone
import argparse
import os

# Parse input arguments
parser = argparse.ArgumentParser()
parser.add_argument("inputImage", type=str, help="The input AIM image")
parser.add_argument("outputImage", type=str, help="The output NIfTI image")
args = parser.parse_args()

inputImage = args.inputImage
outputImage = args.outputImage

# Extract directory, filename, basename, and extensions
directory, filename = os.path.split(outputImage)
basename, extension = os.path.splitext(filename)

# Make sure the file extension is lower case.
# There is some issue opening upper case file extensions in Dragonfly. 
if extension.islower() == False:
    extension = extension.lower()

# Check if file extension is correct (.nii)
if extension != ".nii":
    print "\nERROR: Output file extension must be .nii"
    print "Please try running the script again with the proper input:\n"
    print "Usage: python Aim2MhaVtkBone.py inputImage.AIM outputImage.NII"
    exit()
else:
    print "Converting to NIfTI file...\n"
    outputImageNIfTI = os.path.join(directory, basename + extension)

# Read in the image using VTKBone's AIM reader
print "Reading " + inputImage + "\n"
reader = vtkbone.vtkboneAIMReader()
reader.SetFileName(inputImage)
reader.DataOnCellsOff()
reader.Update()

# Determine scalar type to use
#   VTK_CHAR <-> D1char
#   VTK_SHORT <-> D1short
#   If it is of type BIT, CHAR, SIGNED CHAR, or UNSIGNED CHAR it is possible
#   to store in a CHAR.
inputScalarType = reader.GetOutput().GetScalarType()
if (inputScalarType == vtk.VTK_BIT or
    inputScalarType == vtk.VTK_CHAR or
    inputScalarType == vtk.VTK_SIGNED_CHAR or
    inputScalarType == vtk.VTK_UNSIGNED_CHAR):

    # Make sure the image will fit in the range
    #   It is possible that the chars are defined in such a way that either
    #   signed or unsigned chars don't fit inside the char. We can be safe
    #   buy checking if the image range will fit inside the VTK_CHAR
    scalarRange = reader.GetOutput().GetScalarRange()
    if scalarRange[0] >= vtk.VTK_SHORT_MIN and scalarRange[1] <= vtk.VTK_SHORT_MAX:
        outputScalarType = vtk.VTK_CHAR
    else:
        outputScalarType = vtk.VTK_SHORT
else:
    outputScalarType = vtk.VTK_SHORT

# Cast
print "Converting to " + str(vtk.vtkImageScalarTypeNameMacro(outputScalarType)) + "...\n"
caster = vtk.vtkImageCast()
caster.SetOutputScalarType(outputScalarType)
caster.SetInputConnection(reader.GetOutputPort())
caster.ReleaseDataFlagOff()
caster.Update()

# Write out the image as .nii
print "Writing to " + outputImageNIfTI
writer = vtk.vtkNIFTIImageWriter()
writer.SetInputConnection(caster.GetOutputPort())
writer.SetFileName(outputImageNIfTI)
writer.Write()

print "\nDone!"