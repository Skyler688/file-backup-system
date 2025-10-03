import requests as req
from flask import Flask, request
import os
import shutil

app = Flask(__name__)

# This function is used to validate the servers url in live time
def server_test(server_url):
    try:
        res = req.get("http://" + server_url + ":4000/test", timeout=0.3)
        res.raise_for_status()

        if res.status_code == 200:
            return True
        else:
            return False
    except (req.exceptions.ConnectionError,
            req.exceptions.Timeout,
            req.exceptions.HTTPError,
            req.exceptions.InvalidURL):
        return False

# This function will open the target file and send over 1Mb chunks to the server.
def send_file(file_path, server_ip):
    file_size = os.path.getsize(file_path)
    sent_bytes = 0

    server_url = "http://" + server_ip + ":4000/upload"

    with open(file_path, "rb") as file_obj:
        while chunk := file_obj.read(1024 * 1024): # 1M byte chunks
            sent_bytes += len(chunk)

            is_done = sent_bytes >= file_size
                
            data = {
                "file_name": file_path,
                "is_done": is_done, 
            }
            binary_chunk = {
                "chunk": chunk
            }
            res = req.post(server_url, data=data, files=binary_chunk)
            res.raise_for_status()
            
            print(res)

# NOTE -> should use when a new target is added or the target structure is changed.
def backup_target(target, server_ip):
    path_dirs = target.split("/")
    sudo_path = ""
    for index, dir in enumerate(path_dirs):
        sudo_path += dir
        if len(path_dirs) - 1 != index:
            sudo_path += "_"
    print(sudo_path)        
    shutil.make_archive(sudo_path, "zip", target)
    send_file(file_path=sudo_path + ".zip", server_ip=server_ip)
    os.remove(sudo_path + ".zip")
    # for child in targets["children"]: 
    #     if child["type"] == "file":
    #         send_file(child["path"], server_ip=server_ip)
    #     elif child["type"] == "dir":
    #         backup_target(targets=child, server_ip=server_ip) # recursive calls to copy over the pull directory tree




# with open("testing.txt", "w") as test_file:
#     for index in range(1000000):
#         test_file.write(f"testingtestingtestingtestingtestingtestingtestingtestingtestingtestingtestingtestingtestingtestingtesting{index}\n")

 
# send_file("hip-hop-trap.als", "http://127.0.0.1:4000/upload")   




# make a receving function that creats the file and dirs with the meta data and then takes each chunk and writes to the file until tranfer is done. may want to leave the data
# in memory until the tranfer is done to prevent posible brocken files. 

chunks = None

@app.route("/upload", methods=["POST"])
def upload_file():
    file = request.form.get("file_name")
    is_done = request.form.get("is_done")
    chunk = request.files.get("chunk")

    with open(file, "ab") as f:
        f.write(chunk.read())  
        if is_done == "True":
            return "File upload done", 201
        else:
            return "File chunk written", 200
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)   