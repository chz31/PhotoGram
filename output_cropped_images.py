volNodeName = 'cropped_volume' #Enter the name of the ROI cropped vector volume node
outputPath = 'C:/Users/czhan2/Desktop/photogrammetry_test/test_ROI_output' #Enter output path dir

import numpy
import os

volumeNode = slicer.util.getNode(volNodeName) 
volArrays = slicer.util.arrayFromVolume(volumeNode) 

originalVolumeIJKToRAS = numpy.diag([-1.0, -1.0, 1.0, 1.0])
spacingScale = numpy.array([1.0, 1.0, 1.0])
ijkToRAS = numpy.dot(originalVolumeIJKToRAS, numpy.diag([spacingScale[0], spacingScale[1], spacingScale[2], 1.0]))

ijkToRAS = slicer.util.vtkMatrixFromArray(ijkToRAS)

for i in range(volArrays.shape[0]):
  imageArr = volArrays[i, :, :, :]
  imageArr = numpy.flipud(imageArr)
  shape = imageArr.shape
  vtype = vtk.util.numpy_support.get_vtk_array_type(imageArr.dtype)
  channel_count = shape[2] #3 for vector array
  flat_img_array = imageArr.flatten()
  vtk_arr = vtk.util.numpy_support.numpy_to_vtk(num_array=flat_img_array, deep=True, array_type=vtype)
  vtk_arr.SetNumberOfComponents(channel_count)
  #build a vtkImageData object for the ith image array
  imgVTK = vtk.vtkImageData()
  imgVTK.SetDimensions(shape[1], shape[0], 1)
  imgVTK.AllocateScalars(vtk.VTK_UNSIGNED_CHAR, 3)
  imgVTK.GetPointData().SetScalars(vtk_arr)
  #write tiff images
  w_tiff = vtk.vtkTIFFWriter()
  w_tiff.SetInputData(imgVTK)
  outFileName = os.path.join(outputPath, '{0:04d}.tif'.format(i))
  w_tiff.SetFileName(outFileName)
  w_tiff.Write()

