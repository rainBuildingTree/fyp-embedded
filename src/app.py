print("Start Module Loading...\n")
import cv2
print("cv2 loaded")
import socketio
print("socketio loaded")
import base64
print("base64 loaded")
import time
print("time loaded")
import os
print("os loaded")
import sounddevice as sd
print("sounddevice loaded")
from scipy.io.wavfile import write
print("scipy loaded")
from picamera2 import Picamera2
print("piCamera2 loaded")
import requests
print("request loaded")
from video_play import *
print("video play loaded")
print("Module Loading Finished!\n")
import subprocess

from picamera2 import Picamera2
picam2 = Picamera2()
picam2.configure(picam2.create_video_configuration(main={"size": (640, 480)}))

print("Start Data Initializing...\n")
SERVER_URL = "143.89.94.254:5000"
API_KEY = "1234"

# Picamera2 초기화 및 설정 (비디오 해상도: 640x480)
print("Camera Initialized")
sio = socketio.Client()
print("Socket Initialized")
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
        #sio.mode = "sign-to-text"
        #sio.connect(f"ws://{SERVER_URL}?api_key={API_KEY}&mode=sign-to-text")
        #picam2.start()

        print("Sign-to-text 모드 시작 (Ctrl+C로 종료)")
        #picam2.start_and_record_video("buffer.mp4", duration=10)
        #time.sleep(1.0)
        #subprocess.run([
        #    "ffmpeg", "-y", "-i", "buffer.mp4",
        #    "-vf", "transpose=1",  # 실제 회전
        #    "-c:a", "copy",
        #    "buffer_rotated.mp4"
        #])
        filename = input("Write the file name: ")
        with open(filename, 'rb') as f:
            files = {'file': (filename, f, 'video/mp4')}
            start_time = time.time()
            response = requests.post(f"http://{SERVER_URL}/upload_sign_video?api_key={API_KEY}", files=files, stream=True)
            end_time = time.time()
            content = response.content
            retrieve_time = time.time()
            print(f'Upload Delay: {end_time - start_time}')
            print(f'Retrieve Delay: {retrieve_time - end_time}')
            print(str(content))
            #with open('output_video.mp4', 'wb') as outputb:
            #    outputb.write(response.content)
        #play_video_on_display('output_video.mp4', 15)
        #while True:
        #    frame = picam2.capture_array()
        #    success, buffer = cv2.imencode('.jpg', frame)
        #    if not success:
        #        continue
        #    frame_base64 = base64.b64encode(buffer).decode('utf-8')
        #    sio.emit('frame', f"data:image/jpeg;base64,{frame_base64}")
        #    time.sleep(0.05)

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
        
        play_video_on_display('output_video.mp4', 15)

    except Exception as e:
        print(f"[!] 오류 발생: {str(e)}")
    finally:
        if sio.connected:
            sio.disconnect()
        if os.path.exists(audio_path):
            os.remove(audio_path)
print("Methods Initialized")
print("Data Initializing Finished!\n")

print("Start Main Program")
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

