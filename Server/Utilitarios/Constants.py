#File Directoies
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]  # sobe: Utilitarios -> Server -> repo
pathBase = str(REPO_ROOT)
projectPathName = "\\ClassificationGraphSolutionforIoHT"
projectPath = pathBase + projectPathName

pathDownloads = "\\download"
pathProjectDownloads = projectPath + pathDownloads

pathSaveModels = "\\Server\\MLModels\\saved_models"
pathProjectSaveModels = projectPath + pathSaveModels

pathDataset = "\\Server\\Datasets\\Source" + "\\" 
pathProjectDataset = projectPath + pathDataset


#Database Connection Information
host_name = 'localhost' 
user_name = 'root'
db_password = 'mysqlroot' #need change for cath from file
db_password_verificator = 0



