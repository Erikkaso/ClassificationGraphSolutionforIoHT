# Classification Graph Solution for IoHT
Solution to create a Classification Graph using Cloud for Internet of Health Applications from Evilasio Junior Research

# Setup

Download this full repository

To add new Datasets:
 - Open Server directory
 - Open Datasets directory
 - Open Source directory
 - Open Datasets directory
 - Add the new Dataset in the Datasets directory
 - Back two directoris for Datasets directory
 - Open DatasetManipulation directory
 - Open Format directory
 - Create code for preprocessing following the pattern of Dataset*.py files and Dataset*<sensors>.py files
 - Optional: Case need add new sensors or sesnsor combinations
 - - Back for DatasetManipulation directory
   - Open Preprocessing directory
   - Create new preprocessing code file for new sensor compbination with same out signature of both other preprocessing code files in this directory
 - Finaly Modify the MainFunctions.py to join the informations for new Dataset to the building graph instrunctions in this code file 

# Dependencies for local execution
- Python 3.10
- MySQL Server
- Python packages listed in `Requirements.txt`

## Docker

The image contains the Flask API, the existing polling process, datasets,
models and all Python dependencies. MySQL remains external to the container.

Build the image from the repository root:

```powershell
docker build -t classification-graph:complete .
```

Run it with the external MySQL connection:

```powershell
docker run --name classification-graph `
  -p 3000:3000 `
  -e DB_HOST="host.docker.internal" `
  -e DB_PORT="3306" `
  -e DB_USER="root" `
  -e DB_PASSWORD="your_password" `
  -e DB_NAME="KnowlegeGraphDB" `
  -v "${PWD}\download:/app/download" `
  -v "${PWD}\Server\MLModels\saved_models:/app/Server/MLModels/saved_models" `
  classification-graph:complete
```

The API is available at `http://localhost:3000`. The container starts both
the API and `API/MainServer.py`; the latter uses the existing polling and
retraining implementation. The image health check calls `/`.

# Initilizing steps

Create a virtual environment and install the dependencies from the repository root:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r Requirements.txt
```

Configure the MySQL connection. The application creates the `KnowlegeGraphDB` database when an endpoint that needs graph data is first called:

```powershell
$env:DB_HOST = "localhost"
$env:DB_USER = "root"
$env:DB_PASSWORD = "your_password"
```

Run the Flask Web API on port 3000:

```powershell
python -m API.app
```

Alternatively, use the Flask CLI:

```powershell
flask --app API.app run --host=0.0.0.0 --port=3000
```

The legacy polling and retraining process in `API/MainServer.py` and `API/ServerProcessApi.py` still requires import and initialization refactoring before use. The commands above start the minimal API for status checks and artifact downloads.

# Web API endpoinds

Informs the API that the graph must be updated:
- <_API address_>:3000/UpdateGraphRequest/2

Download the last updated complete graph:
- <_API address_>:3000/GraphRequest

Download the last generated optimized graph:
- <_API address_>:3000/OptimizeGraphRequest/download.xml

Request for optimization and download of the graph optimized by the application:
- <_API address_>:3000/OptimizeGraphRequest/<_All types of sensors used by the application separated by an underscore_>
or
- <_API address_>:3000/OptimizeGraphRequest/<_All types of sensors used by the application separated by an underscore_>/<_Threshold probability_>

Request to download the trained models:
- <_API address_>:3000/saved_model/<_Model Name_>

Note: We suggest downloading the complete graph first to identify which models are trained and the types of sensors it uses. The complete Graph can also guide decision-making in the requirements elicitation and application design phases.
