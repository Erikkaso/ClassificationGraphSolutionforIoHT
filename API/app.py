import sys
import json
from pathlib import Path
from xml.parsers.expat import ExpatError

from flask import Flask, jsonify, request, send_file, send_from_directory
from API.converter import parse_xml


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
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
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


@app.route('/convert', methods=['POST'])
def convert_endpoint():
    file = request.files.get('file')
    if file is None:
        return jsonify(error='Nenhum arquivo enviado.'), 400
    if not (file.filename or '').lower().endswith('.xml'):
        return jsonify(error='O arquivo precisa ser XML.'), 400
    try:
        data = parse_xml(file.read().decode('utf-8-sig'))
    except (UnicodeDecodeError, ExpatError):
        return jsonify(error='Arquivo XML invalido ou fora da codificacao UTF-8.'), 400
    return jsonify(json_content=json.dumps(data, ensure_ascii=False))


def graph_response(path, prefer_json=False):
    path = Path(path)
    if request.args.get('format') == 'json' and prefer_json and path.with_suffix('.json').is_file():
        try:
            data = json.loads(path.with_suffix('.json').read_text(encoding='utf-8-sig'))
        except (UnicodeDecodeError, json.JSONDecodeError):
            return jsonify(error='O grafo salvo contem JSON invalido.'), 422
        return jsonify(data)
    if not path.is_file():
        return jsonify(error='Grafo ainda nao disponivel.'), 404
    if request.args.get('format') == 'json':
        try:
            data = parse_xml(path.read_text(encoding='utf-8-sig'))
        except (UnicodeDecodeError, ExpatError):
            return jsonify(error='O grafo salvo contem XML invalido.'), 422
        return jsonify(data)
    return send_file(path, as_attachment=True)


@app.route('/saved_models')
def list_models():
    extensions = {'.tflite', '.tflite16', '.tflite32', '.onnx', '.joblib'}
    models = sorted(
        path.relative_to(MODEL_ROOT).as_posix()
        for path in MODEL_ROOT.rglob('*')
        if path.is_file() and path.suffix.lower() in extensions
    )
    return jsonify(models=models)

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
    return optimized_graph_response(sensors)

@app.route('/OptimizeGraphRequest/<sensors>/<percentage>')
def optimizeGraphRequestPercentage(sensors,percentage):
    try:
        percentage = int(percentage)
    except ValueError:
        return jsonify(error='Informe uma porcentagem inteira de 0 a 100.'), 400
    if not 0 <= percentage <= 100:
        return jsonify(error='Informe uma porcentagem inteira de 0 a 100.'), 400
    return optimized_graph_response(sensors, percentage / 100)


def optimized_graph_response(sensors, probability=0):
    try:
        edges = gF.optimizeGraph(get_dao(), sensors.lower().split('_'), probability)
        path = xml_create(*edges, 'KnowledgeBaseOptimized')
    except Exception:
        app.logger.exception('Falha ao otimizar o grafo')
        return jsonify(error='Falha ao otimizar. Verifique o banco de dados e os logs da API.'), 503
    return graph_response(path)

@app.route('/OptimizeGraphRequest/download.xml')
def downloadOptimizeGraph():
    return graph_response(DOWNLOAD_ROOT / 'KnowledgeBaseOptimized.xml')
    
@app.route('/GraphRequest')
def downloadGraph():
    return graph_response(DOWNLOAD_ROOT / 'KnowledgeBase.xml', prefer_json=True)

@app.route('/saved_model/<path:filename>', methods=['GET', 'POST'])
def download(filename):
    return send_from_directory(
        directory=app.config['UPLOAD_FOLDER'],
        path=filename,
        as_attachment=True,
    )


if __name__ == "__main__":
    app.run(port=3000)
