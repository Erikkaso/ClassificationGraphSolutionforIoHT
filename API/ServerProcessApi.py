import json
import os
import requests
import platform

api_token = 'seu_api_token'

api_url_base = os.environ.get('API_URL_BASE', 'http://127.0.0.1:3000').rstrip('/')

headers = {'Content-Type': 'application/json',
           'Authorization': 'Bearer {0}'.format(api_token)}

def get_info(id=None):

    api_url_model = '{0}/UpdateGraphRequest/0'.format(api_url_base)
    api_url_model_generated = '{0}/UpdateGraphRequest/1'.format(api_url_base)
    api_url_model_generate = '{0}/UpdateGraphRequest/2'.format(api_url_base)
    api_url_optmize = '{0}/OptimizeGraphRequest/acc_gyr'.format(api_url_base)
    api_url_optmize_with_percentage = '{0}/OptimizeGraphRequest/acc/50'.format(api_url_base)
    api_url = '{0}//api/v1/resources/ngos'.format(api_url_base)
    
    try:
        if id == 0:
            response = requests.get(api_url_model, headers=headers, timeout=10)
        elif id == 3:
            response = requests.get(api_url_optmize, headers=headers, timeout=120)
        elif id == 1:
            response = requests.get(api_url_model_generated, headers=headers, timeout=10)
        elif id == 2:
            response = requests.get(api_url_model_generate, headers=headers, timeout=10)
        elif id == 4:
            response = requests.get(api_url_optmize_with_percentage, headers=headers, timeout=120)
        else:
            response = requests.get(api_url_base, headers=headers, timeout=10)
    except requests.RequestException as error:
        print(f'[!] API indisponível em {api_url_base}: {error}')
        return None

    if id == 0:
        print(api_url_model)
    elif id == 3:
        print(api_url_optmize)
    elif id == 1:
        print(api_url_model_generated)
    elif id == 2:
        print(api_url_model_generate)
    elif id == 4:
        print(api_url_optmize_with_percentage)
    else:
        print(api_url_base)
    if response.status_code == 200:
        return response.content.decode('utf-8')#json.loads(response.content.decode('utf-8'))
    else:
        return response.content.decode('utf-8')

def execute(id=None):
    info = get_info(id)
    if info is not None:
        print(info)
        if info == 'execute':
            #response = requests.post(api_url, headers=headers, json=ssh_key)
            #modeltree.generateTreeModels()
            '''
            print("Aqui estão suas informações: ")
            for c in account_info['ngos']:
                print('{0}'.format(c))
            '''
        elif info == 'graph_update':
            get_info(1) #limpa requisição
            updateGraph()
        elif info == 'graph_optimized':
            print('Optimized')
    else:
        print('[!] Solicitação inválida')


