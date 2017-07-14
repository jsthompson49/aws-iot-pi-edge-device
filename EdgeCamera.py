import cv2
import os
import picamera
import picamera.array
import time


class EdgeCamera:
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
        tagFileName = tagDirectory + '/image' + str(len(files)) + '.jpg'
        os.rename(self.getImageFileName(name), tagFileName)

    def removeImage(self, name):
        fileName = self.getImageFileName(name)
        if os.path.exists(fileName):
            os.remove(fileName)

    def getImageFileName(self, name):
        return self.path + '/capture-' + name + '.jpg'
    
if __name__ == "__main__":
    import sys
    edgeCamera = EdgeCamera('/home/pi/aws/camera/data')
    edgeCamera.captureImage(sys.argv[1])
    edgeCamera.tagImage(sys.argv[1], sys.argv[2])
