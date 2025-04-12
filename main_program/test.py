import cv2
import socketio
import base64
import time
import os
import sounddevice as sd
from scipy.io.wavfile import write
from picamera2 import Picamera2
import requests

SERVER_URL = "143.89.94.254:5000"
API_KEY = "1234"

# Picamera2 초기화 및 설정 (비디오 해상도: 640x480)
picam2 = Picamera2()
picam2.configure(picam2.create_video_configuration(main={"size": (640, 480)}))

sio = socketio.Client()

@sio.event
def connect():
    print(f"[✓] Connected to server in {sio.mode} mode")

@sio.on('message')
def on_message(data):
    print(f"[Server Message] {data['data']}")

@sio.on('prediction')
def on_prediction(data):
    print(f"Predicted: {data['predicted_word']}, Probability: {data['probability']:.4f}")
    print(f"Top 5: {data['top_5_predictions']}")

@sio.on('video_frame')
def on_video_frame(data):
    print("Received video frame")

@sio.on('error')
def on_error(data):
    print(f"[Error] {data['error']}")

def sign_to_text_mode():
    try:
        sio.mode = "sign-to-text"
        sio.connect(f"ws://{SERVER_URL}?api_key={API_KEY}&mode=sign-to-text")
        picam2.start()

        print("🟢 Sign-to-text 모드 시작 (Ctrl+C로 종료)")
        while True:
            frame = picam2.capture_array()
            success, buffer = cv2.imencode('.jpg', frame)
            if not success:
                continue
            frame_base64 = base64.b64encode(buffer).decode('utf-8')
            sio.emit('frame', f"data:image/jpeg;base64,{frame_base64}")
            time.sleep(0.05)

    except KeyboardInterrupt:
        print("\n[!] 사용자 중단. Sign-to-text 종료.")
    except Exception as e:
        print(f"[!] 오류 발생: {str(e)}")
    finally:
        picam2.stop()
        if sio.connected:
            sio.disconnect()

def speech_to_sign_mode():
    audio_path = "input_audio.wav"
    try:
        print("🎤 음성 녹음 중 (10초)...")
        duration = 10
        samplerate = 16000
        audio = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='int16')
        sd.wait()

        write(audio_path, samplerate, audio)
        print(f"[✓] 오디오 저장 완료: {audio_path}")

        # 서버 연결 (socket.io는 실제 사용 안 함)
        sio.mode = "speech-to-sign"
        sio.connect(f"http://{SERVER_URL}?api_key={API_KEY}&mode=speech-to-sign")

        with open(audio_path, 'rb') as f:
            files = {'file': (audio_path, f, 'audio/wav')}
            response = requests.post(f"http://{SERVER_URL}/handle_audio", files=files)

        if response.status_code == 200:
            output_path = "output_video.mp4"
            with open(output_path, "wb") as f:
                f.write(response.content)
            print(f"[✓] 비디오 저장 완료: {output_path}")
        else:
            print(f"[!] 서버 오류: {response.text}")

    except Exception as e:
        print(f"[!] 오류 발생: {str(e)}")
    finally:
        if sio.connected:
            sio.disconnect()
        if os.path.exists(audio_path):
            os.remove(audio_path)

def main():
    try:
        while True:
            print("\n=== 모드 선택 ===")
            print("1. 손말 → 텍스트 (sign-to-text)")
            print("2. 음성 → 손말 (speech-to-sign)")
            print("3. 종료")
            selected_mode = input("모드를 선택하세요 (1/2/3): ").strip()

            if selected_mode == "1":
                sign_to_text_mode()
            elif selected_mode == "2":
                speech_to_sign_mode()
            elif selected_mode == "3":
                print("👋 프로그램 종료.")
                break
            else:
                print("❌ 잘못된 입력입니다. 다시 선택하세요.")
    except KeyboardInterrupt:
        print("\n👋 프로그램 강제 종료됨.")

if __name__ == "__main__":
    main()

