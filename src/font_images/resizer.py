import os
from PIL import Image

def resize_all_images_in_directory(directory_path, scale=2):
    for filename in os.listdir(directory_path):
        if filename.lower().endswith(".png"):
            file_path = os.path.join(directory_path, filename)
            try:
                img = Image.open(file_path)
                new_size = (img.width * scale, img.height * scale)
                resized_img = img.resize(new_size, Image.NEAREST)

                # 만약 원본이 1bit 이미지였으면 다시 1bit로 변환
                if img.mode == '1':
                    resized_img = resized_img.convert('1')

                resized_img.save(file_path)
                print(f"[✓] Resized: {filename} → {new_size}")
            except Exception as e:
                print(f"[!] Failed to resize {filename}: {e}")

# 예시 사용
resize_all_images_in_directory(".", scale=2)