"""
import os
filePath = "directory/to/mask_image_ROI.py"
#
rootPath = "directory/to/the/folder/for/all/photos/of/a/specimen" #the full directory that contains all photos of a specimen
setName = "vertical_1" #the folder name that contains a particular photo set under the "rootPath"
volNodeName = 'photo_volumetric_node_name' #the imported volumetric node name
ROI_name = "Crop Volume ROI"

inputPath = os.path.join(rootPath, setName)
maskedDir = setName + "_masked"
outputPath_masked = os.path.join(rootPath, maskedDir)

if not os.path.exists(outputPath_masked):
  os.makedirs(outputPath_masked)

exec(open(filePath).read())
"""

import math
# import SimpleITK as sitk
import numpy as np
# import os

volumeNode = slicer.util.getNode(volNodeName) 
volArrays = slicer.util.arrayFromVolume(volumeNode) 


imageArr_0 = volArrays[0, :, :, :]
originalVolumeDimensions = [imageArr_0.shape[1], imageArr_0.shape[0], 64]
originalVolumeNumberOfScalarComponents = imageArr_0.shape[2]  #scalar = 3
originalVolumeVoxelDataType = np.dtype(imageArr_0.dtype)
originalVolumeIJKToRAS = np.diag([-1.0, -1.0, 1.0, 1.0])


fullExtent = [0, 0, 0, 0, 0, 0]
spacingScale = np.array([1.0, 1.0, 1.0])
for i in range(3):
  fullExtent[i*2+1] = int(math.floor(originalVolumeDimensions[i]/spacingScale[i])) - 1


ijkToRAS = np.dot(originalVolumeIJKToRAS, np.diag([spacingScale[0], spacingScale[1], spacingScale[2], 1.0]))
rasToIJK = np.linalg.inv(ijkToRAS)


#Get ROI bound
outputROINode = slicer.util.getNode(ROI_name) 
outputBounds = None
center = [0.0, 0.0, 0.0]
radius = [0.0, 0.0, 0.0]
outputROINode.GetXYZ(center)
outputROINode.GetRadiusXYZ(radius)
outputBounds = [
  center[0]-radius[0], center[0]+radius[0],
  center[1]-radius[1], center[1]+radius[1],
  center[2]-radius[2], center[2]+radius[2]
  ]
outputVolumeBounds = outputBounds


extentIJK = vtk.vtkBoundingBox()
for cornerR in [outputVolumeBounds[0], outputVolumeBounds[1]]:
  for cornerA in [outputVolumeBounds[2], outputVolumeBounds[3]]:
    for cornerS in [outputVolumeBounds[4], outputVolumeBounds[5]]:
      cornerIJK = np.dot(rasToIJK, [cornerR, cornerA, cornerS, 1.0])[0:3]
      extentIJK.AddPoint(cornerIJK)


extent = [0,0,0,0,0,0]
for i in range(3):
  extent[i*2] = int(math.floor(extentIJK.GetBound(i*2)-0.5))
  if extent[i*2] < fullExtent[i*2]:
    extent[i*2] = fullExtent[i*2]
  extent[i*2+1] = int(math.ceil(extentIJK.GetBound(i*2+1)+0.5))


fileNamesExt = os.listdir(inputPath)
fileNames = [os.path.splitext(fileName)[0] for fileName in fileNamesExt]



for i in range(volArrays.shape[0]):
  #masked_img
  imageArr = volArrays[i, :, :, :]
  imageArr_masked = np.copy(imageArr)
  imageArr_masked = np.flipud(imageArr_masked)
  shape = imageArr_masked.shape
  imageArr_cropped = np.copy(imageArr_masked)
  #masking image
  imageArr_masked[:(imageArr.shape[0]-extent[3]+1), :, :] = [0, 0, 0]
  imageArr_masked[:, :extent[0], :] = [0, 0, 0]
  imageArr_masked[(imageArr.shape[0]-extent[2]):, :, :] = [0, 0, 0]
  imageArr_masked[:, (extent[1]+1):, :] = [0, 0, 0]
  #
  vtype = vtk.util.numpy_support.get_vtk_array_type(imageArr_masked.dtype)
  channel_count = shape[2] #3 for vector array
  flat_img_array = imageArr_masked.flatten()
  vtk_arr = vtk.util.numpy_support.numpy_to_vtk(num_array=flat_img_array, deep=True, array_type=vtype)
  vtk_arr.SetNumberOfComponents(channel_count)
  #build a vtkImageData object for the ith image array
  imgVTK = vtk.vtkImageData()
  imgVTK.SetDimensions(shape[1], shape[0], 1)
  imgVTK.AllocateScalars(vtk.VTK_UNSIGNED_CHAR, 3)
  imgVTK.GetPointData().SetScalars(vtk_arr)
  #write masked image
  w_jpeg_masked = vtk.vtkJPEGWriter()
  w_jpeg_masked.SetInputData(imgVTK)
  outFileName_masked = os.path.join(outputPath_masked, fileNamesExt[i])
  w_jpeg_masked.SetFileName(outFileName_masked)
  w_jpeg_masked.Write()
  #
  #


