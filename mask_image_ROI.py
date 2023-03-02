"""
import os
filePath = "C:/Users/czhan2/OneDrive/Mouse_Skulls/R_test/photogrammetry/mask_image_ROI.py"
#
specimenID = "beaver_0"
#
setName = "horizontal_gcp"
volNodeName = 'DSC_0291_gcp'
rootPath = os.path.join("C:/Users/czhan2/Pictures/digiCamControl/Session1/beavers_burke", specimenID)
inputPath = os.path.join(rootPath, setName)
maskedDir = setName + "_masked"
croppedDir = setName + "_cropped"
outputPath_masked = os.path.join(rootPath, maskedDir)
outputPath_cropped = os.path.join(rootPath, croppedDir)

if not os.path.exists(outputPath_masked):
  os.makedirs(outputPath_masked)

if not os.path.exists(outputPath_cropped):
  os.makedirs(outputPath_cropped)

exec(open(filePath).read())
"""

import math
# import SimpleITK as sitk
import numpy as np
# import os

volumeNode = slicer.util.getNode(volNodeName) 
volArrays = slicer.util.arrayFromVolume(volumeNode) 

# ijkToRAS = slicer.util.vtkMatrixFromArray(ijkToRAS)
# 
# reader = sitk.ImageFileReader()
# reader.SetFileName("C:/Users/czhan2/Pictures/digiCamControl/Session1/beavers_burke/beaver_1_34050/horizontal_4/DSC_0740.jpg")
# image = reader.Execute()
# 
# sliceArray = sitk.GetArrayFromImage(image)

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
outputROINode = slicer.util.getNode("Crop Volume ROI") 
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

# originRAS = np.dot(ijkToRAS, [extent[0], extent[2], extent[4], 1.0])[0:3]
# ijkToRAS[0:3,3] = originRAS

# shape = [extent[5]-extent[4]+1, extent[3]-extent[2]+1, extent[1]-extent[0]+1]


# extent = [1470, 3403, 1421, 2185, 0, 63]

# inputPath = "C:/Users/czhan2/Pictures/digiCamControl/Session1/beavers_burke/82710/vertical_9"
# inputPath = "C:/Users/czhan2/Pictures/digiCamControl/Session1/beaver_0/64pics_setting/horizontal_up_mid"

fileNamesExt = os.listdir(inputPath)
fileNames = [os.path.splitext(fileName)[0] for fileName in fileNamesExt]

# outputPath_masked = 'C:/Users/czhan2/Pictures/digiCamControl/Session1//beavers_burke/82710/vertical_9_masked' #Enter output path dir
# outputPath = 'C:/Users/czhan2/Pictures/digiCamControl/Session1/beaver_0/64pics_setting/horizontal_up_mid_cropped2' #Enter output path dir

# outputPath_cropped = 'C:/Users/czhan2/Pictures/digiCamControl/Session1//beavers_burke/82710/vertical_9_cropped' #Enter output path dir


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
  #cropped image
  imageArr_cropped = imageArr_cropped[(imageArr.shape[0]-extent[3]+1):(imageArr.shape[0]-extent[2]), 
                     extent[0]:(extent[1]+1), :] 
  shape_cropped = imageArr_cropped.shape
  #
  flat_img_array_cropped = imageArr_cropped.flatten()
  vtk_arr_cropped = vtk.util.numpy_support.numpy_to_vtk(num_array=flat_img_array_cropped, deep=True, array_type=vtype)
  vtk_arr_cropped.SetNumberOfComponents(channel_count)
  #build a vtkImageData object for the ith image array
  imgVTK = vtk.vtkImageData()
  imgVTK.SetDimensions(shape_cropped[1], shape_cropped[0], 1)
  imgVTK.AllocateScalars(vtk.VTK_UNSIGNED_CHAR, 3)
  imgVTK.GetPointData().SetScalars(vtk_arr_cropped)
  #w
  #write cropped image
  w_jpeg_cropped = vtk.vtkJPEGWriter()
  w_jpeg_cropped.SetInputData(imgVTK)
  outFileName_cropped = os.path.join(outputPath_cropped, fileNamesExt[i])
  w_jpeg_cropped.SetFileName(outFileName_cropped)
  w_jpeg_cropped.Write()  


