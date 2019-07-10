# coding=utf-8
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
# Description: Converts AIMs to MHA files.
#
# History:
# 2016.08.18  Andres Kroker Created
# 2018.02.18  Sarah Manske  Modified to use vtkbone instead of vtkbonelab.
#                           Will not work as AIM writer
# 2018.07.17 Scott Brunet   Modified to convert file to NIfTI format
#                           if extension is .nii
#----------------------------------------------------- 
#
# Notes:
#  - Need numerics88 libraries
#  - $ conda create –n imgproc –c numerics88 python=2.6 vtk vtkbone
#  - $ source activate imgproc
#  - $ conda update hdf4
#
# Usage:
#   First run the command:  source activate imgproc     (or "activate imgproc")
#   Next, run the script:   python Aim2MhaVtkBone.py inputImage.AIM outputImage.MHA
#----------------------------------------------------- 

# Imports
import vtk
import vtkbone
import argparse
import os

# Parse input arguments
parser = argparse.ArgumentParser()
parser.add_argument("inputImage",
                    type=str,
                    help="The input AIM image")
parser.add_argument("outputImage",
                    type=str,
                    help="The output Mhd image")
args = parser.parse_args()

inputImage = args.inputImage
outputImage = args.outputImage

# extract directory, filename, basename, and extensions
directory, filename = os.path.split(outputImage)
basename, extension = os.path.splitext(filename)

# check if raw file needed
if extension.lower() == ".mha":
    print "no .raw file will be created as info integrated in image file."
elif extension.lower() == ".mhd":
    outputImageRaw = os.path.join(directory, basename + ".raw")
elif extension.lower() == ".nii":
    outputImageRaw = os.path.join(directory, basename + ".raw")
else:
    print "output file extension must be .mhd or .mha. Setting it to .mha"
    outputImage = os.path.join(directory, basename + ".mha")
    extension = ".mha"

# Read in the image
print "Reading {0}".format(inputImage)
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
print "Converting to {0}".format(vtk.vtkImageScalarTypeNameMacro(outputScalarType))
caster = vtk.vtkImageCast()
caster.SetOutputScalarType(outputScalarType)
caster.SetInputConnection(reader.GetOutputPort())
caster.ReleaseDataFlagOff()
caster.Update()

# Write the image out
if extension.lower() == '.mha':
    print "Writing to {0}".format(outputImage)
    writer = vtk.vtkMetaImageWriter()
    writer.SetInputConnection(caster.GetOutputPort())
    writer.SetFileName(outputImage)
    writer.Write()
# else:
#     print "Writing to {0}".format(outputImage)
#     writer = vtk.vtkMetaImageWriter()
#     writer.SetInputConnection(caster.GetOutputPort())
#     writer.SetFileName(outputImage)
#     writer.SetRAWFileName(outputImageRaw)
#     writer.Write()

if extension.lower() == '.nii':
    print "Writing to {0}".format(outputImage)
    writer = vtk.vtkNIFTIImageWriter()
    writer.SetInputConnection(caster.GetOutputPort())
    writer.SetFileName(outputImage)
    writer.Write()
