from picamera2 import Picamera2, Preview
import time

cam = Picamera2()
config = cam.create_preview_configuration()
cam.configure(config)
#cam.start_preview(Preview.DRM)
cam.start()
time.sleep(2)
cam.capture_file("test.jpg")

