import cv2
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
        cv2.imwrite(self.path + '/' + name + '/capture.jpg', image)
        camera.close()
    
if __name__ == "__main__":
    import sys
    edgeCamera = EdgeCamera('/home/pi/aws/camera/data')
    edgeCamera.captureImage(sys.argv[1])
