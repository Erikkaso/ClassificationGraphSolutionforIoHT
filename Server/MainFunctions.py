from Database.DBConnection import DBConnection
import DBInitialize
from DAO.Dao import DAO
from DAO.addVerticeEdgeLists import addSensorList, addFeatureList, addMLModelList, addFinalStateList, addMLAlgorithmList
from DAO.addVerticeEdgeLists import addSensorFeatureList, addFeatureMLModel, addMLModelFinalState
from DAO.Entities import Sensor, Feature, MLModel, FinalState, MLAlgorithm
from XMLCreate import xml_create
from MLModels.MLModels.Tensorflow.ANNTensorflow import trainModelWithACCGYR, trainModelWithOnlyACC
from MLModels.MLModels.SkLearn.DecisionTreeSkLearn import trainDecisionTreeModelAccGyr, trainDecisionTreeModelAcc
from MLModels.MLModels.SkLearn.RandomForestSKLearn import trainRandomForestModelAccGyr, trainRandomForestModelAcc
from MLModels.MLModels.SkLearn.SVMSKLearn import ModelTrainer
from graphFunctions import addToGraph, getGraphValues, optimizeGraph
from Datasets.DatasetManipulation.Preprocessing.DatasetACC_GYR import DatasetACC_GYR
from Datasets.DatasetManipulation.Preprocessing.DatasetACC import DatasetACC
from Datasets.DatasetManipulation.Format.Dataset1 import Dataset1
from Datasets.DatasetManipulation.Format.Dataset2 import Dataset2

import os
import platform
import time
from Utilitarios import Constants
pathBase = Constants.pathBase
pathDataset = Constants.pathProjectDataset

print("\n=======Verifica se já existe banco de dados e tabelas e cria conexão==========\n")

so = platform.system()
db = DBInitialize.DBInitialize()
dao = DAO(db.connection_db)

print("\n=======Conexão com banco salva==========\n")

print("=========Initialize Graph Generate Data===========")

algorithName = ["Artificial Neural Network"]
modelName = ["LastANNModelAll.tflite"]
modelName2 = ["LastANNModelACC.tflite"]

algorithName2 = ["Decision Tree"]
modelName3 = ["sklearn_model_dt.onnx"]
modelName4 = ["sklearn_model_dt2.onnx"]

algorithName3 = ["Random Forest"]
modelName5 = ["sklearn_model_rf.onnx"]
modelName6 = ["sklearn_model_rf2.onnx"]

algorithName4 = ["Support Vector Machines"]
modelName7 = ["acc_model.joblib"]
modelName8 = ["acc_gyr_model.joblib"]

sensorList = [["acc", "accelerometer"], ["gyr","gyroscope"]]
featureList = ["acc_mean", "acc_max", "acc_min", "acc_std", "acc_kurtosis", "acc_skewness", "acc_entropy", "acc_mad", "acc_iqr","gyr_mean", "gyr_max", "gyr_min", "gyr_std", "gyr_kurtosis", "gyr_skewness", "gyr_entropy", "gyr_mad", "gyr_iqr"]

sensorList2 = [["acc", "accelerometer"]]
featureList2 = ["acc_mean", "acc_max", "acc_min", "acc_std", "acc_kurtosis", "acc_skewness", "acc_entropy", "acc_mad", "acc_iqr"]

finalStateListACC = ['Walk', 'Hitting on a table', 'Hitting a wall', 'Running', 'Laying', 'Bumping the Wall', 'Writing', 'Clapping Standing', 'Clap Sitting', 'Jump', 'Fall Forward With Support', 'Fall Forward Without Support', 'Fall to the Sides', 'Sitting', 'Sitting With Support', 'Sitting Without Support', 'Grope', 'Brush_teeth', 'Climb_stairs', 'Comb_hair', 'Descend_stairs', 'Drink_glass', 'Eat_meat', 'Eat_soup', 'Getup_bed', 'Liedown_bed', 'Pour_water','Sitdown_chair', 'Standup_chair', 'Use_telephone']
finalStateListACCGYR = ['Walk', 'Hitting on a table', 'Hitting a wall', 'Running', 'Laying', 'Bumping the Wall', 'Writing', 'Clapping Standing', 'Clap Sitting', 'Jump', 'Fall Forward With Support', 'Fall Forward Without Support', 'Fall to the Sides', 'Sitting', 'Sitting With Support', 'Sitting Without Support', 'Grope']
    

