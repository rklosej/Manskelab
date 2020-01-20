# # coding=utf-8
# #-----------------------------------------------------
# # resample.py
# #
# # Created by:   Michael Kuczynski
# # Created on:   2019.08.07
# #
# # Description: Resamples input images based on specified user input parameters.
# #-----------------------------------------------------
# #
# # Requirements:
# #   -Python 3.4 or later
# #
# # Usage:
# #   1. python resample.py <INPUT_IMAGE> <OUTPUT_DIRECTORY> <OUTPUT_SPACING_X> <OUTPUT_SPACING_Y> <OUTPUT_SPACING_Z>
# #
# #   2. python resample.py <INPUT_DICOM_DIRECTORY> <OUTPUT_DIRECTORY> <OUTPUT_SPACING_X> <OUTPUT_SPACING_Y> <OUTPUT_SPACING_Z>
# #
# # Notes:
# #   -Current accepted file formats: NIfTI (.nii), MHA (.mha), DICOM series (provide directory containing uncompressed .dcm files)
# #
# #   -If the input is a DICOM series, the output will be a NIfTI image. Writing out a DICOM series takes more work... (TO-DO later)
# #       -Note that there is currently no functionality to check if a valid DICOM directory has been provided. You MUST provide a DICOM
# #        directory that contains only one series and no other files (ONLY uncompressed .dcm files).
# #
# #   -Spacing = voxel size
# #   -Extent  = dimensions
# #   -Origin  = where the image is centred (i.e. image origin)
# #   -Bounds  = Extent * Spacing + Origin
# #-----------------------------------------------------

import os
import sys
import vtk
from vtk import vtkStructuredPointsReader
import errno
import ntpath
import pydicom
import argparse
import platform

# Load Nifti Image
NiftiReader = vtk.vtkNIFTIImageReader()  
NiftiReader.SetFileName("D:\\Git\\ENME683\\img\\calibrationMarkers_CT.nii")
NiftiReader.Update()  
NiftiImage = NiftiReader.GetOutput()



# meshReader = vtk.vtkPolyDataReader
# meshReader.SetFileName( "D:\\Git\\ENME683\\img\\MA_CT_MARKERS00001.vtk" )
# meshReader.Update()
# xMarker = meshReader.GetOutput()

reader = vtkStructuredPointsReader()
reader.SetFileName("D:\\Git\\ENME683\\img\\MA_CT_MARKERS00001.vtk")
reader.ReadAllVectorsOn()
reader.ReadAllScalarsOn()
reader.Update()
xMarker = reader.GetOutput()


cutter = vtk.vtkCutter()
if vtk.VTK_MAJOR_VERSION <= 5:
    cutter.SetInput(reader.GetOutput())
else:
    cutter.SetInputConnection(reader.GetOutputPort())
cutter.SetCutFunction(plane)
stripper2 = vtk.vtkStripper()
if vtk.VTK_MAJOR_VERSION <= 5:
    stripper2.SetInput(cutter.GetOutput())
else:
    stripper2.SetInputConnection(cutter.GetOutputPort())
dataToStencil2 = vtk.vtkPolyDataToImageStencil()
if vtk.VTK_MAJOR_VERSION <= 5:
    dataToStencil2.SetInput(stripper2.GetOutput())
else:
    dataToStencil2.SetInputConnection(stripper2.GetOutputPort())
dataToStencil2.SetOutputSpacing(0.8, 0.8, 1.5)
dataToStencil2.SetOutputOrigin(0.0, 0.0, 0.0)
stencil2 = vtk.vtkImageStencil()
if vtk.VTK_MAJOR_VERSION <= 5:
    stencil2.SetInput(reader2.GetOutput())
    stencil2.SetStencil(dataToStencil2.GetOutput())
else:
    stencil2.SetInputConnection(reader2.GetOutputPort())
    stencil2.SetStencilConnection(dataToStencil2.GetOutputPort())
stencil2.SetBackgroundValue(500)

# contour = vtk.vtkMarchingCubes()
# contour.SetInputConnection(reader.GetOutputPort())
# contour.Update()

