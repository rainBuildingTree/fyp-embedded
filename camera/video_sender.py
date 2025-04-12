import cv2
import asyncio
import websockets

async def send_video():
    with asyncio.wait_for(websockets.connect('ws://172.29.164.229:8000/video'), 60):
        cap = cv2.VideoCapture(0)
        #while True:
            #ret, frame = cap.read()
            #if not ret:
            #    break
            #_, buffer = cv2.imencode('.jpg', frame)
            #await websocket.send(buffer.tobytes())
        cap.release()

asyncio.run(send_video())
