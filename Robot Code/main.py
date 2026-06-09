from motors import Motors
from compass import Compass
from sensors import Sensors
from camera import Camera
from cavision import Vision
import pyb

#INIT

motors = Motors()
compass = Compass()
sensors = Sensors()
camera = Camera()
vision = Vision()


#HOME

HOME_HEADING = compass.heading()
print(f"HOME HEADING SET (raw): {HOME_HEADING:.1f}°")

COMPASS_OFFSET = -2

HOME_HEADING = HOME_HEADING + COMPASS_OFFSET

if HOME_HEADING >= 360:
    HOME_HEADING -= 360
elif HOME_HEADING < 0:
    HOME_HEADING += 360

print(f"HOME HEADING SET (calibrat): {HOME_HEADING:.1f}°")

BACK_HEADING = (HOME_HEADING + 180) % 360
print(f"BACK HEADING (start direction): {BACK_HEADING:.1f}°")


# ANGLE ERROR

def angle_error(target, current):
    err = target - current
    while err > 180:
        err -= 360
    while err < -180:
        err += 360
    return err


# AFIȘARE

def draw_status_on_camera(img, phase, ball_info=""):
    img.draw_string(10, 10, f"PHASE: {phase}", color=(255, 0, 0), scale=2)

    if ball_info:
        img.draw_string(10, 40, ball_info, color=(0, 255, 0), scale=1)
    else:
        img.draw_string(10, 40, "No ball detected", color=(0, 0, 255), scale=1)

    current_heading = compass.heading()
    img.draw_string(10, 70, f"Heading: {current_heading:.1f}", color=(255, 255, 0), scale=1)
    img.draw_string(10, 100, f"Target: {HOME_HEADING:.1f}", color=(0, 255, 255), scale=1)

    wall_dist = sensors.distance_cm()
    if wall_dist < 25:
        img.draw_string(10, 130, f"WALL: {wall_dist}cm", color=(255, 0, 255), scale=1)


# DEBLOCARE


def unblock_robot():

    motors.reverse(100, 100)
    pyb.delay(200) 

    motors.move(0, 100)
    pyb.delay(830)
    motors.stop()
    pyb.delay(50)

    if quick_scan_wall():
        print("Minge Gasita")
        return True
    return False


# CAUTARE ZIG ZAG

BASE = 100
DELTA = 32
T = 350

def forward():
    motors.move(BASE, BASE)
    pyb.delay(100)

def lean_left():
    motors.move(BASE - DELTA + 10, BASE + DELTA)
    pyb.delay(T + 400)

def lean_right():
    motors.move(BASE + DELTA, BASE - DELTA - 15)
    pyb.delay(T + 420)

def zigzag_search_with_ball_check():
    print("Cautare Zig-Zag")

    search_start = pyb.millis()
    timeout = 3000

    for cycle in range(10):

        if sensors.wall_close(11):
            print(f" Perete detectat in {sensors.distance_cm()}cm!")
            motors.stop()
            unblock_robot()
            continue

       
        if pyb.millis() - search_start > timeout:
            print(" Timeout! 360..")
            if recover_lost_ball():
                return True
            else:
                print("Bila nu a fost gasita ,cautam din nou")
                search_start = pyb.millis()
                continue

  
        img = camera.get_frame()
        ball = vision.find_ball(img)
        if ball is not None:
            draw_status_on_camera(img, "Minge Gasita", f"cx={ball['cx']}")
            print(f"*** Minge Gasita! ***")
            motors.stop()
            return True

        forward()

       
        if sensors.wall_close(11):
            print(f" Perete in {sensors.distance_cm()}cm!")
            motors.stop()
            unblock_robot()
            continue

        img = camera.get_frame()
        ball = vision.find_ball(img)
        if ball is not None:
            draw_status_on_camera(img, "Minge Gasita", f"cx={ball['cx']}")
            motors.stop()
            return True

        lean_left()

        if sensors.wall_close(11):
            print(f" Perete in {sensors.distance_cm()}cm!")
            motors.stop()
            unblock_robot()
            continue

        img = camera.get_frame()
        ball = vision.find_ball(img)
        if ball is not None:
            draw_status_on_camera(img, "Minge Gasita", f"cx={ball['cx']}")
            motors.stop()
            return True

        forward()

        if sensors.wall_close(11):
            print(f" Perete in {sensors.distance_cm()}cm!")
            motors.stop()
            unblock_robot()
            continue

        img = camera.get_frame()
        ball = vision.find_ball(img)
        if ball is not None:
            draw_status_on_camera(img, "Minge Gasita", f"cx={ball['cx']}")
            motors.stop()
            return True

        lean_right()

        if sensors.wall_close(11):
            print(f" Perete in {sensors.distance_cm()}cm!")
            motors.stop()
            unblock_robot()
            continue

        img = camera.get_frame()
        ball = vision.find_ball(img)
        if ball is not None:
            draw_status_on_camera(img, "Minge Gasita", f"cx={ball['cx']}")
            motors.stop()
            return True

        print(f"Cycle {cycle+1}/10 - no ball")

    motors.stop()
    return False


