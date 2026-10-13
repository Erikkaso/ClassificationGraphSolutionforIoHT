import sys
from pathlib import Path

from flask import Flask, send_file, send_from_directory


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SERVER_ROOT = PROJECT_ROOT / "Server"
DOWNLOAD_ROOT = PROJECT_ROOT / "download"
MODEL_ROOT = SERVER_ROOT / "MLModels" / "saved_models"
if str(SERVER_ROOT) not in sys.path:
    sys.path.insert(0, str(SERVER_ROOT))

from Server.DAO.Dao import DAO
from Server.DBInitialize import DBInitialize
from Server.XMLCreate import xml_create
import Server.graphFunctions as gF

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['UPLOAD_FOLDER'] = str(MODEL_ROOT)
db = None
dao = None
modelText = ""


def get_dao():
    global db, dao
    if dao is None:
        db = DBInitialize()
        dao = DAO(db.connection_db)
    return dao

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
    graphOptimized = gF.optimizeGraph(get_dao(),sensors)
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
    graphOptimized = gF.optimizeGraph(get_dao(),sensors,int(percentage)/100)
    edgeSensorFeaturesO = graphOptimized[0]
    edgeFeatureModelsO = graphOptimized[1] 
    edgeModelFinalStatesO = graphOptimized[2]
    xml_create(edgeSensorFeaturesO, edgeFeatureModelsO, edgeModelFinalStatesO, "KnowledgeBaseOptimized")
    return downloadOptimizeGraph()

@app.route('/OptimizeGraphRequest/download.xml')
def downloadOptimizeGraph():
    return send_file(DOWNLOAD_ROOT / "KnowledgeBaseOptimized.xml", as_attachment=True)
    
@app.route('/GraphRequest')
def downloadGraph():
    return send_file(DOWNLOAD_ROOT / "KnowledgeBase.xml", as_attachment=True)

@app.route('/saved_model/<path:filename>', methods=['GET', 'POST'])
def download(filename):
    return send_from_directory(
        directory=app.config['UPLOAD_FOLDER'],
        path=filename,
        as_attachment=True,
    )


if __name__ == "__main__":
    app.run(port=3000)
