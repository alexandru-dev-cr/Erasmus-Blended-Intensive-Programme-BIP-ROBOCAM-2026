
class Vision:

    def __init__(self):


        self.green_threshold = (100, 0, -15, -128, 92, 13)


        self.red_threshold = (0, 100, 24, 127, -128, 127)


        self.yellow_threshold = (100, 6, -26, 55, 65, 127)

    def find_ball(self, img):



        blobs = img.find_blobs(


             [ self.green_threshold,
               self.red_threshold,
               self.yellow_threshold],

            pixels_threshold=80,
            area_threshold=80,

            merge=True
        )

        if not blobs:
            return None

        biggest = max(
            blobs,
            key=lambda b: b.pixels()
        )

        return {

            "cx": biggest.cx(),
            "cy": biggest.cy(),

            "w": biggest.w(),
            "h": biggest.h(),

            "pixels": biggest.pixels(),

            "rect": biggest.rect()
        }
