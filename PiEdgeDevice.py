from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import argparse
import EdgeCamera as ec
import FaceRecognizer as fr
import json
import logging
import os
import sys
import time
import uuid

messageCount = 0
count = 0

def topicCallback(client, userdata, message):
        global messageCount
        messageCount += 1
        print("From IoT Queue received(" + str(messageCount) + "): " + message.topic + " => " + str(message.payload))

        request = json.loads(message.payload.decode())
        requestType = request['type']
        if 'action' in request:
            action = request['action']
            mode = request['mode']
            if 'arguments' in request:
                    arguments = request['arguments']
            else:
                    arguments = {}
            print("request=" + requestType + " mode=" + mode + " action=" + action + " arguments=" + str(arguments) + "\n")
            processCommand(requestType, mode, action, arguments)
        

def processCommand(requestType, mode, action, arguments):
        if requestType == "camera":
                if mode == 'image':
                        if action == 'capture':
                                imageId = str(uuid.uuid4())
                                edgeCamera.captureImage(imageId)
                                imageFileName = edgeCamera.getImageFileName(imageId)
                                tag = faceRecognizer.recognize(imageFileName)
                                if tag == '':
                                        sendResponse('camera', 'image', { 'imageId': imageId })
                                else:
                                        sendResponse('camera', 'image', { 'tag': tag })
                                        os.remove(imageFileName)
                        elif action == 'tag':
                                edgeCamera.tagImage(arguments['imageId'], arguments['tag'])
                        elif action == 'remove':
                                edgeCamera.removeImage(arguments['imageId'])
        
def sendResponse(responseType, reply, results):
        response = {'type': responseType, 'reply': reply, 'results': results}
        myAWSIoTMQTTClient.publish(topic, json.dumps(response), 1)

# Read in command-line parameters
parser = argparse.ArgumentParser()
parser.add_argument("-e", "--endpoint", action="store", dest="host", default="a131ws0b6gtght.iot.us-west-2.amazonaws.com", help="Your AWS IoT custom endpoint")
parser.add_argument("-r", "--rootCA", action="store", dest="rootCAPath", default="/home/pi/aws/root-CA.crt", help="Root CA file path")
parser.add_argument("-c", "--cert", action="store", dest="certificatePath", default="/home/pi/aws/RaspberryPiPrimary.cert.pem", help="Certificate file path")
parser.add_argument("-k", "--key", action="store", dest="privateKeyPath", default="/home/pi/aws/RaspberryPiPrimary.private.key", help="Private key file path")
parser.add_argument("-w", "--websocket", action="store_true", dest="useWebsocket", default=False, help="Use MQTT over WebSocket")
parser.add_argument("-id", "--clientId", action="store", dest="clientId", default="RaspberryPiPrimary", help="Targeted client id")
parser.add_argument("-t", "--topic", action="store", dest="topic", default="demo/command", help="Targeted topic")
parser.add_argument("-dp", "--dataPath", action="store", dest="dataPath", default="/home/pi/aws/camera/data", help="Path to raw data storage")

args = parser.parse_args()
host = args.host
rootCAPath = args.rootCAPath
certificatePath = args.certificatePath
privateKeyPath = args.privateKeyPath
useWebsocket = args.useWebsocket
clientId = args.clientId
topic = args.topic
dataPath = args.dataPath

if args.useWebsocket and args.certificatePath and args.privateKeyPath:
	parser.error("X.509 cert authentication and WebSocket are mutual exclusive. Please pick one.")
	exit(2)

if not args.useWebsocket and (not args.certificatePath or not args.privateKeyPath):
	parser.error("Missing credentials for authentication.")
	exit(2)

# Configure logging
logger = logging.getLogger("AWSIoTPythonSDK.core")
logger.setLevel(logging.DEBUG)
streamHandler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)

# Configure Camera Device
edgeCamera = ec.EdgeCamera(dataPath)
faceRecognizer = fr.FaceRecognizer(dataPath)
faceRecognizer.load()

# Init AWSIoTMQTTClient
myAWSIoTMQTTClient = None
if useWebsocket:
	myAWSIoTMQTTClient = AWSIoTMQTTClient(clientId, useWebsocket=True)
	myAWSIoTMQTTClient.configureEndpoint(host, 443)
	myAWSIoTMQTTClient.configureCredentials(rootCAPath)
else:
	myAWSIoTMQTTClient = AWSIoTMQTTClient(clientId)
	myAWSIoTMQTTClient.configureEndpoint(host, 8883)
	myAWSIoTMQTTClient.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

# AWSIoTMQTTClient connection configuration
myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

# Connect and subscribe to AWS IoT
myAWSIoTMQTTClient.connect()
myAWSIoTMQTTClient.subscribe(topic, 1, topicCallback)
time.sleep(2)

# Publish to the same topic in a loop forever
while True:
        if (count % 60 == 0):
            print("Listening ... " + str(count) + " seconds; processed " + str(messageCount) + " messages\n")

        count += 1
        time.sleep(1)
