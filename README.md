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
- Python 3
- MySQL Server
- Flask
- TensorFLow 2.0
- Scikit Learn
- Numpy 1.*  - Because Tensorflow

# Initilizing steps

Run the following command to run the flask Web API (app.py) on server port 3000:
 - flask run --host=0.0.0.0 --port=3000 &

Modify the ServerProcessAPI.py file to read the correct endpoint of your web API (e.g., api_url_base = '<_API address_>:3000')

Run "python MainServer.py" to run the server constant process or "python ServerProcessAPI.py" to test the web API

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
- <_API address_>:3000/OptimizeGraphRequest/saved_model/<_Model Name_>

Note: We suggest downloading the complete graph first to identify which models are trained and the types of sensors it uses. The complete Graph can also guide decision-making in the requirements elicitation and application design phases.
