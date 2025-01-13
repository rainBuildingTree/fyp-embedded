from PIL import Image
import numpy as np

path = './font_images/0.png'
img = Image.open(path)
np_img = np.array(img, dtype=np.uint16)
np_img.flatten()
for item in np_img:
    print(item)

