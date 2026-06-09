import math
import time
from pyb import SPI, Pin



cs = Pin("P3", Pin.OUT_PP)
cs.high()

spi = SPI(2, SPI.MASTER, baudrate=100000, polarity=0, phase=0)



WHO_AM_I = 0x0F
CTRL_REG1 = 0x20
CTRL_REG2 = 0x21
CTRL_REG3 = 0x22
CTRL_REG4 = 0x23
MAG_X_L = 0x28
MAG_X_H = 0x29
MAG_Y_L = 0x2A
MAG_Y_H = 0x2B


class Compass:

    def __init__(self):
        self.X_offset = -1774.5
        self.Y_offset = 3411.5
        self.X_scale = 1146.5
        self.Y_scale = 1086.5
        self.init_sensor()


    def writeSPI(self, address, value):
        cs.low()
        spi.send(bytearray([address & 0x7F, value]))
        cs.high()

    def readSPI(self, address):
        cs.low()
        spi.send(address | 0x80)
        val = spi.recv(1)
        cs.high()
        return val[0]


    def init_sensor(self):
        self.writeSPI(CTRL_REG1, 0x70)
        self.writeSPI(CTRL_REG2, 0x00)
        self.writeSPI(CTRL_REG3, 0x00)
        self.writeSPI(CTRL_REG4, 0x0C)
        time.sleep_ms(100)


    def read_mag_raw(self):
        x = (self.readSPI(MAG_X_H) << 8) | self.readSPI(MAG_X_L)
        y = (self.readSPI(MAG_Y_H) << 8) | self.readSPI(MAG_Y_L)

        if x > 32767:
            x -= 65536
        if y > 32767:
            y -= 65536

        return x, y


    def set_calibration(self, X_offset, Y_offset, X_scale, Y_scale):
        self.X_offset = X_offset
        self.Y_offset = Y_offset
        self.X_scale = X_scale
        self.Y_scale = Y_scale


    def heading(self):
        x, y = self.read_mag_raw()

        x = (x - self.X_offset) / self.X_scale
        y = (y - self.Y_offset) / self.Y_scale

        angle = math.atan2(y, x) * 180 / math.pi

        if angle < 0:
            angle += 360

        return angle
