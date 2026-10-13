# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np 
import scipy
from six.moves import urllib
from scipy import stats ##statistic functions
from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType
import subprocess
import os
import platform
import tensorflow as tf
from tensorflow import keras
from os.path import join
from pathlib import Path
from Utilitarios import Constants
pathProjectSaveModels = Constants.pathProjectSaveModels

#####################################################################################################################

def trainRandomForestModelAccGyr(threshold, testMin, testMax, preprocessingData):
    
    print("===ACC Random Forest===")
    
    labelTrain, labelTest, MyNewDataSetTrain, MyNewDataSetTest = preprocessingData
    
    from sklearn.ensemble import RandomForestClassifier
    from sklearn import tree
    X, y = MyNewDataSetTrain, labelTrain
    
    cont = 0
    valueAccuracy = 0
    resultModel = None
    while cont < testMin or (valueAccuracy < threshold and cont < testMax):
        clf = RandomForestClassifier(max_depth=11, random_state=0)
        clf = clf.fit(X, y)

        result = []
        for mndst in  MyNewDataSetTest:
          result.append(clf.predict([mndst]))

        qtd = 0
        for i in range(len(labelTest)):
          if result[i] == labelTest[i]:
            qtd += 1
            
        if valueAccuracy < qtd/len(labelTest):
            valueAccuracy = qtd/len(labelTest)
            resultModel = clf
        cont+=1
    
    print(round(valueAccuracy,2))

    print("==== Random Forest Model Save ====")
    # Specify an initial type for the model ( similar to input shape for the model )
    initial_type = [ 
        ( 'input_study_hours' , FloatTensorType( [None,1] ) ) 
    ]

    ##pip install -q tflite_support
    
    '''
    ##**Transfort to Tensorflow lite model**
    # 2. Reimplement in Keras
    saved_model = keras.Sequential([
    keras.layers.Input(shape=(1,)),
    keras.layers.Dense(units=1)  # Equivalent to linear regression
    ])

    # Transfer weights from sklearn to Keras (if applicable and compatible)
    saved_model.layers[0].set_weights([resultModel.coef_.reshape(1,1), sklearn_model.intercept_])

    #saved_model = convert_sklearn( resultModel , initial_types=initial_type )
    pathModel = Constants.pathProjectSaveModels+ "\\RadomForest\\"

    _TFLITE_MODEL_PATH = pathModel+"sklearn_model_rf.tflite"

    converter = tf.lite.TFLiteConverter.from_saved_model(saved_model)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    tflite_model = converter.convert()


    with open(_TFLITE_MODEL_PATH, 'wb') as f:
      f.write(tflite_model)

    PATH_DIR = Path.cwd()
    dataset_dir = PATH_DIR.joinpath(pathModel)
    tflite_model_file = dataset_dir.joinpath("sklearn_model_rf.tflite"+'32')
    tflite_model_file.write_bytes(tflite_model)

    converter = tf.lite.TFLiteConverter.from_saved_model(saved_model)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    converter.target_spec.supported_types = [tf.float16]
    tflite_model = converter.convert()

    PATH_DIR = Path.cwd()
    dataset_dir = PATH_DIR.joinpath(pathModel)
    tflite_model_file = dataset_dir.joinpath("sklearn_model_rf.tflite"+'16')
    tflite_model_file.write_bytes(tflite_model)

    '''
    # Write the ONNX model to disk
    converted_model = convert_sklearn( resultModel , initial_types=initial_type )
    with open( "sklearn_model_rf.onnx", "wb" ) as f:
        f.write( converted_model.SerializeToString() )

    
    cmd = ['python', '-m', 'onnxruntime.tools.convert_onnx_models_to_ort', 'sklearn_model_rf.onnx']
    shell_cmd = subprocess.run((cmd), capture_output=True, text=True)
    command_output=(shell_cmd.stdout)
    
    so = platform.system()
    if so == "Windows":
        os.system('copy sklearn_model_rf.onnx '+pathProjectSaveModels+'\\RandomForest')
        os.system('del sklearn_model_rf.onnx')
        os.system('copy sklearn_model_rf.ort '+pathProjectSaveModels+'\\RandomForest')
        os.system('del sklearn_model_rf.ort')
    if so == "Linux":
        os.system('mv sklearn_model_rf.onnx '+pathProjectSaveModels+'\\RandomForest')
        
    return [resultModel,valueAccuracy]

