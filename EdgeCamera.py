import cv2
import os
import picamera
import picamera.array
import time


class EdgeCamera:
    FILE_NAME_PREFIX = "capture-"
    FILE_NAME_EXTENSION = ".jpg"

    def __init__(self, path):
        self.path = path

    def captureImage(self, name):
        camera = picamera.PiCamera()
        rawCap=picamera.array.PiRGBArray(camera)
        camera.start_preview()
        time.sleep(1)
        camera.capture(rawCap, format='bgr')
        image=rawCap.array
        cv2.imwrite(self.getImageFileName(name), image)
        camera.close()

    def tagImage(self, name, tag):
        tagDirectory = self.path + '/' + tag
        if not os.path.exists(tagDirectory):
            os.mkdir(tagDirectory)
        files = os.listdir(tagDirectory)
        tagFileName = tagDirectory + '/image' + str(len(files)) + self.FILE_NAME_EXTENSION
        os.rename(self.getImageFileName(name), tagFileName)

    def removeImage(self, name):
        fileName = self.getImageFileName(name)
        if os.path.exists(fileName):
            os.remove(fileName)

    def getImageFileName(self, name):
        return self.path + '/' + self.FILE_NAME_PREFIX + name + self.FILE_NAME_EXTENSION

    def getImageId(self, imageFileName):
        basename = os.path.basename(imageFileName)
        return basename[len(self.FILE_NAME_PREFIX):len(basename) - len(self.FILE_NAME_EXTENSION)]

    def getLatestImageFileName(self):
        imageFileNames = [os.path.join(self.path, f) for f in os.listdir(self.path) if f.startswith(self.FILE_NAME_PREFIX) and f.endswith(self.FILE_NAME_EXTENSION)]
        latest = max(imageFileNames, key=os.path.getctime)
        print("latest={} mod={} current={}".format(latest, os.path.getctime(latest), time.time()))
        if time.time() - os.path.getctime(latest) > 120:
            latest = ''
        return latest
    
if __name__ == "__main__":
    import sys
    edgeCamera = EdgeCamera('/home/pi/camera/data')
    edgeCamera.captureImage(sys.argv[1])
    edgeCamera.tagImage(sys.argv[1], sys.argv[2])