dt1 = Dataset1(pathDataset+"\\Dataset1")
dt2 = Dataset2(pathDataset+"\\D2_ADL_Dataset\\HMP_Dataset\\All_data")


print("=========begin preprocessing===========")
start_time = time.perf_counter()
preprocessingData = DatasetACC_GYR([dt1]).executePreprocessing()
preprocessingDataACC = DatasetACC([dt1,dt2]).executePreprocessing()
end_time = time.perf_counter()
elapsed_time = end_time - start_time
print("==Total time processing:" + str(elapsed_time)+"==")
print("=========end preprocessing=========")



print("=========trainning===========")
start_time = time.perf_counter()

print("=========ANN ACC and GYR===========")
ANNModelACCGYR = trainModelWithACCGYR(0.7, 1, 2, preprocessingData)
print("=========ANN ACC===========")
ANNModelOnlyACC = trainModelWithOnlyACC(0.7, 1, 2, preprocessingDataACC)

print("=========Decision Tree ACC and GYR===========")
DTModelAllACCGYR = trainDecisionTreeModelAccGyr(0.75, 1, 2, preprocessingData)
print("=========Decision Tree ACC===========")
DTModelOnlyACC = trainDecisionTreeModelAcc(0.8, 1, 2, preprocessingDataACC)

print("=========Random Forest ACC and GYR===========")
RFModelAllACCGYR = trainRandomForestModelAccGyr(0.75, 1, 2, preprocessingData)
print("=========Random Forest ACC===========")
RFModelOnlyACC = trainRandomForestModelAcc(0.8, 1, 2, preprocessingDataACC)

print("=========SVM ACC and GYR===========")
modelTrainer = ModelTrainer()
SVMMODELACCGYR = modelTrainer.train_modelACCGYR(0.7,1,2,preprocessingData,finalStateListACCGYR)
print("=========SVM ACC ===========")
SVMMODELACC = modelTrainer.train_modelACC(0.7,1,2,preprocessingData,finalStateListACC)

end_time = time.perf_counter()
elapsed_time = end_time - start_time
print("==Total time trainig models:" + str(elapsed_time)+"==")
print("=========trainning===========")

print("=========Generate Graph===========")

#Add grafo
#Add Ann Model related Values with All Sensors
valuesList = getGraphValues(sensorList, featureList, algorithName, modelName, finalStateListACCGYR, ANNModelACCGYR)[1]
probability = valuesList[1]
valuesList = valuesList[0]
addToGraph(dao, valuesList, probability) 

#Add Ann Model related Values with only Accelerometer
valuesList2 = getGraphValues(sensorList2, featureList2, algorithName, modelName2, finalStateListACC, ANNModelOnlyACC)[1]
probability2 = valuesList2[1]
valuesList2 = valuesList2[0]
addToGraph(dao, valuesList2, probability2)


#Add Decision Tree Model related Values with All Sensors
valuesList = getGraphValues(sensorList, featureList, algorithName2, modelName3, finalStateListACCGYR, DTModelAllACCGYR)[1]
probability = valuesList[1]
valuesList = valuesList[0]
print(valuesList[1])
print(valuesList[0])
addToGraph(dao, valuesList, probability) 

#Add Decision Tree Model related Values with only Accelerometer
valuesList = getGraphValues(sensorList2, featureList2, algorithName2, modelName4, finalStateListACC, DTModelOnlyACC)[1]
probability = valuesList[1]
valuesList = valuesList[0]
print(valuesList[1])
print(valuesList[0])
addToGraph(dao, valuesList, probability) 

