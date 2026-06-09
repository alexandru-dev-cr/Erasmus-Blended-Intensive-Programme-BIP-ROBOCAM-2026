# ROBOCAM 2026 — Computer Vision Ball-Collecting Robot

> **ROBOCAM** — Robot Competition based on Computer Vision and AI
> Hosted by the **Faculty of Computer Science, "Alexandru Ioan Cuza" University of Iași**

---

## Team & Results

*   **Alexandru-Teodor Livadariu** — Hardware & Software
*   **Cezar Codreanu** — Hardware & Software

 **Result: 7th place out of 14 competing teams 🏆**

---

## Project Overview

Our robot is a fully autonomous agent designed to detect, track, and collect colored balls scattered within an arena, then safely navigate back to deliver them to a designated "home" zone — all without any human intervention.

The project combines **real-time computer vision**, **magnetic compass navigation**, and **adaptive motor control**, running entirely on an OpenMV Cam H7 microcontroller.

---

## Software Architecture & File Responsibilities

The codebase is split into modular Python files, each handling a specific subsystem:

* `main.py` — The core brain; runs the main state machine that decides whether to search, attack, or go home.
* `camera.py` — Handles camera startup and captures real-time video frames.
* `cavision.py` — The vision system; uses color blob detection to spot and track the balls.
* `compass.py` — Reads the digital compass (via SPI) to calculate the robot's driving direction.
* `motors.py` — Controls the speed and direction of the wheels using PWM signals.
* `sensors.py` — Manages peripheral hardware: the IR ball-detector, wall sensor, and buzzer alerts.
* `CALIBRARE.txt` — A standalone utility script used to calibrate the compass against magnetic interference.

---

## ⚙️ Core Functionalities

### 1. Ball Detection (`cavision.py`)
Target tracking relies on color blob detection within the **LAB color space**. The system uses calibrated thresholds tuned for three distinct target colors: **Green**, **Red**, and **Yellow**. To filter out background noise, the script isolates the largest matching color blob in the frame and outputs its center coordinates, width, height, and pixel count.

### 2. Zig-Zag Search (`main.py`)
When no balls are visible, the robot defaults to an exploration routine. It executes a sweeping zig-zag pattern (alternating forward movement with slight left and right leaning arcs) to maximize arena coverage. While searching, it constantly monitors two inputs:
*   **Wall proximity** (via the analog IR sensor) to prevent collisions.
*   **Camera feed** to immediately break the search if a ball is spotted.

### 3. Attack Mode (`attack_mode()`)
As soon as a ball is spotted, the robot enters attack mode[cite: 1]. It uses a simple **Proportional (P) Controller** to stay locked onto the target[cite: 1]:

$$\text{Error} = \text{Ball Center} - \text{Frame Center}$$
$$\text{Correction} = \text{Error} \times K_p \quad (\text{where } K_p = 0.4)$$

This correction automatically adjusts the speed of the wheels, steering the robot directly into the ball until the internal IR sensor confirms it has been successfully caught[cite: 1].

### 4. Compass Navigation (`compass.py`)
The LIS3MDL magnetic compass provides orientation telemetry. At startup, the robot locks its initial direction as `HOME_HEADING`. After collecting a ball, it computes the heading error relative to home (normalized within the $[-180^\circ, 180^\circ]$ range) and applies a scaled correction factor to steer back precisely toward the starting base.

### 5. Delivery & Return Run
After securing a ball, the system switches to its delivery state:
1.  Aligns itself until the current heading matches `HOME_HEADING`.
2.  Drives forward, continuously adjusting its trajectory using compass feedback.
3.  Upon reaching the starting wall (detected by the analog IR sensor), it deposits the ball.
4.  Executes a quick escape maneuver (reversing combined with a circular rotation) before clearing its state and resuming the search loop.

### 6. Compass Calibration (`CALIBRARE.txt`)
To counter magnetic interference from the motors and chassis, the calibration script spins the robot $360^\circ$ for 10 seconds. It samples raw X/Y magnetic data to calculate hard-iron offsets and scaling factors, ensuring accurate heading data during the run.

---

## Hardware Stack

*   **Microcontroller:** OpenMV Cam H7 running MicroPython.
*   **Camera:** Onboard image sensor operating at QVGA resolution ($320 \times 240$) in RGB565 format.
*   **Magnetic Sensor:** LIS3MDL compass connected over SPI.
*   **Actuators:** 2× DC Motors driven via hardware PWM channels.
*   **Ball Capture Sensor:** Digital IR sensor configured with an internal pull-up resistor.
*   **Wall Detection Sensor:** Analog IR distance sensor mapped to an ADC pin.
*   **Audio Feedback:** Digital Piezo Buzzer for signaling events like calibrations or successful captures.

---

## Dependencies

The software is completely native to **MicroPython for OpenMV**. It relies strictly on built-in, hardware-optimized standard libraries: `sensor`, `pyb`, `math`, and `time`.