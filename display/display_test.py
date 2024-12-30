import display_driver as dpd
import img_converter as ic

img_path = './test_images/skullman.png'
processed_img = ic.convert_image_to_data(img_path)
print(len(processed_img))
display = dpd.DisplayDriver()
target_size = 128 * 128 * 2
fill_size = target_size - len(processed_img)
fill_data = [0xFF] * fill_size
processed_img.extend(fill_data)
display.set_window(0,0,128,128)
display.write_command(dpd.DisplayDriver.CMD_MEM_WRITE, processed_img)

while True:
    input_key = input("press x to finish")
    if input_key == 'x':
        break
