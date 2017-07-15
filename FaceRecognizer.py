import cv2
import cv2.face as cvfr
import numpy as np
import os

class FaceRecognizer:
    def __init__(self, path):
        self.path = path
        self.labels = []
        self.recognizer = cvfr.createLBPHFaceRecognizer()

    def predict(self, imageFileName):
        print('Predicting ' +  imageFileName)
        image = cv2.imread(imageFileName)
        grayImage = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        #x = 0
        #y = 0
        #w = 400
        #h = 600
        #predictedIndex,confidence = self.recognizer.predict(grayImage[y: y + h, x: x + w])
        predictedIndex = self.recognizer.predict(grayImage)
        print("Recognized as " + self.labels[predictedIndex])

    def train(self):
        images = []
        ids = []
        id = 0
        for subdir in os.listdir(self.path):
            imageDirPath = os.path.join(self.path, subdir)
            if os.path.isdir(imageDirPath):    
                imageFileNames = [os.path.join(imageDirPath, f) for f in os.listdir(imageDirPath) if f.endswith('.jpg')]
                for imageFileName in imageFileNames:
                    print('Adding ' +  subdir + '(' + str(id) + '): ' + imageFileName)
                    image = cv2.imread(imageFileName)
                    images.append(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY))
                    ids.append(id)
                self.labels.append(subdir)
                id += 1
        print('Training for labels ... ' + str(self.labels))
        self.recognizer.train(images, np.array(ids))
        print('Training complete')
    
if __name__ == "__main__":
    import sys
    faceRecognizer = FaceRecognizer('/home/pi/aws/camera/data')
    faceRecognizer.train()
    if len(sys.argv) > 1:
        faceRecognizer.predict('/home/pi/aws/camera/data/' + sys.argv[1])
