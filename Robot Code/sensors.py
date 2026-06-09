import pyb
from pyb import Pin


class Sensors:

    def __init__(self):



        self.ball_sensor = Pin(
            "P8",
            Pin.IN,
            Pin.PULL_UP
        )



        self.wall_sensor = pyb.ADC(
            pyb.Pin("P6")
        )



        self.buzzer = Pin(
            "P9",
            Pin.OUT_PP
        )



        self.points = [

            (3950, 5),
            (2550, 10),
            (1800, 15),
            (1400, 20),
            (1100, 25),
            (1000, 30)
        ]



    def has_ball(self):

        # fascicul intrerupt
        return self.ball_sensor.value() == 1



    def raw_distance(self):

        return self.wall_sensor.read()



    def distance_cm(self):

        raw = self.raw_distance()

        for i in range(len(self.points) - 1):

            x0, y0 = self.points[i]
            x1, y1 = self.points[i + 1]

            if x1 <= raw <= x0:

                dist = y0 + (
                    (y1 - y0)
                    * (raw - x0)
                    / (x1 - x0)
                )

                return int(dist)

        if raw > self.points[0][0]:
            return self.points[0][1]

        if raw < self.points[-1][0]:
            return self.points[-1][1]

        return 999



    def wall_close(self, limit=10):

        return self.distance_cm() < limit



    def beep(self, duration=100):

        self.buzzer.high()

        pyb.delay(duration)

        self.buzzer.low()