# pol2stenc = vtk.vtkPolyDataToImageStencil()
# pol2stenc.SetInputConnection(contour.GetOutputPort())
# pol2stenc.SetOutputOrigin(0,0,0)
# pol2stenc.SetOutputSpacing(0.5,0.5,1.25)
# pol2stenc.Update()


writer = vtk.vtkNIFTIImageWriter()
writer.SetFileName( "D:\\Git\\ENME683\\img\\test2.nii")
writer.SetInputData(pol2stenc.GetOutput())
writer.Write()


# #   // polygonal data --> image stencil:
# #   vtkSmartPointer<vtkPolyDataToImageStencil> pol2stenc = vtkSmartPointer<vtkPolyDataToImageStencil>::New();
# # #if VTK_MAJOR_VERSION <= 5
# #   pol2stenc->SetInput(xMarker);
# # #else
# #   pol2stenc->SetInputData(xMarker);
# # #endif
# #   pol2stenc->SetOutputOrigin(origin);
# #   pol2stenc->SetOutputSpacing(spacing);
# #   pol2stenc->SetOutputWholeExtent(whiteImage->GetExtent());
# #   pol2stenc->Update();

# #   // cut the corresponding white image and set the background:
# #   vtkSmartPointer<vtkImageStencil> imgstenc = vtkSmartPointer<vtkImageStencil>::New();
# # #if VTK_MAJOR_VERSION <= 5
# #   imgstenc->SetInput(whiteImage);
# #   imgstenc->SetStencil(pol2stenc->GetOutput());
# # #else
# #   imgstenc->SetInputData(whiteImage);
# #   imgstenc->SetStencilConnection(pol2stenc->GetOutputPort());
# # #endif
# #   imgstenc->ReverseStencilOff();
# #   imgstenc->SetBackgroundValue(outval);
# #   imgstenc->Update();









# # #Print some information about the image
# # print ( "Dimensions:  " + str(NiftiImage.GetDimensions()) )
# # print ( "Spacing:     " + str( round( NiftiImage.GetSpacing()[0], 4 ) ) 
# #                         + str( round( NiftiImage.GetSpacing()[1], 4 ) ) 
# #                         + str( round( NiftiImage.GetSpacing()[2], 4 ) ) )
# # print ( "Origin:      " + str(NiftiImage.GetOrigin()) )

# # print ( "\nResampling the input image. New image information will be:" )
# # print ( "Dimensions:   " + str(NiftiImage.GetDimensions()) )
# # print ( "Spacing:     (" + str(spacingX) + ", " + str(spacingY) + ", " + str(spacingZ) + ")" )
# # print ( "Origin:       " + str(NiftiImage.GetOrigin()) )

# # resliceFilter = vtk.vtkImageReslice()
# # resliceFilter.SetInputData(NiftiImage)
# # resliceFilter.SetOutputSpacing(spacingX, spacingY, spacingZ)
# # resliceFilter.SetInterpolationModeToCubic()
# # resliceFilter.Update()
# # imageResampled = resliceFilter.GetOutput()

# # writer = vtk.vtkNIFTIImageWriter()
# # writer.SetFileName( str(outputFileName) ) 
# # writer.SetInputData(imageResampled)
# # writer.Write()
    
  





# import vtk
# from vtk.util.misc import vtkGetDataRoot

# VTK_DATA_ROOT = vtkGetDataRoot()

# # A script to test the stencil filter with a polydata stencil.
# # Image pipeline
# reader = vtk.vtkPNGReader()
# reader.SetDataSpacing(0.8, 0.8, 1.5)
# reader.SetDataOrigin(0.0, 0.0, 0.0)
# reader.SetFileName("M:\\02 Projects\\RAMHA\\BRISQUE\\test.png")
# sphere = vtk.vtkSphereSource()
# sphere.SetPhiResolution(12)
# sphere.SetThetaResolution(12)
# sphere.SetCenter(102, 102, 0)
# sphere.SetRadius(60)
# triangle = vtk.vtkTriangleFilter()
# if vtk.VTK_MAJOR_VERSION <= 5:
#     triangle.SetInput(sphere.GetOutput())
# else:
#     triangle.SetInputConnection(sphere.GetOutputPort())

