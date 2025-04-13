import RPi.GPIO as GPIO
import spidev
import time
import img2dat
from PIL import Image
import numpy as np
import cv2
import socketio
import base64
import time
import os
import sounddevice as sd
from scipy.io.wavfile import write
from picamera2 import Picamera2
import requests
from video_play import *
import app

import importlib

def main():
    try:
        importlib.reload(app)
        app.main()
    except KeyboardInterrupt:
        pass
    finally:
        print("1. app.py 재로드")
        print("2. 프로그램 종료\n")
        selected = input().strip()
        if selected == '1':
            main()
        else:
            return

if __name__ == '__main__':
    main()