# PRINDE BILA


FRAME_CENTER = 160
BASE_SPEED = 100
Kp = 0.4
DEADZONE = 15

def attack_mode():
    print("Mod Atac")

    no_ball_counter = 0
    max_no_ball = 25

    while True:
   
        if sensors.wall_close(11):
            print(f" Perete in {sensors.distance_cm()}cm!")
            if unblock_robot():
                return attack_mode()
            else:
                return False

        img = camera.get_frame()
        ball = vision.find_ball(img)

        if ball is None:
            no_ball_counter += 1
            draw_status_on_camera(img, "Atac", f"NO BALL ({no_ball_counter})")
            pyb.delay(10)

            if no_ball_counter > max_no_ball:
                print("Minge Pierduta!")
                return False
            continue

        no_ball_counter = 0
        cx = ball["cx"]
        error = cx - FRAME_CENTER

        draw_status_on_camera(img, "Atac", f"err={error}")
        img.draw_circle(cx, ball["cy"], 10, color=(0, 255, 0), thickness=2)
        img.draw_line(FRAME_CENTER, 0, FRAME_CENTER, 240, color=(255, 0, 0))

        if sensors.has_ball():
            pyb.delay(50)
            print("  Stabilizare...")
            motors.move(30, 30)
            pyb.delay(180)
            pyb.delay(40)

            sensors.beep(200)
            print("Capturata si stabilizata")
            draw_status_on_camera(img, "Capturata", "Minge in cupa")
            return True


        abs_err = abs(error)

        if abs_err > DEADZONE:
            turn = error * Kp
            left = BASE_SPEED + turn
            right = BASE_SPEED - turn
            left = max(20, min(100, left))
            right = max(20, min(100, right))
        else:
            left = BASE_SPEED
            right = BASE_SPEED

        motors.move(int(left), int(right))
        pyb.delay(40)


# DUCE MINGEA LA HOME


def deliver_ball_to_home():
   
    print("Minge spre casa ")

    if not sensors.has_ball():
        print("Mingea nu este in cupa, scanez 360")
        if recover_lost_ball():
            print("Minge recuperata ,continui livrarea")
        else:
            print("Minge pierduta ,caut din nou")
            return False

    current = compass.heading()
    err = angle_error(HOME_HEADING, current)

   
    if abs(err) > 90:
        print(f"  Intorc (err={err:.1f}°)")

        if err > 0:
            print("  Stanga")
            motors.move(20, 60)
        else:
            print("  Dreapta")
            motors.move(60, 20)

        start_time = pyb.millis()
        while True:
            if not sensors.has_ball():
                print("Minge pierduta in timpul intoarcerii")
                return recover_lost_ball()

            current = compass.heading()
            err = angle_error(HOME_HEADING, current)

            if abs(err) < 10:
                print(f"  Aliniata (err={err:.1f}°)")
                break

            if pyb.millis() - start_time > 3000:
                print(" Stop intoarcere")
                break

            pyb.delay(50)

        motors.stop()
        pyb.delay(50)

 
    print(" Viteza max spre perete")

    for step in range(200):
        if not sensors.has_ball():
            print("Bila pierduta din senzor ,asteptam 150ms")
            pyb.delay(150)
            if not sensors.has_ball():
                print("Bila inca lipseste initializam recuperarea")
                motors.stop()
                return recover_lost_ball()
            else:
                print("Semnal minge recuperat,continuam drumul.")

        img = camera.get_frame()
        current = compass.heading()
        err = angle_error(HOME_HEADING, current)

        draw_status_on_camera(img, "DELIVERING", f"err={err:.1f}°")

        correction = err * 0.10
        left = 100 + correction
        right = 100 - correction
        left = max(50, min(100, left))
        right = max(50, min(100, right))

        motors.move(int(left), int(right))
        pyb.delay(30)

        if sensors.wall_close(15):
            print("Perete!")
            motors.stop()
            return True

    motors.stop()
    return True

# =========================================
# DROP BALL ȘI ROTAȚIE CIRCULARĂ
# =========================================

def drop_and_circular_return():
    print("DROP & RETURN")

    pyb.delay(50)

    motors.reverse(100, 100)
    pyb.delay(150)

    print("return")

    motors.move(0, 100)
    pyb.delay(800)

    motors.stop()

    print("Pregatit!")
    sensors.beep(100)

# =========================================
# QUICK SCAN - WALL
# =========================================

