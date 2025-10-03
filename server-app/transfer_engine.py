import requests as req
from flask import Flask, request
import os
import zipfile

app = Flask(__name__)



# make a function that takes a file and creates the nesisary meta data. Then read a chunk of the file into a buffer and send it over.

# def send_file(file_obj, server_url):
#     while chunk := file_obj.read(1024*1024):
#         data = {
#             "file_name": "test.txt",
#             "is_done": False,
#             "chunk": chunk
#         }
#         files = {
#             "chunk": chunk
#         }
#         res = req.post(server_url, data=data, files=files)
#         res.raise_for_status()
        
#         print(res.status_code)


# make a receving function that creates the file and dirs with the meta data and then takes each chunk and wrights to the file until tranfer is done. may want to leave the data
# in memory until the transfer is done to prevent possible brocken files. 

chunks = None

@app.route("/upload", methods=["POST"])
def upload_file():
    file = "backup/" + request.form.get("file_name")
    is_done = request.form.get("is_done")
    chunk = request.files.get("chunk")

    os.makedirs(os.path.dirname(file), exist_ok=True)

    with open(file, "ab") as f:
        f.write(chunk.read()) 

    if is_done == "True":
        if ".zip" in file:
            with zipfile.ZipFile(file, "r") as zip:
                zip.extractall("backup/")
        return "File upload done", 201
    else:
        return "File chunk written", 200
        
# This route is used to update the ui if the server IP is valid
@app.route("/test", methods=["GET"])
def respond_valid():
    return "", 200        

    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4000)     