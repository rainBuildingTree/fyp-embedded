import cv2
import numpy as np
from PIL import Image
import display_driver as dpd
import time

def center_crop_to_square(frame):
    h, w, _ = frame.shape
    if w > h:
        delta = (w - h) // 2
        frame = frame[:, delta:delta + h]
    else:
        delta = (h - w) // 2
        frame = frame[delta:delta + w, :]
    return frame

def convert_frame_to_r5g6b5_bytes(frame) -> list[int]:
    image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)).convert("RGB")
    arr = np.array(image)
    r = (arr[:, :, 0] >> 3).astype(np.uint16)
    g = (arr[:, :, 1] >> 2).astype(np.uint16)
    b = (arr[:, :, 2] >> 3).astype(np.uint16)
    rgb565 = (r << 11) | (g << 5) | b

    # 상하위 바이트 interleave
    high = (rgb565 >> 8).flatten()
    low = (rgb565 & 0xFF).flatten()
    interleaved = np.column_stack((high, low)).flatten()
    return interleaved.tolist()

def play_video_on_display(video_path: str, fps: int = 10):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("❌ Cannot open video.")
        return

    display = dpd.DisplayDriver()
    target_size = 128 * 128 * 2
    delay = 1.0 / fps

    while True:
        ret, frame = cap.read()
        if not ret:
            break  # 영상 끝

        frame = center_crop_to_square(frame)
        frame = cv2.resize(frame, (128, 128))

        processed_img = convert_frame_to_r5g6b5_bytes(frame)
        fill_size = target_size - len(processed_img)
        if fill_size > 0:
            fill_data = [0x80, 0x00] * (fill_size // 2)
            processed_img.extend(fill_data)

        display.set_window(0, 0, 128, 128)
        display.write_command(dpd.DisplayDriver.CMD_MEM_WRITE, processed_img)

        time.sleep(delay)  # 재생 속도 조절

    cap.release()

if __name__ == "__main__":
    play_video_on_display("example.mp4", fps=5)  # or 5, 15 etc.