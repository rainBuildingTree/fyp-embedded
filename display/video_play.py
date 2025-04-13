import cv2
import numpy as np
from PIL import Image
import display_driver as dpd

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
    """
    NumPy BGR frame → PIL RGB → RGB565 bytes list
    """
    image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)).convert("RGB")
    arr = np.array(image)
    r = (arr[:, :, 0] >> 3).astype(np.uint16)
    g = (arr[:, :, 1] >> 2).astype(np.uint16)
    b = (arr[:, :, 2] >> 3).astype(np.uint16)
    rgb565 = (r << 11) | (g << 5) | b

    # 상위 바이트, 하위 바이트 분리
    high = (rgb565 >> 8).flatten()
    low = (rgb565 & 0xFF).flatten()
    interleaved = np.column_stack((high, low)).flatten()
    return interleaved.tolist()

def play_5_frames_with_input(video_path: str):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("❌ Cannot open video.")
        return

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if total_frames < 5:
        print("❌ Not enough frames.")
        return

    frame_indices = [int(total_frames * i / 5) for i in range(5)]
    display = dpd.DisplayDriver()
    target_size = 128 * 128 * 2  # 16-bit per pixel

    for idx in frame_indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ret, frame = cap.read()
        if not ret:
            print(f"⚠️ Failed to read frame {idx}")
            continue

        frame = center_crop_to_square(frame)
        frame = cv2.resize(frame, (128, 128))

        processed_img = convert_frame_to_r5g6b5_bytes(frame)
        fill_size = target_size - len(processed_img)
        if fill_size > 0:
            fill_data = [0x80, 0x00] * (fill_size // 2)
            processed_img.extend(fill_data)

        display.set_window(0, 0, 128, 128)
        display.write_command(dpd.DisplayDriver.CMD_MEM_WRITE, processed_img)

        # 사용자 입력 대기
        while True:
            key = input("▶ Press 'x' to show next frame: ")
            if key.lower() == 'x':
                break

    cap.release()


if __name__ == "__main__":
    # 디스플레이 드라이버 초기화
    display = DisplayDriver()

    # 출력할 비디오 경로 지정
    video_path = "example.mp4"  # 반드시 128x128에 적당한 영상이어야 함 (크롭됨)

    # 5프레임만 추출해서 1초 간격으로 디스플레이 출력
    play_5_frames_on_display(video_path, display, delay_sec=1.0)