def quick_scan_wall():
    """Scanare rapidă când lovește peretele"""
    print("=== QUICK SCAN (WALL MODE) ===")

    print("in FATA")
    img = camera.get_frame()
    ball = vision.find_ball(img)
    if ball is not None:
        print(f" Minge gasita in fata!")
        return True

    print(" STG")
    motors.rotate_left(100)
    pyb.delay(310)
    motors.stop()
    pyb.delay(30)

    img = camera.get_frame()
    ball = vision.find_ball(img)
    if ball is not None:
        print(f" Minge gasita in stanga!")
        motors.rotate_right(100)
        pyb.delay(310)
        motors.stop()
        return True

    print("DRP")
    motors.rotate_right(100)
    pyb.delay(620)
    motors.stop()
    pyb.delay(30)

    img = camera.get_frame()
    ball = vision.find_ball(img)
    if ball is not None:
        print(f"Minge gasita in dreapta!")
        motors.rotate_left(100)
        pyb.delay(310)
        motors.stop()
        return True

    print("Centrare")
    motors.rotate_left(100)
    pyb.delay(200)
    motors.stop()

    print("Nu am gasit mingea")
    return False

# =========================================
# QUICK SCAN - SIMPLE
# =========================================

def quick_scan_simple():
   
    print("Scanare Rapida")

    start_heading = compass.heading()
    print(f"DEBUG: start_heading={start_heading:.1f}°, BACK_HEADING={BACK_HEADING:.1f}°")

    print("in Fata")
    img = camera.get_frame()
    ball = vision.find_ball(img)
    if ball is not None:
        print(f" Bila gasita in fata!")
        return True

    print("in stanga")
    motors.rotate_left(100)
    pyb.delay(295)
    motors.stop()
    pyb.delay(30)

    img = camera.get_frame()
    ball = vision.find_ball(img)
    if ball is not None:
        print(f" Bila gasita in stanga!")
        motors.rotate_right(100)
        pyb.delay(450)
        motors.stop()
        return True

    print("DRP")
    motors.rotate_right(100)
    pyb.delay(590)
    motors.stop()
    pyb.delay(30)

    img = camera.get_frame()
    ball = vision.find_ball(img)
    if ball is not None:
        print(f"Bila gasita in dreapta!")
        motors.rotate_left(100)
        pyb.delay(295)
        motors.stop()
        return True

    print(" Nici o bila gasita ,return backheading")
    current = compass.heading()
    err = angle_error(BACK_HEADING, current)

    if abs(err) > 10:
        print(f"  Rotatie spre BACK_HEADING (err={err:.1f}°)")
        if err > 0:
            motors.rotate_left(70)
        else:
            motors.rotate_right(70)
        pyb.delay(int(abs(err) * 5))
        motors.stop()
    else:
        print("  Deja spre BACK_HEADING")

    print("  Nici o bila gasita ,cautare zig zag")
    return False

# =========================================
# RECOVER LOST BALL
# =========================================

def recover_lost_ball():
    
    print("360 ")

    motors.rotate_left(100)
    start_time = pyb.millis()

    while pyb.millis() - start_time < 1650:
        img = camera.get_frame()
        ball = vision.find_ball(img)
        if ball is not None:
            print(f" Minge Gasita ,atac")
            motors.stop()
            return attack_mode()

    motors.stop()
    print("Mingea nu a fost gasita")
    return False

# =========================================
# GO HOME
# =========================================

def go_home():
    
    print("Orientare spre casa")

    for step in range(80):
        current = compass.heading()
        err = angle_error(HOME_HEADING, current)

        if abs(err) < 10:
            print("Deja sunt spre casa")
            break

        if err > 0:
            motors.rotate_left(50)
        else:
            motors.rotate_right(50)

        pyb.delay(30)

    motors.stop()
    pyb.delay(100)

# =========================================
# MAIN
# =========================================

def main():
    print("\n" + "="*50)
    print("ROBOT STARTING")
    print(f"Home heading: {HOME_HEADING:.1f}°")
    print("="*50 + "\n")

    ball_count = 0

    while True:
        if sensors.has_ball():
            print(" Minge in cupa,livrez")
            deliver_ball_to_home()
            drop_and_circular_return()
            ball_count += 1
            print(f"Ball #{ball_count} livrata cu succes!")
            pyb.delay(500)

            
            print("\n Pregatit de bila urmatoare,cautare zig zag---")
            continue 

        print(f"\n  Cautare Zig Zag #{ball_count + 1} ")
        ball_found = zigzag_search_with_ball_check()

        if not ball_found:
            print("Nici o bila gasita , ma rotesc")
            motors.rotate_left(40)
            pyb.delay(2000)
            motors.stop()
            continue

        if not attack_mode():
            print("Atac esuat ,incerc din nou")
            continue

        ball_count += 1
        print(f"Ball #{ball_count} Bila capturata ,Livrez!")
        deliver_ball_to_home()
        drop_and_circular_return()

if __name__ == "__main__":
    main()