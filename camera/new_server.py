import socket
import cv2
from picamera2 import Picamera2

# Picamera2 초기화
picam2 = Picamera2()
picam2.configure(picam2.create_video_configuration(main={"size": (640, 480)}))
picam2.start()

# 서버 소켓 설정
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('0.0.0.0', 8080))
server_socket.listen(1)
print('서버 대기 중...')

conn, addr = server_socket.accept()
print('연결됨:', addr)

try:
    while True:
        frame = picam2.capture_array()
        _, buffer = cv2.imencode('.jpg', frame)
        data = buffer.tobytes()

        # 프레임 길이 전송
        conn.sendall(len(data).to_bytes(4, byteorder='big'))
        # 프레임 데이터 전송
        conn.sendall(data)
except:
    pass
finally:
    picam2.stop()
    conn.close()
    server_socket.close()