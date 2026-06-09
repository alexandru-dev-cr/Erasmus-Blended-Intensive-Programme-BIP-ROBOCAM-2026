import sensor
import time

class Camera:

    def __init__(self):

        sensor.reset()

        sensor.set_pixformat(sensor.RGB565)

       
        sensor.set_framesize(sensor.QVGA)

        sensor.set_vflip(True)
        sensor.set_hmirror(True)

        sensor.skip_frames(time=2000)

        self.clock = time.clock()

    def get_frame(self):

        self.clock.tick()

        return sensor.snapshot()

    def fps(self):

        return self.clock.fps()