# coding=utf-8
#-----------------------------------------------------
# resample.py
#
# Created by:   Michael Kuczynski
# Created on:   2019.08.07
#
# Description: Resamples input images based on specified user input parameters.
#-----------------------------------------------------
#
# Requirements:
#   -Python 3.4 or later
#
# Usage:
#   1. python resample.py <INPUT_IMAGE> <OUTPUT_DIRECTORY> <OUTPUT_SPACING_X> <OUTPUT_SPACING_Y> <OUTPUT_SPACING_Z>
#
#   2. python resample.py <INPUT_DICOM_DIRECTORY> <OUTPUT_DIRECTORY> <OUTPUT_SPACING_X> <OUTPUT_SPACING_Y> <OUTPUT_SPACING_Z>
#
# Notes:
#   -Current accepted file formats: NIfTI (.nii), MHA (.mha), DICOM series (provide directory containing uncompressed .dcm files)
#
#   -If the input is a DICOM series, the output will be a NIfTI image. Writing out a DICOM series takes more work... (TO-DO later)
#       -Note that there is currently no functionality to check if a valid DICOM directory has been provided. You MUST provide a DICOM
#        directory that contains only one series and no other files (ONLY uncompressed .dcm files).
#
#   -Spacing = voxel size
#   -Extent  = dimensions
#   -Origin  = where the image is centred (i.e. image origin)
#   -Bounds  = Extent * Spacing + Origin
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

parser.add_argument("inputPath", type=str, help="The input image file path")
parser.add_argument("outputPath", type=str, help="The output image file path")
parser.add_argument("spacingX", type=str, help="The new voxel size (X)")
parser.add_argument("spacingY", type=str, help="The new voxel size (Y)")
parser.add_argument("spacingZ", type=str, help="The new voxel size (Z)")

args = parser.parse_args()

inputPath = args.inputPath
outputPath = args.outputPath
spacingX = round( float(args.spacingX), 4)
spacingY = round( float(args.spacingY), 4)
spacingZ = round( float(args.spacingZ), 4)

# Get the absolute path for the input
inputPathAbs = os.path.abspath(inputPath)
outputPathAbs = os.path.abspath(outputPath)

# Create the output file name (resliced)
outputFileName = os.path.join(outputPathAbs, "reslice.nii")

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
        dicomReader = vtk.vtkDICOMImageReader()
        dicomReader.SetDirectoryName(inputPathAbs) 
        dicomReader.Update()  
        dicomImage = dicomReader.GetOutput()

        #Print some information about the image
        print ( "Dimensions:  " + str(dicomImage.GetDimensions()) )
        print ( "Spacing:     " + str( round( dicomImage.GetSpacing()[0], 4 ) ) 
                                + str( round( dicomImage.GetSpacing()[1], 4 ) ) 
                                + str( round( dicomImage.GetSpacing()[2], 4 ) ) )
        print ( "Origin:      " + str(dicomImage.GetOrigin()) )
    
        print ( "\nResampling the input image. New image information will be:" )
        print ( "Dimensions:   " + str(dicomImage.GetDimensions()) )
        print ( "Spacing:     (" + str(spacingX) + ", " + str(spacingY) + ", " + str(spacingZ) + ")" )
        print ( "Origin:       " + str(dicomImage.GetOrigin()) )

        resliceFilter = vtk.vtkImageReslice()
        resliceFilter.SetInputData(dicomImage)

        # vtkDICOMReader always flips images bottom-to-top.
        # In order to have a coordinate system defined at the top left corner we need to set the direction cosines.
        # (i.e. the first pixel for each slice is the top left corner, and images are in ascending order)
        resliceFilter.SetResliceAxesDirectionCosines(-1,0,0, 0,1,0, 0,0,1)

        resliceFilter.SetOutputSpacing(spacingX, spacingY, spacingZ)
        resliceFilter.SetInterpolationModeToCubic()
        resliceFilter.Update()
        imageResampled = resliceFilter.GetOutput()

        writer = vtk.vtkNIFTIImageWriter()
        writer.SetFileName( str(outputFileName) ) 
        writer.SetInputData(imageResampled)
        writer.Write()

