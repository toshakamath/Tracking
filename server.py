from flask import Flask, url_for, send_from_directory, request
import logging, os
from werkzeug.utils import secure_filename
from flask import jsonify, make_response
import roundrobin
# import worker
import grpc_client

app = Flask(__name__)
file_handler = logging.FileHandler('server.log')
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)

PROJECT_HOME = os.path.dirname(os.path.realpath(__file__))
UPLOAD_FOLDER = '{}/uploads/'.format(PROJECT_HOME)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

saveThisFile = None

def create_new_folder(local_dir):
    newpath = local_dir
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    return newpath

@app.route('/', methods = ['POST'])
def api_root():
    app.logger.info(PROJECT_HOME)
    if request.method == 'POST' and request.files['image']:
        app.logger.info(app.config['UPLOAD_FOLDER'])
        img = request.files['image']
        img_name = secure_filename(img.filename)
        client = grpc_client.Client(roundrobin.getIpAddress())
        client.upload(img, img_name)
        # create_new_folder(app.config['UPLOAD_FOLDER'])
        # saved_path = os.path.join(app.config['UPLOAD_FOLDER'], img_name)
        # app.logger.info("saving {}".format(saved_path))
        # img.save(saved_path)
        # worker.enqueue_request_queue(img.filename,"write")
        # worker.blockThread()
        # return make_response(jsonify({"success":True,"filename":img.filename}),200)
        return make_response(jsonify({"success":True}),200)
    else:
        return "Where is the file?"


@app.route('/addMessage', methods = ['POST'])
def addMessage():
    if request.method == 'POST':
        try:
            data = request.get_json()
            messageId = data['messageId']
            message = data['message']
            
            if messageId is None or message is None:
                print("NO CONTENT")
                return make_response(jsonify({"success":False,"error":"Content is Missing !"}),501)
            else:
                print("Data",message,messageId)
                messageBytes = bytearray(message,'utf-8')
                print("Data",message,messageBytes)
                # Send This to GRPC function
                return make_response(jsonify({"success":True}),200)
        except Exception as e:
            print("EXCEPTION",e)
            return make_response(jsonify({"success":False,"error":"Content is Missing"}),501)
    else:
        print("NO POST")
        return make_response(jsonify({"success":False,"error":"No Message Present"}),501)


@app.route('/addFile', methods = ['POST'])
def addFile():
    if request.method == 'POST':
        try:
            data = request.get_json()
            fileId = data['fileId']
            file = data['content']

            if fileId is None or file is None:
                print("NO CONTENT")
                return make_response(jsonify({"success":False,"error":"Content is Missing"}),501)
            else:
                print("FileId : ",fileId)
                print("File Content : ",file)
                saveThisFile = file
                hashedFileId = secure_filename(fileId)
                # Send This to GRPC function
                # client = grpc_client.Client('localhost:9999')
                # client.upload(fileId, hashedFileId)

                # variables2 = json.loads(s) # to convert back into dictionary
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

        if messageId is None :
            return make_response(jsonify({"success":False,"error":"Content is Missing"}),501)
        else:
            #Get the message from grpc using message ID from request

            # client = grpc_client.Client('localhost:9999')
            # Send messageId to GRPC function and get message in response
            # messageBytes = client.upload(messageId)
            # # convert message byte array to message and return to user
            # message = bytearray(messageBytes)
            #return message in bytes array to client in "content"
            
            return make_response(jsonify({"success":True, "message": "Hello", "messageId": messageId}),200)
    else:
        return make_response(jsonify({"success":False,"error":"No Message Present"}),501)


@app.route('/getFile', methods = ['GET'])
def getFile():
    if request.method == 'GET':
        fileId = request.args.get('fileId')

        if fileId is None :
            return make_response(jsonify({"success":False,"error":"Content is Missing"}),501)
        else:
            print("FILE ID RECEIVED : ",fileId, saveThisFile)
            # Get the file from grpc using file ID from request
            
            # fileBytes = bytearray(file)
            # # fileBytes = json.dumps(myObject)# dictionary to bytes
            # # Send This to GRPC function
            # # variables2 = json.loads(s) # to convert back into dictionary

            #return file in bytes array to client in "content"
            return make_response(jsonify({"success":True, "content": saveThisFile}),200)
    else:
        return make_response(jsonify({"success":False,"error":"No File Present"}),501)



if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False)