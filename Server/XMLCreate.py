import shutil
import sys
import os
from bs4 import BeautifulSoup
from Utilitarios import Constants 


def xml_create(edgeSensorFeature, edgeFeaturesModel, edgeModelsFinalStatus, fileName = Constants.graphName):
    #====================Arquivo===============
    feedFileName = fileName
    path = Constants.pathProjectDownloads
    feedFile = path+"\\"+feedFileName+".xml"
    
    #====================Montar XML============
    ##====================Cabeçalho===============
    xml = '<KnowledgeRepresentation>\n'
    
    ##===================Itens================
    ##===================edgeSensorFeature=============
    xml= xml +  '<edgeSensorFeature>\n'
    for esf in edgeSensorFeature:
        #Inicio item
        xml= xml +  '<EdgeSensorFeature>\n'
        #Sensor
        xml= xml +  '<vSensor>\n'
        xml= xml +  '<typeSensor>'+esf.Sensor.typeSensor.upper()+'</typeSensor>\n'
        xml= xml +  '</vSensor>\n'
        #Feature
        xml= xml +  '<vFeature>\n'
        xml= xml +  '<feature></feature>\n'
        xml= xml +  '<featureName>\n'
        xml= xml +  '<idSensor>'+esf.Feature.featureName.split('_')[0].upper()+'</idSensor>\n'
        xml= xml +  '<name>'+esf.Feature.featureName.split('_')[1]+'</name>\n'
        xml= xml +  '</featureName>\n'
        xml= xml +  '</vFeature>\n'
        #Fim item
        xml= xml +  '</EdgeSensorFeature>\n'
    xml= xml +  '</edgeSensorFeature>\n'
    
    ##===================edgeFeaturesModel=============
    xml= xml +  '<edgeFeaturesModel>\n'
    for efm in edgeFeaturesModel:
        #Inicio item
        xml= xml +  '<EdgeFeatureModel>\n'
        #Feature
        xml= xml +  '<vFeature>\n'
        xml= xml +  '<feature></feature>\n'
        xml= xml +  '<featureName>\n'
        xml= xml +  '<idSensor>'+efm.Feature.featureName.split('_')[0].upper()+'</idSensor>\n'
        xml= xml +  '<name>'+efm.Feature.featureName.split('_')[1]+'</name>\n'
        xml= xml +  '</featureName>\n'
        xml= xml +  '</vFeature>\n'
        #Model
        xml= xml +  '<vModel>\n'
        xml= xml +  '<inFeature>'+str(efm.MLModel.numInFeature)+'</inFeature>\n'
        xml= xml +  '<modelName>'+efm.MLModel.titleModel+efm.MLModel.modelExtension+'</modelName>\n'
        xml= xml +  '<outFeature>'+str(efm.MLModel.numOutFeature)+'</outFeature>\n'
        xml= xml +  '</vModel>\n'
        #Fim item
        xml= xml +  '</EdgeFeatureModel>\n'
    xml= xml +  '</edgeFeaturesModel>\n'
    
    ##===================edgeModelsFinalStatus=============
    xml= xml +  '<edgeModelsFinalStatus>\n'
    for emf in edgeModelsFinalStatus:
        #Inicio item
        xml= xml +  '<EdgeModelsFinalStatus>\n'
        #Model
        xml= xml +  '<vModel>\n'
        xml= xml +  '<inFeature>'+str(emf.MLModel.numInFeature)+'</inFeature>\n'
        xml= xml +  '<modelName>'+emf.MLModel.titleModel+emf.MLModel.modelExtension+'</modelName>\n'
        xml= xml +  '<outFeature>'+str(emf.MLModel.numOutFeature)+'</outFeature>\n'
        xml= xml +  '</vModel>\n'
        #FinalState
        xml= xml +  '<vFinalStatus>\n'
        xml= xml +  '<finalStatus>'+emf.FinalState.description+'</finalStatus>\n'
        xml= xml +  '</vFinalStatus>\n'
        #Probabilitys
        xml= xml +  '<probability>'+str(emf.probability)+'</probability>\n'
        #Fim item
        xml= xml +  '</EdgeModelsFinalStatus>\n'
    xml= xml +  '</edgeModelsFinalStatus>\n'
    
    ##===============Fechamento===============
    xml = xml + '</KnowledgeRepresentation>'


    #====================Gravar XML============
    with open(feedFile, 'w', encoding="utf-8") as f2: 
        f2.write(xml)
    f2.close()
    #print(xml)
    return feedFile