# If the input is a file, check if it is NIfTI or MHA
elif os.path.isfile(inputPathAbs) :
    filename, fileExtension = os.path.splitext(inputPathAbs)
    outputPath, outputFile = ntpath.split(outputPathAbs)

    # Check if the provided file exists and is a valid format
    if not os.path.isfile(inputPathAbs) :
        print ("Error: provided file does not exist!")

    if str(fileExtension).lower() == ".nii" :
        print ("Input file is NIfTI")
    
        NiftiReader = vtk.vtkNIFTIImageReader()  
        NiftiReader.SetFileName(inputPathAbs)
        NiftiReader.Update()  
        NiftiImage = NiftiReader.GetOutput()
    
        #Print some information about the image
        print ( "Dimensions:  " + str(NiftiImage.GetDimensions()) )
        print ( "Spacing:     " + str( round( NiftiImage.GetSpacing()[0], 4 ) ) 
                                + str( round( NiftiImage.GetSpacing()[1], 4 ) ) 
                                + str( round( NiftiImage.GetSpacing()[2], 4 ) ) )
        print ( "Origin:      " + str(NiftiImage.GetOrigin()) )
    
        print ( "\nResampling the input image. New image information will be:" )
        print ( "Dimensions:   " + str(NiftiImage.GetDimensions()) )
        print ( "Spacing:     (" + str(spacingX) + ", " + str(spacingY) + ", " + str(spacingZ) + ")" )
        print ( "Origin:       " + str(NiftiImage.GetOrigin()) )
    
        resliceFilter = vtk.vtkImageReslice()
        resliceFilter.SetInputData(NiftiImage)
        resliceFilter.SetOutputSpacing(spacingX, spacingY, spacingZ)
        resliceFilter.SetInterpolationModeToCubic()
        resliceFilter.Update()
        imageResampled = resliceFilter.GetOutput()
    
        writer = vtk.vtkNIFTIImageWriter()
        writer.SetFileName( str(outputFileName) ) 
        writer.SetInputData(imageResampled)
        writer.Write()
    
    elif str(fileExtension).lower() == ".mha" :
        print ("Input file is MHA\n")
    
        MetaReader = vtk.vtkMetaImageReader()
        MetaReader.SetFileName(inputPathAbs)
        MetaReader.Update()  
        MetaImage = MetaReader.GetOutput()
    
        #Print some information about the image
        print ( "Dimensions:  " + str(MetaImage.GetDimensions()) )
        print ( "Spacing:     " + str( round( MetaImage.GetSpacing()[0], 4 ) ) 
                                + str( round( MetaImage.GetSpacing()[1], 4 ) ) 
                                + str( round( MetaImage.GetSpacing()[2], 4 ) ) )
        print ( "Origin:      " + str(MetaImage.GetOrigin()) )
    
        print ( "\nResampling the input image. New image information will be:" )
        print ( "Dimensions:   " + str(MetaImage.GetDimensions()) )
        print ( "Spacing:     (" + str(spacingX) + ", " + str(spacingY) + ", " + str(spacingZ) + ")" )
        print ( "Origin:       " + str(MetaImage.GetOrigin()) )
    
        resliceFilter = vtk.vtkImageReslice()
        resliceFilter.SetInputData(MetaImage)
        resliceFilter.SetOutputSpacing(spacingX, spacingY, spacingZ)
        resliceFilter.SetInterpolationModeToCubic()
        resliceFilter.Update()
        imageResampled = resliceFilter.GetOutput()
    
        writer = vtk.vtkMetaImageWriter()
        writer.SetFileName( str(outputFileName) ) 
        writer.SetInputData(imageResampled)
        writer.Write()