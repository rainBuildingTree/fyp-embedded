from picamera2 import Picamera2

cam = Picamera2()
cam.start_and_record_video("test.mp4", duration=10)
