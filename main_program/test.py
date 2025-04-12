import cv2
import socketio
import base64
import time
import requests
import os

SERVER_URL = "http://143.89.94.254:5000"
API_KEY = "1234"

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
    cap = cv2.VideoCapture(0)
    try:
        sio.connect(f"{SERVER_URL}?api_key={API_KEY}&mode=sign-to-text")
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            _, buffer = cv2.imencode('.jpg', frame)
            frame_base64 = base64.b64encode(buffer).decode('utf-8')
            sio.emit('frame', f"data:image/jpeg;base64,{frame_base64}")
            time.sleep(0.05)
    except KeyboardInterrupt:
        print("Stopping sign-to-text mode...")
    finally:
        cap.release()
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
