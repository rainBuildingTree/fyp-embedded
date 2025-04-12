import socketio
import asyncio
import base64
import cv2
from picamera2 import Picamera2
import sounddevice as sd
import numpy as np
import io
import wave
from concurrent.futures import ThreadPoolExecutor

SERVER_URL = "http://<서버IP>:8080"
MODE = "sign-to-text"  # or "voice-to-text"

sio = socketio.AsyncClient()
executor = ThreadPoolExecutor()

# 비디오용
picam2 = Picamera2()
picam2.configure(picam2.create_video_configuration(main={"size": (640, 480)}))

# 오디오용
SAMPLE_RATE = 16000
DURATION = 1  # 초 단위 청크

def record_audio_chunk():
    audio = sd.rec(int(SAMPLE_RATE * DURATION), samplerate=SAMPLE_RATE, channels=1, dtype='int16')
    sd.wait()

    buffer = io.BytesIO()
    wf = wave.open(buffer, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(SAMPLE_RATE)
    wf.writeframes(audio.tobytes())
    wf.close()
    return buffer.getvalue()

async def capture_frame():
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(executor, picam2.capture_array)

async def encode_frame(frame):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(executor, lambda: cv2.imencode('.jpg', frame)[1].tobytes())

@sio.event
async def connect():
    print(f"서버에 연결됨 (mode: {MODE})")
    await sio.emit("mode", {"mode": MODE})

@sio.event
async def disconnect():
    print("서버 연결 종료됨")

async def stream_video():
    picam2.start()
    try:
        while True:
            frame = await capture_frame()
            data = await encode_frame(frame)
            encoded = base64.b64encode(data).decode('utf-8')
            await sio.emit('frame', {'image': encoded})
            await asyncio.sleep(0.05)
    finally:
        picam2.stop()

async def stream_audio():
    while True:
        audio_bytes = await asyncio.get_running_loop().run_in_executor(executor, record_audio_chunk)
        encoded = base64.b64encode(audio_bytes).decode('utf-8')
        await sio.emit('audio', {'data': encoded})
        await asyncio.sleep(0.1)

async def main():
    await sio.connect(SERVER_URL + f"?mode={MODE}")
    if MODE == "sign-to-text":
        await stream_video()
    elif MODE == "voice-to-text":
        await stream_audio()
    await sio.wait()

if __name__ == "__main__":
    asyncio.run(main())
