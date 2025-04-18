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
import json
import display_driver as dpd

from picamera2 import Picamera2
picam2 = Picamera2()
picam2.configure(picam2.create_video_configuration(main={"size": (640, 480)}))

print("Start Data Initializing...\n")
SERVER_URL = "10.89.100.33:5000"
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
        print("🟢 Sign-to-text Mode Start (Ctrl+C to quit)")

        filename = input("📂 Write the file name: ")
        with open(filename, 'rb') as f:
            files = {'file': (filename, f, 'video/mp4')}
            start_time = time.time()
            response = requests.post(f"http://{SERVER_URL}/upload_sign_video?api_key={API_KEY}", files=files, stream=True)
            end_time = time.time()
            content = response.content.decode('utf-8')
            retrieve_time = time.time()
            content_json = json.loads(content)
            pretty = json.dumps(content_json, indent=2, ensure_ascii=False)

            print(f'⏱️ Upload Delay: {end_time - start_time:.3f} sec')
            print(f'⏱️ Retrieve Delay: {retrieve_time - end_time:.3f} sec')
            print(pretty)

            # 디스플레이 준비
            display = dpd.DisplayDriver()
            display.render_square(0, 0, 128, 128, 0xFFFF)

            # 최종 예측 텍스트 준비
            if "final_prediction" in content_json:
                prediction_text = content_json["final_prediction"].upper()
            else:
                prediction_text = "NO PREDICTION FOUND"

            # 여러 줄로 나누기 (줄당 최대 문자 수 = 128 / FONT_WIDTH)
            max_chars_per_line = 128 // display.FONT_WIDTH  # 128 / 20 = 6
            lines = [prediction_text[i:i + max_chars_per_line] for i in range(0, len(prediction_text), max_chars_per_line)]

            total_text_height = len(lines) * display.FONT_HEIGHT
            start_y = max((128 - total_text_height) // 2, 0)

            # 줄마다 중앙 정렬하여 출력
            for idx, line in enumerate(lines):
                line_width = len(line) * display.FONT_WIDTH
                x = max((128 - line_width) // 2, 0)
                y = start_y + idx * display.FONT_HEIGHT
                display.render_text(x, y, line)

            input("🔵 press any key to close...")
            
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
        print("\n[!] User interrupt. Sign-to-text exit.")
    except Exception as e:
        print(f"[!] Error occured: {str(e)}")
    finally:
        picam2.stop()
        if sio.connected:
            sio.disconnect()

def speech_to_sign_mode():
    audio_path = "input_audio.wav"
    try:
        print("🎤 recording (10 secs)...")
        duration = 10
        samplerate = 16000
        audio = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='int16')
        sd.wait()

        write(audio_path, samplerate, audio)
        print(f"[✓] audio saving finished: {audio_path}")

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
            print(f"[✓] video saving finished: {output_path}")
        else:
            print(f"[!] server error: {response.text}")
        
        play_video_on_display('output_video.mp4', 15)

    except Exception as e:
        print(f"[!] error occured: {str(e)}")
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
            print("\n=== Mode Selection ===")
            print("1.  (sign-to-text)")
            print("2.  (speech-to-sign)")
            print("3. exit")
            selected_mode = input("Select Mode (1/2/3): ").strip()

            if selected_mode == "1":
                sign_to_text_mode()
            elif selected_mode == "2":
                speech_to_sign_mode()
            elif selected_mode == "3":
                print("👋 program exit")
                break
            else:
                print("❌ Wrong input, select again")
    except KeyboardInterrupt:
        print("\n👋 Force program exit")

if __name__ == "__main__":
    main()

