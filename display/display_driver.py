import RPi.GPIO as GPIO
import spidev
import time
import img2dat

class DisplayDriver:
    # Manipulate offset according to the device condition
    DEVICE_COL_OFFSET = 2
    DEVICE_ROW_OFFSET = 1
    # Command List
    CMD_PIXEL_FMT_SET = 0x3A
    DAT_12BIT_PER_PIXEL = 0x01
    DAT_16BIT_PER_PIXEL = 0x05
    DAT_18BIT_PER_PIXEL = 0x06
    CMD_SLEEP_IN = 0x10
    CMD_SLEEP_OUT = 0x11
    CMD_DISPLAY_INVERSION_OFF = 0x20
    CMD_DISPLAY_INVERSION_ON = 0x21
    CMD_DISPLAY_OFF = 0x28
    CMD_DISPLAY_ON = 0x29
    CMD_COL_ADDR_SET = 0x2A
    CMD_ROW_ADDR_SET = 0x2B
    CMD_MEM_WRITE = 0x2C
    CMD_TEARING_EFFECT_OFF = 0x34
    CMD_TEARING_EFFECT_ON = 0x35
    CMD_MEM_ACCESS_CTRL = 0x36
    # Hardware Data
    DC_PIN = 25
    RST_PIN = 22
    SPI_BUS = 0
    SPI_DEVICE = 0
    DISPLAY_WIDTH = 128
    DISPLAY_HEIGHT = 128
    FONT_WIDTH = 10
    FONT_HEIGHT = 15
    FONT_LOCATION = './font_images/'

    def __init__(self):
        # Setup SPI
        self.spi = spidev.SpiDev()
        self.spi.open(self.SPI_BUS, self.SPI_DEVICE)
        self.spi.max_speed_hz = 10000000
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.DC_PIN, GPIO.OUT)
        GPIO.setup(self.RST_PIN, GPIO.OUT)

        # Setup Display Hardware
        self.reset_device()
        self.write_command(DisplayDriver.CMD_PIXEL_FMT_SET, DisplayDriver.DAT_16BIT_PER_PIXEL)
        self.write_command(DisplayDriver.CMD_MEM_ACCESS_CTRL, 0b00001000)
        self.write_command(DisplayDriver.CMD_DISPLAY_INVERSION_ON)
        self.write_command(DisplayDriver.CMD_SLEEP_OUT)
        time.sleep(0.12)
        self.write_command(DisplayDriver.CMD_DISPLAY_ON)
        time.sleep(0.02)

        # Load Font Data
        for i in range(10):
            self.font_dict[f"{i}"] = img2dat.convert_image_to_data(f"{DisplayDriver.FONT_LOCATION}{i}.png")
        for char in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            self.font_dict[f"{char}"] = img2dat.convert_image_to_data(f"{DisplayDriver.FONT_LOCATION}{char}.png")
        self.font_dict["special"] = img2dat.convert_image_to_data(f"{DisplayDriver.FONT_LOCATION}special.png")

    def __del__(self):
        self.write_command(DisplayDriver.CMD_DISPLAY_OFF)
        time.sleep(0.12)
        self.write_command(DisplayDriver.CMD_SLEEP_IN)
        time.sleep(0.12)
        self.reset_device()
        time.sleep(0.12)
        self.spi.close()
        GPIO.cleanup()

    def reset_device(self):
        GPIO.output(self.RST_PIN, GPIO.LOW)
        time.sleep(0.12)
        GPIO.output(self.RST_PIN, GPIO.HIGH)

    def write_command(self, cmd_code, param = None):
        GPIO.output(self.DC_PIN, GPIO.LOW)
        cmd_code = cmd_code if isinstance(cmd_code, list) else [cmd_code]
        self.spi.xfer2(cmd_code)
        if param is not None:
            self.write_data(param)

    def write_data(self, data):
        GPIO.output(self.DC_PIN, GPIO.HIGH)
        data = data if isinstance(data, list) else [data]
        # Limit data transfer to 4096 bytes per a transfer
        if (len(data) < 250):
            self.spi.writebytes2(data)
        else:
            transfer_count = int(len(data) / 250)
            for i in range(transfer_count):
                self.spi.writebytes2(data[i*250:(i+1)*250])
            self.spi.writebytes2(data[(transfer_count)*250:len(data)])
            print(transfer_count*250)
            print(len(data))
            print(data[-2], data[-1])

    def split_to_bytes(self, data):
            return [(data & 0xFF00) >> 8, (data & 0xFF)]

    def set_window(self, x, y, width, height):
        x0 = x + DisplayDriver.DEVICE_COL_OFFSET
        y0 = y + DisplayDriver.DEVICE_ROW_OFFSET
        x1 = x0 + width - 1
        y1 = y0 + height - 1
        col_data = self.split_to_bytes(x0) + self.split_to_bytes(x1)
        row_data = self.split_to_bytes(y0) + self.split_to_bytes(y1)
        self.write_command(DisplayDriver.CMD_COL_ADDR_SET, col_data)
        self.write_command(DisplayDriver.CMD_ROW_ADDR_SET, row_data)
    
    def render_image(self, x, y, width, height, image_data):
        if (len(image_data) != width * height):
            print(f"ERROR: render data doesn't match window size(window: {width * height}, data: {len(image_data)})")
        self.set_window(x, y, width, height)
        self.write_command(DisplayDriver.CMD_MEM_WRITE, image_data)
    
    def render_square(self, x, y, width, height, r5g6b5color):
        self.set_window(x, y, width, height)
        data = self.split_to_bytes(r5g6b5color) * (width * height)
        self.write_command(DisplayDriver.CMD_MEM_WRITE, data)
    
    def render_char(self, x, y, char):
        self.set_window(x, y, DisplayDriver.FONT_WIDTH, DisplayDriver.FONT_HEIGHT)
        self.write_command(DisplayDriver.CMD_MEM_WRITE, self.font_dict[char])


# SPEAKING
# LISTENING