def trainRandomForestModelAcc(threshold, testMin, testMax, preprocessingData):
    
    print("===ACC Random Forest===")
    
    labelTrain, labelTest, MyNewDataSetTrain, MyNewDataSetTest = preprocessingData
    
    from sklearn.ensemble import RandomForestClassifier
    from sklearn import tree
    X, y = MyNewDataSetTrain, labelTrain
    
    cont = 0
    valueAccuracy = 0
    resultModel = None
    while cont < testMin or (valueAccuracy < threshold and cont < testMax):
        clf = RandomForestClassifier(max_depth=11, random_state=0)
        clf = clf.fit(X, y)

        result = []
        for mndst in  MyNewDataSetTest:
          result.append(clf.predict([mndst]))

        qtd = 0
        for i in range(len(labelTest)):
          if result[i] == labelTest[i]:
            qtd += 1
            
        if valueAccuracy < qtd/len(labelTest):
            valueAccuracy = qtd/len(labelTest)
            resultModel = clf
        cont+=1
    
    print(round(valueAccuracy,2))

    print("==== Random Forest Model Save ====")
    # Specify an initial type for the model ( similar to input shape for the model )
    initial_type = [ 
        ( 'input_study_hours' , FloatTensorType( [None,1] ) ) 
    ]
    '''
    saved_model = convert_sklearn( resultModel , initial_types=initial_type )
    pathModel = Constants.pathProjectSaveModels+ "\\RadomForest\\"

    _TFLITE_MODEL_PATH = pathModel+"sklearn_model_rf2.tflite"

    converter = tf.lite.TFLiteConverter.from_saved_model(saved_model)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    tflite_model = converter.convert()


    with open(_TFLITE_MODEL_PATH, 'wb') as f:
      f.write(tflite_model)

    PATH_DIR = Path.cwd()
    dataset_dir = PATH_DIR.joinpath(pathModel)
    tflite_model_file = dataset_dir.joinpath("sklearn_model_rf2.tflite"+'32')
    tflite_model_file.write_bytes(tflite_model)

    converter = tf.lite.TFLiteConverter.from_saved_model(saved_model)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    converter.target_spec.supported_types = [tf.float16]
    tflite_model = converter.convert()

    PATH_DIR = Path.cwd()
    dataset_dir = PATH_DIR.joinpath(pathModel)
    tflite_model_file = dataset_dir.joinpath("sklearn_model_rf2.tflite"+'16')
    tflite_model_file.write_bytes(tflite_model)

    '''

    # Write the ONNX model to disk
    converted_model = convert_sklearn( resultModel , initial_types=initial_type )
    with open( "sklearn_model_rf2.onnx", "wb" ) as f:
        f.write( converted_model.SerializeToString() )

    
    cmd = ['python', '-m', 'onnxruntime.tools.convert_onnx_models_to_ort', 'sklearn_model_rf2.onnx']
    shell_cmd = subprocess.run((cmd), capture_output=True, text=True)
    command_output=(shell_cmd.stdout)
    
    so = platform.system()
    if so == "Windows":
        os.system('copy sklearn_model_rf2.onnx '+pathProjectSaveModels+'\\RandomForest')
        os.system('del sklearn_model_rf2.onnx')
        os.system('copy sklearn_model_rf2.ort '+pathProjectSaveModels+'\\RandomForest')
        os.system('del sklearn_model_rf2.ort')
    if so == "Linux":
        os.system('mv sklearn_model_rf2.onnx '+pathProjectSaveModels+'\\RandomForest')
    
    return [resultModel,valueAccuracy]