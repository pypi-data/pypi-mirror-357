import spidev
from gpiozero import DigitalOutputDevice
from PIL import Image, ImageDraw
import time
import numpy as np

class ST7789VW:

    # setup display
    def __init__(self, width=240, height=240, spi_bus=0, spi_device=0,
                 dc_pin=25, rst_pin=27, bl_pin=18, rotation=0, spi_speed_hz=62500000):
        self.width = width
        self.height = height
        self.rotation = rotation

        # setup pins
        self.dc = DigitalOutputDevice(dc_pin)
        self.rst = DigitalOutputDevice(rst_pin)
        self.bl = DigitalOutputDevice(bl_pin)

        # setup SPI
        self.spi = spidev.SpiDev()
        self.spi.open(spi_bus, spi_device)
        self.spi.max_speed_hz = spi_speed_hz
        self.spi.mode = 0b11

        # initialize display
        self._reset()
        self._init_display()
        self.bl.on()

    # method to reset display
    def _reset(self):
        self.rst.on()
        time.sleep(0.1)
        self.rst.off()
        time.sleep(0.1)
        self.rst.on()
        time.sleep(0.1)

    # send command to display
    def _write_command(self, cmd):
        self.dc.off()
        self.spi.writebytes([cmd])

    # send data to display
    def _write_data(self, data):
        self.dc.on()
        if isinstance(data, int):
            self.spi.writebytes([data])
        else:
            max_chunk = 2048
            for i in range(0, len(data), max_chunk):
                self.spi.writebytes(data[i:i + max_chunk])

    # method to complete initialization routine
    def _init_display(self):
        self._write_command(0x36)
        rotation_modes = [0x00, 0x60, 0xC0, 0xA0]
        self._write_data(rotation_modes[self.rotation % 4])

        self._write_command(0x3A) 
        self._write_data(0x05)

        self._write_command(0xB2)
        self._write_data([0x0C, 0x0C, 0x00, 0x33, 0x33])

        self._write_command(0xB7)
        self._write_data(0x35)

        self._write_command(0xBB)
        self._write_data(0x19)

        self._write_command(0xC0)
        self._write_data(0x2C)

        self._write_command(0xC2)
        self._write_data(0x01)

        self._write_command(0xC3)
        self._write_data(0x12)

        self._write_command(0xC4)
        self._write_data(0x20)

        self._write_command(0xC6)
        self._write_data(0x0F)

        self._write_command(0xD0)
        self._write_data([0xA4, 0xA1])

        self._write_command(0xE0)
        self._write_data([0xD0, 0x08, 0x11, 0x08, 0x0C, 0x15, 0x39, 0x33,
                          0x50, 0x36, 0x13, 0x14, 0x29, 0x2D])

        self._write_command(0xE1)
        self._write_data([0xD0, 0x08, 0x10, 0x08, 0x06, 0x06, 0x39, 0x44,
                          0x51, 0x0B, 0x16, 0x14, 0x2F, 0x31])

        self._write_command(0x21)
        self._write_command(0x11)
        time.sleep(0.12)
        self._write_command(0x29)

    # method to setup size of display
    def _set_window(self, x0, y0, x1, y1):
        self._write_command(0x2A)
        self._write_data([x0 >> 8, x0 & 0xFF, x1 >> 8, x1 & 0xFF])

        self._write_command(0x2B)
        self._write_data([y0 >> 8, y0 & 0xFF, y1 >> 8, y1 & 0xFF])

        self._write_command(0x2C)

    # method to show image on display
    def display(self, image: Image.Image):
        if image.mode != 'RGB':
            image = image.convert('RGB')
        image = image.resize((self.width, self.height))

        pixel_data = np.asarray(image).astype(np.uint16)
        pixel565 = (((pixel_data[:, :, 0] & 0xF8) << 8) |
                    ((pixel_data[:, :, 1] & 0xFC) << 3) |
                    (pixel_data[:, :, 2] >> 3))

        pixel_bytes = np.dstack(((pixel565 >> 8) & 0xFF, pixel565 & 0xFF)).flatten().tolist()

        self._set_window(0, 0, self.width - 1, self.height - 1)
        self._write_data(pixel_bytes)

    # method to clear display
    def clear(self, color=(0, 0, 0)):
        image = Image.new("RGB", (self.width, self.height), color)
        self.display(image)

    # method to close connection
    def close(self):
        self.spi.close()
        self.dc.close()
        self.rst.close()
        self.bl.close()

