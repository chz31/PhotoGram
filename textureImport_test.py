"""
filePath = "C:/Users/czhan2/Downloads/textureImport_test.py"
#
#specify the directory of the obj file
obj_path = "C:/Users/czhan2/Downloads/test_beaver-textured_model/odm_textured_model_geo.obj"

exec(open(filePath).read())
"""

import os
import unittest
import math
import numpy
import vtk, qt, ctk, slicer
import SimpleITK as sitk
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin
import logging


#Detect file extension as obj

obj_dir = os.path.dirname(obj_path)
obj_filename = os.path.basename(obj_path)
base_name = os.path.splitext(obj_filename)[0]
extension = os.path.splitext(obj_filename)[1]

#Add model node
obj_node = slicer.util.loadModel(obj_path)

#Meanwhie, if the model node ends in obj, search and map texture to it
if extension == ".obj":
  mtl_filename = base_name + ".mtl"
  mtl_path = os.path.join(obj_dir, mtl_filename)
  
  #parse the mtl file to look for texture image file name
  if os.path.exists(mtl_path):
    with open(mtl_path) as f:
      lines = f.read().splitlines() 
  
  texture_filename = lines[len(lines)-1].split(" ")[1]
  texture_path = os.path.join(obj_dir, texture_filename)

  import ImageStacks
  logic = ImageStacks.ImageStacksLogic()
  vectorVolNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLVectorVolumeNode")
  # logic._init_
  logic.outputQuality = 'full'
  logic.outputGrayscale = False
  logic.filePaths = [texture_path]
  logic.loadVolume(outputNode=vectorVolNode, progressCallback = None)
  
  
  import TextureModel
  textureModelLogic = TextureModel.TextureModelLogic()
  textureModelLogic.applyTexture(obj_node, vectorVolNode, None)
  
  slicer.mrmlScene.RemoveNode(vectorVolNode)
    


