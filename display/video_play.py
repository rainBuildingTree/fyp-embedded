import cv2
import time
import numpy as np
from PIL import Image
from display_driver import DisplayDriver

def convert_frame_to_r5g6b5(image: Image.Image) -> list[int]:
    """
    Pillow 이미지 객체를 RGB565 포맷으로 변환하여 list[int]로 반환
    """
    image = image.convert('RGB')
    data = np.array(image)
    r = (data[:, :, 0] >> 3).astype(np.uint16)
    g = (data[:, :, 1] >> 2).astype(np.uint16)
    b = (data[:, :, 2] >> 3).astype(np.uint16)
    rgb565 = (r << 11) | (g << 5) | b
    return rgb565.flatten().tolist()

def center_crop_to_square(frame):
    h, w, _ = frame.shape
    if w > h:
        delta = (w - h) // 2
        frame = frame[:, delta:delta+h]
    else:
        delta = (h - w) // 2
        frame = frame[delta:delta+w, :]
    return frame

def play_5_frames_on_display(video_path: str, display: DisplayDriver, delay_sec: float = 0.5):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Cannot open video.")
        return

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_indices = [int(total_frames * i / 5) for i in range(5)]

    for frame_idx in frame_indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ret, frame = cap.read()
        if not ret:
            print(f"Failed to read frame {frame_idx}")
            continue

        frame = center_crop_to_square(frame)
        frame = cv2.resize(frame, (128, 128))
        pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        pixel_data = convert_frame_to_r5g6b5(pil_image)
        display.render_image(0, 0, 128, 128, pixel_data)

        time.sleep(delay_sec)

    cap.release()

if __name__ == "__main__":
    # 디스플레이 드라이버 초기화
    display = DisplayDriver()

    # 출력할 비디오 경로 지정
    video_path = "example.mp4"  # 반드시 128x128에 적당한 영상이어야 함 (크롭됨)

    # 5프레임만 추출해서 1초 간격으로 디스플레이 출력
    play_5_frames_on_display(video_path, display, delay_sec=1.0)