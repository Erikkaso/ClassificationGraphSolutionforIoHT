from flask import Flask, jsonify, send_file, send_from_directory
from Server.DAO.Dao import DAO
from Server.Database.DBConnection import DBConnection
from Server.DBInitialize import DBInitialize
from Server.XMLCreate import xml_create
import Server.graphFunctions as gF
import os

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['UPLOAD_FOLDER'] = "saved_model"
db = DBInitialize()
dao = DAO(db.connection_db)
modelText = ""

@app.route('/')
def index():
    return 'execute'

@app.route('/UpdateGraphRequest/<id>')
def updateGraphRequest(id=None):
    global modelText
    print(id)
    if id == '0': #UpdateGraphRequest execute
        return modelText
    if id == '1': #UpdateGraphRequest clean
        modelText = ''
        return modelText
    if id == '2': #UpdateGraphRequest
        modelText = 'graph_update'
        return modelText
    else:
        return 'wrong'

@app.route('/OptimizeGraphRequest/<sensors>')
def optimizeGraphRequest(sensors):
    global modelText
    print(id)
    sensors = sensors.split("_")
    graphOptimized = gF.optimizeGraph(dao,sensors)
    edgeSensorFeaturesO = graphOptimized[0]
    edgeFeatureModelsO = graphOptimized[1] 
    edgeModelFinalStatesO = graphOptimized[2]
    xml_create(edgeSensorFeaturesO, edgeFeatureModelsO, edgeModelFinalStatesO, "KnowledgeBaseOptimized")
    return downloadOptimizeGraph()

@app.route('/OptimizeGraphRequest/<sensors>/<percentage>')
def optimizeGraphRequestPercentage(sensors,percentage):
    global modelText
    print(id)
    sensors = sensors.split("_")
    graphOptimized = gF.optimizeGraph(dao,sensors,int(percentage)/100)
    edgeSensorFeaturesO = graphOptimized[0]
    edgeFeatureModelsO = graphOptimized[1] 
    edgeModelFinalStatesO = graphOptimized[2]
    xml_create(edgeSensorFeaturesO, edgeFeatureModelsO, edgeModelFinalStatesO, "KnowledgeBaseOptimized")
    return downloadOptimizeGraph()

@app.route('/OptimizeGraphRequest/download.xml')
def downloadOptimizeGraph():
    import platform
    so = platform.system()
    if so == "Windows":
        return  send_file("download\\KnowledgeBaseOptimized.xml", as_attachment=True)
    if so == "Linux":
        return  send_file("download//KnowledgeBaseOptimized.xml", as_attachment=True)
    
@app.route('/GraphRequest')
def downloadGraph():
    import platform
    so = platform.system()
    if so == "Windows":
        return  send_file("download\\KnowledgeBase.xml", as_attachment=True)
    if so == "Linux":
        return  send_file("download//KnowledgeBase.xml", as_attachment=True)

@app.route('/saved_model/<path:filename>', methods=['GET', 'POST'])
def download(filename):
    uploads = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])
    return send_from_directory(directory=uploads, path=filename)


app.run()