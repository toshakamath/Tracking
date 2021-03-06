from flask import Flask, url_for, send_from_directory, request
import logging, os
from werkzeug.utils import secure_filename
from flask import jsonify, make_response
import roundrobin
import storage_client
import traversal_client
import time
import urllib

app = Flask(__name__)
file_handler = logging.FileHandler('server.log')
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)

PROJECT_HOME = os.path.dirname(os.path.realpath(__file__))
UPLOAD_FOLDER = '{}/uploads/'.format(PROJECT_HOME)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def create_new_folder(local_dir):
    newpath = local_dir
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    return newpath

@app.route('/', methods = ['POST'])
def api_root():
    app.logger.info(PROJECT_HOME)
    if request.method == 'POST' and request.files['image']:
        start = time.time()
        app.logger.info(app.config['UPLOAD_FOLDER'])
        img = request.files['image']
        img_name = secure_filename(img.filename)
        # client = storage_client.Client(roundrobin.getIpAddress())
        client = storage_client.Client(roundrobin.getIpAddress()+":2750")
        client.upload(img, img_name)
        end = time.time()
        print("File size in bytes==", 119669)
        print("Total time with file im memory for upload= ",end - start)
        return make_response(jsonify({"success":True}),200)
    else:
        return "Where is the file?"

@app.route('/getFile', methods = ['GET'])
def getFile():
    if request.method == 'GET':
        fileId = request.args.get('fileId')

        if fileId is None :
            return make_response(jsonify({"success":False,"error":"Content is Missing"}),501)
        else:
            # Get the file from grpc using file ID from request
            fileId = urllib.parse.unquote(fileId)
        
            # hashedFileId = secure_filename(fileId)
            # print("FILE ID  :: ",fileId,hashedFileId);
            ipaddress = roundrobin.getIpAddress()
            client = traversal_client.TraversalClient(ipaddress+":2750", ipaddress)
            result = client.download(fileId)
            if result is None:
                return make_response(jsonify({"success":False,"error":"No such file Present"}),501)

            print("===============result==============")
            print(result)

            #return file in bytes array to client in "content"
            return make_response(jsonify({"success":True, "content": result}),200)
    else:
        return make_response(jsonify({"success":False,"error":"No File Present"}),501)


@app.route('/addFile', methods = ['POST'])
def addFile():
    if request.method == 'POST':
        try:
            data = request.get_json()
            fileId = data['fileId']
            file = data['content']
            fileSize = data['size']

            if fileId is None or file is None:
                print("NO CONTENT")
                return make_response(jsonify({"success":False,"error":"Content is Missing"}),501)
            else:
                # hashedFileId = secure_filename(fileId)
                # Send This to GRPC function
                # client = storage_client.Client(roundrobin.getIpAddress())
                # client.upload(file, hashedFileId)
                #hashedFileId = secure_filename(fileId)
                print("FILE ID  :: ",fileId)
                client = storage_client.Client(roundrobin.getIpAddress()+":2750")
                success = client.upload(file, fileId, fileSize)

                return make_response(jsonify({"success":True}),200)
        except Exception as e:
            print("EXCEPTION",e)
            return make_response(jsonify({"success":False,"error":"Content is Missing"}),501)
    else:
        print("NO POST")
        return make_response(jsonify({"success":False,"error":"No File Present"}),501)


@app.route('/getMessage', methods = ['GET'])
def getMessage():
    if request.method == 'GET':
        messageId = request.args.get('messageId')
        print("messageId--get--==", messageId)
        if messageId is None :
            return make_response(jsonify({"success":False,"error":"Content is Missing"}),501)
        else:
            # client = storage_client.Client(roundrobin.getIpAddress())
            client = storage_client.Client("127.0.0.1:2750")
            result = client.getMessage(messageId)
            if result is None:
                return make_response(jsonify({"success":False,"error":"No Message with this messageId is present"}),501)
            return make_response(jsonify({"success":True, "message": result, "messageId": messageId}),200)
    else:
        return make_response(jsonify({"success":False,"error":"No Message Present"}),501)

@app.route('/addMessage', methods = ['POST'])
def addMessage():
    if request.method == 'POST':
        try:
            data = request.get_json()
            messageId = data['messageId']
            message = data['message']
            
            if messageId is None or message is None:
                return make_response(jsonify({"success":False,"error":"Content is Missing !"}),501)
            else:
                # client = storage_client.Client(roundrobin.getIpAddress())
                client = storage_client.Client(roundrobin.getIpAddress()+":2750")
                # messageBytes = bytearray(message,'utf-8')
                # hashedMessageId = secure_filename(messageId)
                # client = grpc_client.Client(roundrobin.getIpAddress())
                # client.upload(messageBytes, hashedMessageId)
                # client = grpc_client.Client(roundrobin.getIpAddress())
                print("message==", message)
                print("messageId==", messageId)
                client.sendMessage(message, messageId)
                return make_response(jsonify({"success":True}),200)
        except Exception as e:
            print("EXCEPTION",e)
            return make_response(jsonify({"success":False,"error":"Content is Missing"}),501)
    else:
        print("NO POST")
        return make_response(jsonify({"success":False,"error":"No Message Present"}),501)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False,threaded=True)