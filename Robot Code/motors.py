import pyb
from pyb import Timer


tim4 = Timer(4, freq=1000)
tim2 = Timer(2, freq=1000)

# directia generala
M2X = tim4.channel(
    1,
    pyb.Timer.PWM,
    pin=pyb.Pin("P7")
)

# motor stanga
MLeft = tim2.channel(
    4,
    pyb.Timer.PWM,
    pin=pyb.Pin("P4")
)

# motor dreapta
MRight = tim2.channel(
    3,
    pyb.Timer.PWM,
    pin=pyb.Pin("P5")
)


class Motors:


    def forward(self, left=60, right=60):

        left = int(max(0, min(100, left)))
        right = int(max(0, min(100, right)))

        # forward
        M2X.pulse_width_percent(0)

        MLeft.pulse_width_percent(left)
        MRight.pulse_width_percent(right)


    def reverse(self, left=60, right=60):

        left = int(max(0, min(100, left)))
        right = int(max(0, min(100, right)))

        # reverse
        M2X.pulse_width_percent(100)

        MLeft.pulse_width_percent(100 - left)
        MRight.pulse_width_percent(100 - right)


    def rotate_left(self, speed=100):

        speed = int(max(0, min(100, speed)))

        M2X.pulse_width_percent(0)

        MLeft.pulse_width_percent(0)
        MRight.pulse_width_percent(speed)


    def rotate_right(self, speed=100):

        speed = int(max(0, min(100, speed)))

        M2X.pulse_width_percent(0)

        MLeft.pulse_width_percent(speed)
        MRight.pulse_width_percent(0)


    def move(self, left, right):

        left = int(max(0, min(100, left)))
        right = int(max(0, min(100, right)))

        M2X.pulse_width_percent(0)

        MLeft.pulse_width_percent(left)
        MRight.pulse_width_percent(right)


    def stop(self):

        MLeft.pulse_width_percent(0)
        MRight.pulse_width_percent(0)
        M2X.pulse_width_percent(0)
