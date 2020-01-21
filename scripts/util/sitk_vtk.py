#----------------------------------------------------- 
# sitk-2-vtk.py
#
# Created by:   Michael Kuczynski
# Created on:   21-01-2020
#
# Description: Converts between SimpleITK and VTK image types
#-----------------------------------------------------
import vtk
from vtk.util.numpy_support import vtk_to_numpy

import SimpleITK as sitk

# dictionary to convert SimpleITK pixel types to VTK
pixelmap = { sitk.sitkUInt8:   vtk.VTK_UNSIGNED_CHAR,  sitk.sitkInt8:    vtk.VTK_CHAR,
             sitk.sitkUInt16:  vtk.VTK_UNSIGNED_SHORT, sitk.sitkInt16:   vtk.VTK_SHORT,
             sitk.sitkUInt32:  vtk.VTK_UNSIGNED_INT,   sitk.sitkInt32:   vtk.VTK_INT,
             sitk.sitkUInt64:  vtk.VTK_UNSIGNED_LONG,  sitk.sitkInt64:   vtk.VTK_LONG,
             sitk.sitkFloat32: vtk.VTK_FLOAT,          sitk.sitkFloat64: vtk.VTK_DOUBLE,
 
             sitk.sitkVectorUInt8:   vtk.VTK_UNSIGNED_CHAR,  sitk.sitkVectorInt8:    vtk.VTK_CHAR,
             sitk.sitkVectorUInt16:  vtk.VTK_UNSIGNED_SHORT, sitk.sitkVectorInt16:   vtk.VTK_SHORT,
             sitk.sitkVectorUInt32:  vtk.VTK_UNSIGNED_INT,   sitk.sitkVectorInt32:   vtk.VTK_INT,
             sitk.sitkVectorUInt64:  vtk.VTK_UNSIGNED_LONG,  sitk.sitkVectorInt64:   vtk.VTK_LONG,
             sitk.sitkVectorFloat32: vtk.VTK_FLOAT,          sitk.sitkVectorFloat64: vtk.VTK_DOUBLE,
 
             sitk.sitkLabelUInt8:  vtk.VTK_UNSIGNED_CHAR,
             sitk.sitkLabelUInt16: vtk.VTK_UNSIGNED_SHORT,
             sitk.sitkLabelUInt32: vtk.VTK_UNSIGNED_INT,
             sitk.sitkLabelUInt64: vtk.VTK_UNSIGNED_LONG
            }


def sitk2vtk(img, outVol=None):
    size = list(img.GetSize())
    origin = list(img.GetOrigin())
    spacing = list(img.GetSpacing())
    sitktype = img.GetPixelID()
    vtktype = pixelmap[sitktype]
    ncomp = img.GetNumberOfComponentsPerPixel()

    # convert the SimpleITK image to a numpy array
    i2 = sitk.GetArrayFromImage(img)
    i2_string = i2.tostring()

    # send the numpy array to VTK with a vtkImageImport object
    dataImporter = vtk.vtkImageImport()

    dataImporter.CopyImportVoidPointer(i2_string, len(i2_string))

    dataImporter.SetDataScalarType(vtktype)

    dataImporter.SetNumberOfScalarComponents(ncomp)

    # VTK expects 3-dimensional parameters
    if len(size) == 2:
        size.append(1)

    if len(origin) == 2:
        origin.append(0.0)

    if len(spacing) == 2:
        spacing.append(spacing[0])

    # Set the new VTK image's parameters
    dataImporter.SetDataExtent(0, size[0]-1, 0, size[1]-1, 0, size[2]-1)
    dataImporter.SetWholeExtent(0, size[0]-1, 0, size[1]-1, 0, size[2]-1)

    dataImporter.SetDataOrigin(origin)
    dataImporter.SetDataSpacing(spacing)

    dataImporter.Update()

    vtk_image = dataImporter.GetOutput()

    # outVol and this DeepCopy are a work-around to avoid a crash on Windows
    if outVol is not None:
        outVol.DeepCopy(vtk_image)

    return vtk_image


def vtk2sitk(img):
    vtk_data = img.GetPointData().GetScalars()
    numpy_data = vtk_to_numpy(vtk_data)
    dims = img.GetDimensions()
    numpy_data = numpy_data.reshape(dims[2], dims[1], dims[0])
    numpy_data = numpy_data.transpose(2, 1, 0)

    sitk_image = sitk.GetImageFromArray(numpy_data)

    return sitk_image