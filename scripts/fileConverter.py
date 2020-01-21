#----------------------------------------------------- 
# fileConverter.py
#
# Created by:   Michael Kuczynski
# Created on:   21-01-2020
#
# Description: Converts between 3D image file formats.
#              Currently supported conversions:
#                   1. DICOM to NIfTI
#                   2. DICOM to MHA
#                   3. DICOM to AIM
#                   4. NIfTI to MHA
#                   5. NIfTI to AIM
#                   6. NIfTI to DICOM
#                   7. MHA to NIfTI
#                   8. MHA to AIM
#                   9. MHA to DICOM
#                   10. AIM to NIfTI
#                   11. AIM to MHA
#                   12. AIM to DICOM
#
# Notes: File format conversion can be done using several different software libraries/packages. 
# However, when reading in images, VTK does not store the image orientation, direction, or origin. 
# This causes problems when trying to overlay images after conversion. ITK based libraries/packages 
# (like SimpleITK) are able to maintain the original image orientation, direction, and origin.
# Unfortunately, SimpleITK cannot read/write AIM files. vtkbone however, can. The quick solution to
# these problems is to use SimpleITK for all image conversions except AIM and use vtkbone only for AIMs.
#
# Some useful links that explain image orientation, direction, and origin:
#   -https://www.slicer.org/wiki/Coordinate_systems
#   -https://discourse.vtk.org/t/proposal-to-add-orientation-to-vtkimagedata-feedback-wanted/120
#   -http://www.itksnap.org/pmwiki/pmwiki.php?n=Documentation.DirectionMatrices
#   -https://fromosia.wordpress.com/2017/03/10/image-orientation-vtk-itk/
#
#----------------------------------------------------- 
# Usage:
#   python fileConverter.py <inputImage.ext> <outputImage.ext>
#-----------------------------------------------------

import os
import sys
import time
import argparse
import numpy as np

from util.sitk_vtk import sitk2vtk, vtk2sitk
from util.img2dicom import img2dicom

import vtk
import vtkbone

import SimpleITK as sitk

# Parse input arguments
parser = argparse.ArgumentParser()
parser.add_argument( "inputImage", type=str, help="The input image (path + filename)" )
parser.add_argument( "outputImage", type=str, help="The output image (path + filename)" )
args = parser.parse_args()

inputImage = args.inputImage
outputImage = args.outputImage

# Extract directory, filename, basename, and extensions from the output image
outDirectory, outFilename = os.path.split(outputImage)
outBasename, outExtension = os.path.splitext(outFilename)

# Check the output file format
if outExtension.lower() == ".mha" :
    outputImageFileName = os.path.join(outDirectory, outBasename + ".mha")
elif outExtension.lower() == ".mhd" or outExtension.lower() == ".raw" :
    outputImageFileName = os.path.join(outDirectory, outBasename + ".mhd")
    outputImageFileNameRAW = os.path.join(outDirectory, outBasename + ".raw")
elif outExtension.lower() == ".nii" :
    outputImageFileName = os.path.join(outDirectory, outBasename + ".nii")
elif outExtension.lower() == ".aim" :
    outputImageFileName = os.path.join(outDirectory, outBasename + ".aim")
elif outExtension.lower() == ".dcm" :
    outputImageFileName = os.path.join(outDirectory, outBasename + ".dcm")
else :
    print ("Error: output file extension must be MHD, MHA, RAW, NII, or AIM")
    sys.exit(1)

# Check if the input is a DICOM series directory
if os.path.isfile(inputImage) :
    # NOT DICOM SERIES

    # Extract directory, filename, basename, and extensions from the input image
    inDirectory, inFilename = os.path.split(inputImage)
    inBasename, inExtension = os.path.splitext(inFilename)

    # Setup the correct reader based on the input image extension
    if inExtension.lower() == ".aim" :
        imageReader = vtkbone.vtkboneAIMReader()
        imageReader.SetFileName(inputImage)
        imageReader.DataOnCellsOff()
        imageReader.Update()

        # Determine scalar type to use
        #   VTK_CHAR <-> D1char
        #   VTK_SHORT <-> D1short
        #   If it is of type BIT, CHAR, SIGNED CHAR, or UNSIGNED CHAR it is possible
        #   to store in a CHAR.
        inputScalarType = imageReader.GetOutput().GetScalarType()

        if (inputScalarType == vtk.VTK_BIT or inputScalarType == vtk.VTK_CHAR or
            inputScalarType == vtk.VTK_SIGNED_CHAR or
            inputScalarType == vtk.VTK_UNSIGNED_CHAR) :

            # Make sure the image will fit in the range
            #   It is possible that the chars are defined in such a way that either
            #   signed or unsigned chars don't fit inside the char. We can be safe
            #   buy checking if the image range will fit inside the VTK_CHAR
            scalarRange = imageReader.GetOutput().GetScalarRange()
            if scalarRange[0] >= vtk.VTK_SHORT_MIN and scalarRange[1] <= vtk.VTK_SHORT_MAX :
                outputScalarType = vtk.VTK_CHAR
            else :
                outputScalarType = vtk.VTK_SHORT
        else :
            outputScalarType = vtk.VTK_SHORT
    
        # Cast
        caster = vtk.vtkImageCast()
        caster.SetOutputScalarType(outputScalarType)
        caster.SetInputConnection(imageReader.GetOutputPort())
        caster.ReleaseDataFlagOff()
        caster.Update()

        vtk_image = caster.GetOutput()
        sitk_image = vtk2sitk(vtk_image)
    
    else :
        sitk_image = sitk.ReadImage(inputImage)
        vtk_image = sitk2vtk(sitk_image)

# Check if the input is a DICOM series directory
elif os.path.isdir(inputImage) :
    # DICOM DIRECTORY

    # Check if the directory exists
    if not os.path.exists(inputImage):
        print ("Error: DICOM directory does not exist!")
        sys.exit(1)
    else :
        reader = sitk.ImageSeriesReader()

        dicom_names = reader.GetGDCMSeriesFileNames( inputImage )
        reader.SetFileNames( dicom_names )

        sitk_image = reader.Execute()
        vtk_image = sitk2vtk(sitk_image)

# Setup the correct writer based on the output image extension
if outExtension.lower() == ".mha" :
    print ("Writing file: " + str(inputImage) + " to " + str(outputImage))
    sitk.WriteImage(sitk_image, str(outputImageFileName))

elif outExtension.lower() == ".mhd" or outExtension.lower() == ".raw" :
    print ("Writing file: " + str(inputImage) + " to " + str(outputImage))
    sitk.WriteImage(sitk_image, str(outputImageFileName))

elif outExtension.lower() == ".nii" :
    print ("Writing file: " + str(inputImage) + " to " + str(outputImage))
    sitk.WriteImage(sitk_image, str(outputImageFileName))

elif outExtension.lower() == ".dcm" :
    print ("Writing file: " + str(inputImage) + " to " + str(outputImage))
    img2dicom(sitk_image, outDirectory)

elif outExtension.lower() == ".aim" :
    print ("Writing file: " + str(inputImage) + " to " + str(outputImage))
    writer = vtkbone.vtkboneAIMWriter()
    writer.SetFileName( str(outputImageFileName) ) 
    writer.SetInputData(vtk_image)
    writer.Write()

print ("Done!")