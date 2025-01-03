from PIL import Image
import numpy as np

def split_data_to_8bit(data):
    return [((data & 0xFF00) >> 8) & 0xFF, data & 0xFF]

def convert_image_to_data(path):
    image = Image.open(path)
    resized_image = image.resize((128, 128))
    np_image = np.array(resized_image, dtype=np.uint16)
    r = np_image[:,:,0] >> 3
    g = np_image[:,:,1] >> 2
    b = np_image[:,:,2] >> 3
    r = r.flatten().tolist()
    g = g.flatten().tolist()
    b = b.flatten().tolist()
    rgb = [(rr << 11| gg << 5| bb) & 0xFFFF for rr, gg, bb in zip(r, g, b)] 
    final_data = []
    for data in rgb:
        final_data.extend(split_data_to_8bit(data))
    return final_data

def convert_and_save(path_from, path_to):
    list_data = convert_image_to_data(path_from)
    with open(path_to, 'w') as file:
        for value in list_data:
            file.write("%d\n" % value)

def load_list_data(path):
    with open(path, 'r') as file:
        loaded_list = [int(line.strip()) for line in file]
        return loaded_list
    
def reverse_bits(n, bit_length = 16):
    reversed_n = 0
    for i in range(bit_length):
        reversed_n <<= 1
        reversed_n |= (n & 1)
        n >>= 1
    return reversed_n