# stripper = vtk.vtkStripper()
# if vtk.VTK_MAJOR_VERSION <= 5:
#     stripper.SetInput(triangle.GetOutput())
# else:
#     stripper.SetInputConnection(triangle.GetOutputPort())
# dataToStencil = vtk.vtkPolyDataToImageStencil()
# if vtk.VTK_MAJOR_VERSION <= 5:
#     dataToStencil.SetInput(stripper.GetOutput())
# else:
#     dataToStencil.SetInputConnection(stripper.GetOutputPort())
# dataToStencil.SetOutputSpacing(0.8, 0.8, 1.5)
# dataToStencil.SetOutputOrigin(0.0, 0.0, 0.0)

# stencil = vtk.vtkImageStencil()
# if vtk.VTK_MAJOR_VERSION <= 5:
#     stencil.SetInput(reader.GetOutput())
#     stencil.SetStencil(dataToStencil.GetOutput())
# else:
#     stencil.SetInputConnection(reader.GetOutputPort())
#     stencil.SetStencilConnection(dataToStencil.GetOutputPort())
# stencil.ReverseStencilOn()
# stencil.SetBackgroundValue(500)

# # test again with a contour
# reader2 = vtk.vtkPNGReader()
# reader2.SetDataSpacing(0.8, 0.8, 1.5)
# reader2.SetDataOrigin(0.0, 0.0, 0.0)
# reader2.SetFileName("M:\\02 Projects\\RAMHA\\BRISQUE\\test.png")
# plane = vtk.vtkPlane()
# plane.SetOrigin(0, 0, 0)
# plane.SetNormal(0, 0, 1)
# cutter = vtk.vtkCutter()
# if vtk.VTK_MAJOR_VERSION <= 5:
#     cutter.SetInput(sphere.GetOutput())
# else:
#     cutter.SetInputConnection(sphere.GetOutputPort())
# cutter.SetCutFunction(plane)
# stripper2 = vtk.vtkStripper()
# if vtk.VTK_MAJOR_VERSION <= 5:
#     stripper2.SetInput(cutter.GetOutput())
# else:
#     stripper2.SetInputConnection(cutter.GetOutputPort())
# dataToStencil2 = vtk.vtkPolyDataToImageStencil()
# if vtk.VTK_MAJOR_VERSION <= 5:
#     dataToStencil2.SetInput(stripper2.GetOutput())
# else:
#     dataToStencil2.SetInputConnection(stripper2.GetOutputPort())
# dataToStencil2.SetOutputSpacing(0.8, 0.8, 1.5)
# dataToStencil2.SetOutputOrigin(0.0, 0.0, 0.0)
# stencil2 = vtk.vtkImageStencil()
# if vtk.VTK_MAJOR_VERSION <= 5:
#     stencil2.SetInput(reader2.GetOutput())
#     stencil2.SetStencil(dataToStencil2.GetOutput())
# else:
#     stencil2.SetInputConnection(reader2.GetOutputPort())
#     stencil2.SetStencilConnection(dataToStencil2.GetOutputPort())
# stencil2.SetBackgroundValue(500)

# imageAppend = vtk.vtkImageAppend()
# if vtk.VTK_MAJOR_VERSION <= 5:
#     imageAppend.SetInput(stencil.GetOutput())
#     imageAppend.AddInput(stencil2.GetOutput())
# else:
#     imageAppend.SetInputConnection(stencil.GetOutputPort())
#     imageAppend.AddInputConnection(stencil2.GetOutputPort())

# viewer = vtk.vtkImageViewer()
# interator = vtk.vtkRenderWindowInteractor()
# if vtk.VTK_MAJOR_VERSION <= 5:
#     viewer.SetInput(imageAppend.GetOutput())
# else:
#     viewer.SetInputConnection(imageAppend.GetOutputPort())
# viewer.SetupInteractor(interator)
# viewer.SetZSlice(0)
# viewer.SetColorWindow(2000)
# viewer.SetColorLevel(1000)
# viewer.Render()

# interator.Start()