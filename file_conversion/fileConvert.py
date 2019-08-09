# coding=utf-8
#----------------------------------------------------- 
# fileConvert.py
#
# Created by:   Michael Kuczynski
# Created on:   2019.08.09
#
# Description: Converts between 3D image file formats.
#              Currently supported conversions:
#                   1. DICOM to NIfTI
#                   2. DICOM to MHA
#                   3. NIfTI to MHA
#                   4. MHA to NIfTI
#                   5. AIM to NIfTI
#                   6. AIM to MHA
#                   7. AIM to MHD/RAW
#
#----------------------------------------------------- 
#
# Requirements:
#   -Python 2.7
#   -VTK 6.3
#   -vtkbone
#
# Usage:
#   python fileConvert.py <inputImage.ext> <outputImage.ext>
#-----------------------------------------------------

import os
import vtk
import sys
import vtkbone
import argparse

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
else :
    print "Error: output file extension must be MHD, MHA, RAW, or NII"
    sys.exit(1)

# Check if the input is a DICOM series directory
if os.path.isfile(inputImage) :
    # Extract directory, filename, basename, and extensions from the input image
    inDirectory, inFilename = os.path.split(inputImage)
    inBasename, inExtension = os.path.splitext(inFilename)

    # Setup the correct reader based on the input image extension
    if inExtension.lower() == ".mhd" or inExtension.lower() == ".raw" or inExtension.lower() == ".mha" :
        imageReader = vtk.vtkMetaImageReader()
        imageReader.SetFileName(inputImage)
        imageReader.Update()  

        finalImage = vtk.vtkImageData()
        finalImage = imageReader.GetOutput()
    elif inExtension.lower() == ".nii" :
        imageReader = vtk.vtkNIFTIImageReader()  
        imageReader.SetFileName(inputImage)
        imageReader.Update()

        finalImage = vtk.vtkImageData()
        finalImage = imageReader.GetOutput()
    elif inExtension.lower() == ".aim" :
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

        if (inputScalarType == vtk.VTK_BIT or inputScalarType == vtk.VTK_CHAR or
            inputScalarType == vtk.VTK_SIGNED_CHAR or
            inputScalarType == vtk.VTK_UNSIGNED_CHAR) :

            # Make sure the image will fit in the range
            #   It is possible that the chars are defined in such a way that either
            #   signed or unsigned chars don't fit inside the char. We can be safe
            #   buy checking if the image range will fit inside the VTK_CHAR
            scalarRange = reader.GetOutput().GetScalarRange()
            if scalarRange[0] >= vtk.VTK_SHORT_MIN and scalarRange[1] <= vtk.VTK_SHORT_MAX :
                outputScalarType = vtk.VTK_CHAR
            else :
                outputScalarType = vtk.VTK_SHORT
        else :
            outputScalarType = vtk.VTK_SHORT
        
        # Cast
        caster = vtk.vtkImageCast()
        caster.SetOutputScalarType(outputScalarType)
        caster.SetInputConnection(reader.GetOutputPort())
        caster.ReleaseDataFlagOff()
        caster.Update()

        finalImage = vtk.vtkImageData()
        finalImage = caster.GetOutput()

# Check if the input is a DICOM series directory
elif os.path.isdir(inputImage) :
    # Check if the directory exists
    if not os.path.exists(inputImage):
        print "Error: DICOM directory does not exist!"
        sys.exit(1)
    else :
        imageReader = vtk.vtkDICOMImageReader()
        imageReader.SetDirectoryName(inputImage) 
        imageReader.Update()  

        # vtkDICOMReader always flips images bottom-to-top.
        # In order to have a coordinate system defined at the top left corner we need to set the direction cosines.
        # (i.e. the first pixel for each slice is the top left corner, and images are in ascending order)
        resliceFilter = vtk.vtkImageReslice()
        resliceFilter.SetInputConnection( imageReader.GetOutputPort() )

        # Direction cosines will be different for NIfTI vs. MHA!
        if outExtension.lower() == ".mha" or outExtension.lower() == ".mhd" or outExtension.lower() == ".raw" :
            resliceFilter.SetResliceAxesDirectionCosines(1,0,0, 0,-1,0, 0,0,1)
        elif outExtension.lower() == ".nii" :
            resliceFilter.SetResliceAxesDirectionCosines(-1,0,0, 0,1,0, 0,0,1)

        resliceFilter.SetInterpolationModeToCubic()
        resliceFilter.Update()

        finalImage = vtk.vtkImageData()
        finalImage = resliceFilter.GetOutput()

# Setup the correct writer based on the output image extension
if outExtension.lower() == ".mha" :
    print "Writing file: " + str(inputImage) + " to " + str(outputImage)

    writer = vtk.vtkMetaImageWriter()
    writer.SetFileName( str(outputImageFileName) ) 
    writer.SetInputData(finalImage)
    writer.Write()
elif outExtension.lower() == ".mhd" or outExtension.lower() == ".raw" :
    print "Writing file: " + str(inputImage) + " to " + str(outputImage)

    writer = vtk.vtkMetaImageWriter()
    writer.SetFileName( str(outputImageFileName) ) 
    writer.SetRAWFileName( str(outputImageFileNameRAW) )
    writer.SetInputData(finalImage)
    writer.Write()
elif outExtension.lower() == ".nii" :
    print "Writing file: " + str(inputImage) + " to " + str(outputImage)
    
    writer = vtk.vtkNIFTIImageWriter()
    writer.SetFileName( str(outputImageFileName) ) 
    writer.SetInputData(finalImage)
    writer.Write()