#Add Random Forest Model related Values with All Sensors
valuesList = getGraphValues(sensorList, featureList, algorithName3, modelName5, finalStateListACCGYR, RFModelAllACCGYR)[1]
probability = valuesList[1]
valuesList = valuesList[0]
addToGraph(dao, valuesList, probability) 

#Add Random Forest Model related Values with only Accelerometer
valuesList = getGraphValues(sensorList2, featureList2, algorithName3, modelName6, finalStateListACC, RFModelOnlyACC)[1]
probability = valuesList[1]
valuesList = valuesList[0]
addToGraph(dao, valuesList, probability)

#Add SVM related Values with All Sensors
valuesList = getGraphValues(sensorList, featureList, algorithName4, modelName7, finalStateListACCGYR, SVMMODELACCGYR)[1]
probability = valuesList[1]
valuesList = valuesList[0]
addToGraph(dao, valuesList, probability) 

#Add SVM related Values with only Accelerometer
valuesList = getGraphValues(sensorList2, featureList2, algorithName4, modelName8, finalStateListACC, SVMMODELACC)[1]
probability = valuesList[1]
valuesList = valuesList[0]
addToGraph(dao, valuesList, probability) 

'''
if so == "Windows":
    os.system('cls') or None
if so == "Linux":
    os.system('clear') or None
'''

print("\n=======Recupera dados do Banco e Cria o grafo==========\n")

addToGraph(dao, valuesList, probability)
addToGraph(dao, valuesList2, probability2)

print("\n=======Recupera as arestas e vértices para XML==========\n")

edges = dao.includeEdgeList()
edgeSensorFeatures = edges[0]
edgeFeatureModels = edges[1] 
edgeModelFinalStates = edges[2]

print("\n=======Cria Arquivo XML==========\n")

xml_create(edgeSensorFeatures, edgeFeatureModels, edgeModelFinalStates)


'''
print('======edgeSensorFeatures========')
for e in edgeSensorFeatures:
    print(e.Sensor.sensorName + ' - ' + e.Feature.featureName) 
#print(edgeSensorFeatures)

print('======edgeFeatureModels========')
for e in edgeFeatureModels:
    print(e.Feature.featureName + ' - ' + e.MLModel.titleModel + e.MLModel.modelExtension)

print('======edgeModelFinalStates========')
for e in edgeModelFinalStates:
    print(e.MLModel.titleModel + e.MLModel.modelExtension + ' - ' + e.FinalState.description)
'''


print('================================')
print('==========Grafo Otimizado=============')
print('================================')

#sensors = ['acc','gyr']
sensors = ['acc']
graphOptimized = optimizeGraph(dao,sensors, 0.50)
edgeSensorFeaturesO = graphOptimized[0]
edgeFeatureModelsO = graphOptimized[1] 
edgeModelFinalStatesO = graphOptimized[2]

print("\n=======Cria Arquivo XML do Grafo Otimizado==========\n")
xml_create(edgeSensorFeaturesO, edgeFeatureModelsO, edgeModelFinalStatesO, "KnowledgeBaseOptimized")

'''
print('======edgeSensorFeaturesO========')
for e in edgeSensorFeaturesO:
    print(e.Sensor.sensorName + ' - ' + e.Feature.featureName) 
#print(edgeSensorFeatures)

print('======edgeFeatureModelsO========')
for e in edgeFeatureModelsO:
    print(e.Feature.featureName + ' - ' + e.MLModel.titleModel + e.MLModel.modelExtension)
    print(str(e.MLModel.numInFeature) + ' - ' + str(e.MLModel.numOutFeature))

print('======edgeModelFinalStatesO========')
for e in edgeModelFinalStatesO:
    print(e.MLModel.titleModel + e.MLModel.modelExtension + ' - ' + e.FinalState.description)
    print(str(e.MLModel.numInFeature) + ' - ' + str(e.MLModel.numOutFeature) + ' - ' + str(e.probability))
'''
