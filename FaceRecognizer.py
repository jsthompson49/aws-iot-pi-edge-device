import cv2
import cv2.face as cvfr
import numpy as np
import os

class FaceRecognizer:
    MODEL_FILE_NAME = "/model/FaceRecognizerModel.xml"

    def __init__(self, path):
        self.path = path
        self.faceCascade = cv2.CascadeClassifier("/home/pi/opencv-3.1.0/data/haarcascades/haarcascade_frontalface_default.xml");
        self.recognizer = cvfr.createLBPHFaceRecognizer()

    def load(self):
        self.recognizer.load(self.path + self.MODEL_FILE_NAME)

    def save(self):
        self.recognizer.save(self.path + self.MODEL_FILE_NAME)

    def recognize(self, imageFileName):
        print('Recognizing ' +  imageFileName + ' ...')
        grayImage, faces = self.detect(imageFileName)
        if (len(faces) == 1):
            x, y, w, h = faces[0]
            print('Detected face at ({},{})'.format(x, y))
            predictedIndex = self.recognizer.predict(grayImage[y: y + h, x: x + w])
            print("Recognized as " + self.recognizer.getLabelInfo(predictedIndex))
            return self.recognizer.getLabelInfo(predictedIndex)
        else:
            print(str(len(faces)) + " faces detected: " + str(faces))
            return ''

    def drawDetected(self, imageFileName):
        print('Detecting ' +  imageFileName + ' ...')
        grayImage, faces = self.detect(imageFileName)
        if (len(faces) == 0):
            print('No faces detected')
        else:
            for (x, y, w, h) in faces:
                print('Detected face at ({},{}) width={} height={}'.format(x, y, w, h))
                cv2.rectangle(grayImage, (x, y), (x+w, y+h), (0, 255, 0), 2)
            root, ext = os.path.splitext(imageFileName)
            cv2.imwrite(root + '_d' + ext, grayImage)

    def train(self):
        images = []
        ids = []
        id = 0
        for subdir in os.listdir(self.path):
            imageDirPath = os.path.join(self.path, subdir)
            if os.path.isdir(imageDirPath):
                added = False
                imageFileNames = [os.path.join(imageDirPath, f) for f in os.listdir(imageDirPath) if f.endswith('.jpg')]
                for imageFileName in imageFileNames:
                    print('Processing ' +  imageFileName)
                    image, faces = self.detect(imageFileName)
                    if (len(faces) == 1):
                        x, y, w, h = faces[0]
                        print('Adding image')
                        images.append(image[y: y + h, x: x + w])
                        ids.append(id)
                        added = True
                    elif (len(faces) == 0):
                        print('Skipping image: no faces')
                    else:
                        print('Skipping image: too many faces')

                if added:
                    print('Adding ' +  subdir + ':' + str(id))
                    self.recognizer.setLabelInfo(id, subdir)
                id += 1
        print('Training ... ')
        self.recognizer.train(images, np.array(ids))
        print('Training complete')

    def detect(self, imageFileName):
        image = cv2.imread(imageFileName)
        grayImage = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = self.faceCascade.detectMultiScale(image,
            scaleFactor=1.3,
            minNeighbors=5,
            minSize=(100, 100))
        return grayImage, faces
    
if __name__ == "__main__":
    import sys
    faceRecognizer = FaceRecognizer('/home/pi/aws/camera/data')
    if len(sys.argv) > 1:
        path = '/home/pi/aws/camera/data/' + sys.argv[1]
        if os.path.isdir(path):
            imageFileNames = [os.path.join(path, f) for f in os.listdir(path) if f.endswith('.jpg')]
            for imageFileName in imageFileNames:
                  faceRecognizer.drawDetected(imageFileName)
        else:
            faceRecognizer.load()
            faceRecognizer.recognize(path)
    else:
        faceRecognizer.train()
        faceRecognizer.save()
