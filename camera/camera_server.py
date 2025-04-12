import socket
from picamera2 import Picamera2, Preview
from picamera2.outputs import FileOutput
from picamera2.encoders import H264Encoder

# 서버 소켓 설정
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(('0.0.0.0', 8080))
server_socket.listen(1)
print('서버가 시작되었습니다. 클라이언트를 기다리고 있습니다...')

client_socket, _ = server_socket.accept()
print(f"클라이언트 연결됨")

# PiCamera2 설정
picam2 = Picamera2()
camera_config = picam2.create_video_configuration(main={"size": (640, 480)})
picam2.configure(camera_config)

# 스트림을 파일 처럼 사용 (바이너리 모드 "wb"로 소켓 스트림 설정)
stream = client_socket.makefile('wb') 
output = FileOutput(stream)
encoder = H264Encoder(bitrate=10000000)
picam2.start_recording(encoder, output)

picam2.start()

try:
    while True:
        pass  # 무한 루프로 채우기 (필요 시 필요한 동작을 추가 가능)
except KeyboardInterrupt:
    picam2.stop_recording()
    picam2.stop()
    picam2.close()
finally:
    client_socket.close()
    server_socket.close()

