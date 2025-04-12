import cv2
import socketio
import base64
import time
from picamera2 import Picamera2
import requests
import os

SERVER_URL = "http://143.89.94.254:5000"
API_KEY = "1234"

# Picamera2 초기화 및 설정 (비디오 해상도: 640x480)
picam2 = Picamera2()
picam2.configure(picam2.create_video_configuration(main={"size": (640, 480)}))

sio = socketio.Client()

@sio.event
def connect():
    print(f"Connected to server in {selected_mode} mode")

@sio.on('message')
def on_message(data):
    print(data['data'])

@sio.on('prediction')
def on_prediction(data):
    print(f"Predicted: {data['predicted_word']}, Probability: {data['probability']:.4f}")
    print(f"Top 5: {data['top_5_predictions']}")

@sio.on('video_frame')
def on_video_frame(data):
    print("Received video frame")

@sio.on('error')
def on_error(data):
    print(f"Error: {data['error']}")

def sign_to_text_mode():
    try:
        # 서버 연결
        sio.connect(f"{SERVER_URL}?api_key={API_KEY}&mode=sign-to-text")
        # Picamera2 스트림 시작
        picam2.start()
        while True:
            # Picamera2로부터 프레임 캡처 (numpy 배열)
            frame = picam2.capture_array()
            success, buffer = cv2.imencode('.jpg', frame)
            if not success:
                continue
            frame_base64 = base64.b64encode(buffer).decode('utf-8')
            # 서버로 인코딩된 프레임 전송
            sio.emit('frame', f"data:image/jpeg;base64,{frame_base64}")
            time.sleep(0.05)
    except KeyboardInterrupt:
         print("Stopping sign-to-text mode...")
    finally:
         picam2.stop()  # 스트림 종료
         sio.disconnect()

def speech_to_sign_mode(audio_path):
    try:
        sio.connect(f"{SERVER_URL}?api_key={API_KEY}&mode=speech-to-sign")
        response = requests.post(
            f"{SERVER_URL}/predict_speech?mode=speech-to-sign",
            json={"audio_path": audio_path},
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            with open("output_video.mp4", "wb") as f:
                f.write(response.content)
            print("Video saved as output_video.mp4")
        else:
            print(f"Error: {response.json()['error']}")
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        sio.disconnect()

if __name__ == "__main__":
    selected_mode = input("Select mode (sign-to-text / speech-to-sign): ").strip().lower()
    if selected_mode == "sign-to-text":
        sign_to_text_mode()
    elif selected_mode == "speech-to-sign":
        audio_path = input("Enter audio file path: ").strip()
        if os.path.exists(audio_path):
            speech_to_sign_mode(audio_path)
        else:
            print("Audio file not found!")
    else:
        print("Invalid mode selected!")
