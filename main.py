#-Module imports--------------------------------------------------
from flask import Flask, request, session, redirect, jsonify, send_from_directory
from flask_cors import CORS 

from minio import Minio

import os
import socket
#import yaml
import json


#-Custom Modules and mappers-------
#from reserved_instances import invoices, auth, api_helpers

#-Some Globals-----------------------------------------------------
curDir = os.path.dirname(os.path.realpath(__file__)) 
picDir = os.path.join(curDir, "static", "pics")

#-Minio Config via env---
minioConf = {
  "minioBucketName": "pics",
  "minioAccessKey": "minio",
  "minioSecretKey": "minio",
  "minioHost": "localhost:9000",
  "minioSecure": False
}

for key, val in minioConf.items():
  if key in os.environ:
    minioConf[key] = os.environ[key]

#-------------------------


def create_minio_client():
  minioCli = Minio(
    minioConf["minioHost"],
    secure=minioConf["minioSecure"],
    access_key=minioConf["minioAccessKey"],
    secret_key=minioConf["minioSecretKey"]
  )
  return minioCli

#-Build the flask app object---------------------------------------WASN BRETT
app = Flask(__name__, static_url_path='', static_folder='static' )
app.secret_key = "changeitxyz"
app.debug = True
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})


#-App Config and Access Management Section-----------------------
@app.before_first_request
def before_everything():
  # inf = "Do something here"
  if not os.path.isdir(picDir):
    os.makedirs(picDir)

  try: 
    minioCli = create_minio_client()
  except:
    return "Failed to connect to Bucket", 400  

  res = minioCli.bucket_exists(minioConf["minioBucketName"])
  # print(res)
  if not res:
    minioCli.make_bucket(minioConf["minioBucketName"])

#--------------------------------------
@app.before_request
def check_before_every_request():
  inf = "Do something here"


#-The HTML serve part---------------------------------------------
@app.route('/', methods=["GET"])
def html_home_get():
  #return 'Hello from the App root'
  try:
    return app.send_static_file("index.html")
  except:
    return "<h2>Front-End not found in 'dist' folder<h2>"


#-The REST API part-----------------------------------------------
@app.route('/api', methods=["GET"])
def api_home_get():
  reqObj = {
    "method": request.method,
    "path": request.path,
    "message": "Hello From the API",
    "status": 200
  }

  #------------------
  return jsonify(reqObj), reqObj["status"] 


#-The REST API part-----------------------------------------------
@app.route('/api/pics', methods=["GET"])
def api_pics_get():
  reqObj = {
    "method": request.method,
    "path": request.path,
    "message": "",
    "hostname": socket.gethostname(),
    "status": 200
  }

  minioCli = create_minio_client()
  res = minioCli.list_objects(bucket_name=minioConf["minioBucketName"])
  bktImages = []
  for pic in res:
    if pic.object_name.endswith(".jpg") or pic.object_name.endswith(".png"):
      bktImages.append(pic.object_name)
      if pic.object_name not in picDir:
        minioCli.fget_object(
          minioConf["minioBucketName"], pic.object_name, os.path.join(picDir, pic.object_name),
          version_id=pic.version_id,
        )

  curImages = os.listdir(picDir)
  for pic in curImages:
    if pic not in bktImages:
      os.remove(os.path.join(picDir, pic))
    
  reqObj["data"] = os.listdir(picDir)
  
  #------------------
  return jsonify(reqObj), reqObj["status"] 

#-App Runner------------------------------------------------------
if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000)
#------------------------------------------------------------------