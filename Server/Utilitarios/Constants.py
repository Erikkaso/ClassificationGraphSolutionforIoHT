#File Directoies
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

REPO_ROOT = Path(__file__).resolve().parents[3]  # sobe: Utilitarios -> Server -> repo
pathBase = str(REPO_ROOT)
projectPathName = "\\ClassificationGraphSolutionforIoHT"
projectPath = pathBase + projectPathName

pathDownloads = "\\download"
pathProjectDownloads = projectPath + pathDownloads

pathSaveModels = "\\Server\\MLModels\\saved_models"
pathProjectSaveModels = projectPath + pathSaveModels
graphName = "KnowledgeBase"
graphOptimizedName = "KnowledgeBaseOptimized"

pathDataset = "\\Server\\Datasets\\Source" + "\\" 
pathProjectDataset = projectPath + pathDataset


#Database Connection Information
host_name = os.environ.get("DB_HOST") or 'localhost' 
user_name = os.environ.get("DB_USER") or 'root'
db_password = os.environ.get("DB_PASSWORD") or 'mysqlroot' #need change for cath from file
db_password_verificator = 0



