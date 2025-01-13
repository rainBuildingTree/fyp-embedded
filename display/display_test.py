import display_driver as dpd
import img2dat as ic

img_path = './test_images/skullman.png'
processed_img = ic.convert_image_to_data(img_path)
print(len(processed_img))
print(processed_img[0], processed_img[1])
display = dpd.DisplayDriver()
target_size = 128 * 128 * 2
fill_size = target_size - len(processed_img)
fill_data = [0b10000000, 0b00000000] * int(fill_size/2)
processed_img.extend(fill_data)
display.set_window(0,0,128,128)
display.write_command(dpd.DisplayDriver.CMD_MEM_WRITE, processed_img)

while True:
    input_key = input("press x to proceed")
    if input_key == 'x':
        break

display.render_text(0,0,"HELLO WORLD AND GOODBYE WORLD")

while True:
    input_key = input("press x to proceed")
    if input_key == 'x':
        break
