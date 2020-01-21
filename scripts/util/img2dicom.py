#----------------------------------------------------- 
# img2dicom.py
#
# Created by:   Michael Kuczynski
# Created on:   21-01-2020
#
# Description: Converts between SimpleITK and VTK image types
#-----------------------------------------------------

import os
import time
import errno

import SimpleITK as sitk

def img2dicom(img, outDir):
    new_img = img
    spacingX, spacingY, spacingZ = img.GetSpacing()
    new_img.SetSpacing([spacingX, spacingY, spacingZ])

    modification_time = time.strftime("%H%M%S")
    modification_date = time.strftime("%Y%m%d")

    # Copy some of the tags and add the relevant tags indicating the change.
    # For the series instance UID (0020|000e), each of the components is a number, cannot start
    # with zero, and separated by a '.' We create a unique series ID using the date and time.
    # tags of interest:
    direction = new_img.GetDirection()
    series_tag_values = [("0008|0031",modification_time), # Series Time
                         ("0008|0021",modification_date), # Series Date
                         ("0008|0008","DERIVED\\SECONDARY"), # Image Type
                         ("0020|000e", "1.2.826.0.1.3680043.2.1125."+modification_date+".1"+modification_time), # Series Instance UID
                         ("0020|0037", '\\'.join(map(str, (direction[0], direction[3], direction[6],# Image Orientation (Patient)
                                                             direction[1],direction[4],direction[7])))),
                         ("0008|103e", "Created-SimpleITK")] # Series Description

    writer = sitk.ImageFileWriter()
    # Use the study/series/frame of reference information given in the meta-data
    # dictionary and not the automatically generated information from the file IO
    writer.KeepOriginalImageUIDOn()

    outPath = os.path.join(outDir, "dcm")

    try:
        os.mkdir(outPath)
    except OSError as e:
        if e.errno != errno.EEXIST:     # Directory already exists error
            raise

    for i in range(new_img.GetDepth()):
        image_slice = new_img[:,:,i]
        # Tags shared by the series.
        for tag, value in series_tag_values:
            image_slice.SetMetaData(tag, value)
        # Slice specific tags.
        image_slice.SetMetaData("0008|0012", time.strftime("%Y%m%d")) # Instance Creation Date
        image_slice.SetMetaData("0008|0013", time.strftime("%H%M%S")) # Instance Creation Time
        # Setting the type to CT preserves the slice location.
        image_slice.SetMetaData("0008|0060", "CT")  # set the type to CT so the thickness is carried over
        
        # (0020, 0032) image position patient determines the 3D spacing between slices.
        image_slice.SetMetaData("0020|0032", '\\'.join(map(str,new_img.TransformIndexToPhysicalPoint((0,0,i))))) # Image Position (Patient)
        image_slice.SetMetaData("0020,0013", str(i)) # Instance Number

        # Write to the output directory and add the extension dcm, to force writing in DICOM format.
        writer.SetFileName(os.path.join(outPath, "dcm" + str(i) + '.dcm'))
        writer.Execute(image_slice)