def updateGraph():
    from ModelANNTensorflow import trainModelWithACCGYR, trainModelWithOnlyACC
    from ModelDecisionTreeRandomForestSKLearn import trainDecisionTreeModelAccGyr, trainRandomForestModelAccGyr, trainDecisionTreeModelAcc, trainRandomForestModelAcc
    from Server.graphFunctions import addToGraph, getGraphValues, optimizeGraph
    from Server.Datasets.DatasetManipulation.Format.Dataset1 import Dataset1 
    from Server.Datasets.DatasetManipulation.Format.Dataset2 import Dataset2
    from Server.Datasets.DatasetManipulation.Preprocessing.DatasetACC import DatasetACC
    from Server.Datasets.DatasetManipulation.Preprocessing.DatasetACC_GYR import DatasetACC_GYR

    print("=========Initialize Graph Generate Data from Databases===========")

    algorithName = ["Artificial Neural Network"]
    modelName = ["ANNModel.tflite"]
    modelName2 = ["ANNModel2.tflite"]
    
    algorithName2 = ["Decision Tree"]
    modelName3 = ["sklearn_model_dt.onnx"]
    modelName4 = ["sklearn_model_dt2.onnx"]
    
    algorithName3 = ["Random Forest"]
    modelName5 = ["sklearn_model_rf.onnx"]
    modelName6 = ["sklearn_model_rf2.onnx"]
    
    sensorList = [["acc", "accelerometer"], ["gyr","gyroscope"]]
    featureList = ["acc_mean", "acc_max", "acc_min", "acc_std", "acc_kurtosis", "acc_skewness", "acc_entropy", "acc_mad", "acc_iqr","gyr_mean", "gyr_max", "gyr_min", "gyr_std", "gyr_kurtosis", "gyr_skewness", "gyr_entropy", "gyr_mad", "gyr_iqr"]
    
    sensorList2 = [["acc", "accelerometer"]]
    featureList2 = ["acc_mean", "acc_max", "acc_min", "acc_std", "acc_kurtosis", "acc_skewness", "acc_entropy", "acc_mad", "acc_iqr"]
    
    finalStateListACC = ['Walk', 'Hitting on a table', 'Hitting a wall', 'Running', 'Laying', 'Bumping the Wall', 'Writing', 'Clapping Standing', 'Clap Sitting', 'Jump', 'Fall Forward With Support', 'Fall Forward Without Support', 'Fall to the Sides', 'Sitting', 'Sitting With Support', 'Sitting Without Support', 'Grope', 'Brush_teeth', 'Climb_stairs', 'Comb_hair', 'Descend_stairs', 'Drink_glass', 'Eat_meat', 'Eat_soup', 'Getup_bed', 'Liedown_bed', 'Pour_water','Sitdown_chair', 'Standup_chair', 'Use_telephone']
    
    finalStateListACCGYR = ['Walk', 'Hitting on a table', 'Hitting a wall', 'Running', 'Laying', 'Bumping the Wall', 'Writing', 'Clapping Standing', 'Clap Sitting', 'Jump', 'Fall Forward With Support', 'Fall Forward Without Support', 'Fall to the Sides', 'Sitting', 'Sitting With Support', 'Sitting Without Support', 'Grope']
    
    
    ###########Preprocessing############
    dt1 = Dataset1("Datasets/Dataset1")
    dt2 = Dataset2("Datasets/D2_ADL_Dataset/HMP_Dataset/All_data")
    dtACC = DatasetACC([dt1,dt2])
    dtACCGYR = DatasetACC_GYR([dt1])
    ppDataACC = dtACC.executePreprocessing()
    ppDataACCGYR = dtACCGYR.executePreprocessing()
    ###########Trainnig###########
    print("----Training----")
    ANNModelACCGYR = trainModelWithACCGYR(0.75, 1, 10, ppDataACCGYR)
    ANNModelOnlyACC = trainModelWithOnlyACC(0.75, 1, 10, ppDataACC)
    DTModelAllACCGYR = trainDecisionTreeModelAccGyr(0.75, 10, 1000, ppDataACCGYR)
    DTModelOnlyACC = trainDecisionTreeModelAcc(0.8, 1, 10, ppDataACC)
    RFModelAllACCGYR = trainRandomForestModelAccGyr(0.75, 10, 1000, ppDataACCGYR)
    RFModelOnlyACC = trainRandomForestModelAcc(0.8, 1, 10, ppDataACC)


    print("=========Generate Graph===========")
    
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
    
    print("\n=================\n")

def graphXMLGenerate(sensorslist, percentage):
    #for i in range(2,50):
    #    dao.delete("SensorFeature",i)
    edges = dao.includeEdgeList()
    edgeSensorFeatures = edges[0]
    edgeFeatureModels = edges[1] 
    edgeModelFinalStates = edges[2]
    xml_create(edgeSensorFeatures, edgeFeatureModels, edgeModelFinalStates)
    
    sensors = sensorslist.split("_")
    graphOptimized = gF.optimizeGraph(dao,sensors,int(percentage)/100)
    edgeSensorFeaturesO = graphOptimized[0]
    edgeFeatureModelsO = graphOptimized[1] 
    edgeModelFinalStatesO = graphOptimized[2]
    print("teste2")
    xml_create(edgeSensorFeaturesO, edgeFeatureModelsO, edgeModelFinalStatesO, "KnowledgeBaseOptimized2")

#====Teste====
#execute()
if __name__ == "__main__":
    from DBConnection import DBConnection
    from DBInitialize import DBInitialize
    from Server.Dao import DAO
    from Server.addVerticeEdgeLists import addSensorList, addFeatureList, addMLModelList, addFinalStateList, addMLAlgorithmList
    from Server.addVerticeEdgeLists import addSensorFeatureList, addFeatureMLModel, addMLModelFinalState
    from Server.Entities.Entities import Sensor, Feature, MLModel, FinalState, MLAlgorithm
    from XMLCreate import xml_create
    import Server.graphFunctions as gF
    
    #execute(2) #UpdateGraphRequest
    #execute(0) #UpdateGraphRequest Execute
    
    so = platform.system()
    db = DBInitialize()
    dao = DAO(db.connection_db)
    
    ##OptimizeGraphRequest
    #updateGraph()
    graphXMLGenerate("acc_gyr", 50)
    file = open("download.xml", "w")
    file.write(get_info(3))
    file.close()
    print("optimized")
    file = open("download_.xml", "w")
    file.write(get_info(4))
    file.close()
    print("optimized2")
    
