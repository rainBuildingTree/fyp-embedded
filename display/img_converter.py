from PIL import Image
import numpy as np

def convert_image_to_data(path):
    image = Image.open(path)
    resized_image = Image.resize((128, 128))
    np_image = np.array(resized_image)
    r = np_image[:,:,0] >> 3
    g = np_image[:,:,1] >> 2
    b = np_image[:,:,2] >> 3
    rgb = (r << 11) | (g << 5) | b
    return rgb.tolist()