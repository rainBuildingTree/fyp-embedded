from picamera2 import Picamera2
import subprocess

cam = Picamera2()
cam.configure(cam.create_video_configuration(main={"size": (640, 480)}))
cam.start_and_record_video("test.mp4", duration=10)
print('start')
subprocess.run([
    "ffmpeg", "-y", "-i", "test.mp4",
    "-c", "copy", "-metadata:s:v", "rotate=270",
    "test_rotated.mp4"
])
print('end')