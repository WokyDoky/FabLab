# InMoov Humanoid Project: Current Build Documentation

## 1. Project Overview

This document outlines the current state of our InMoov humanoid robot build. The goal is to construct a full InMoov humanoid. Currently, we have a functional head, a custom-designed neck, and a torso. This documentation details the components, configurations, known issues, and software for these modules.

The original InMoov project and some base assembly instructions can be found at [inmoov.fr](https://inmoov.fr). This document focuses on our specific implementation, including deviations and custom modifications.

## 2. Head Assembly

The head assembly is based on the InMoov designs. It features actuated eyes, a moving jaw, and a pivoting neck mechanism.

### 2.1. Eye Mechanism
The head incorporates a two-axis eye mechanism, allowing for both horizontal (X) and vertical (Y) movement.

* **Left Eye:** Houses a camera with a resolution of 30 x 240 pixels.
* **Servos:** Both eyes are actuated by Corona DS929HV servos.
* **Wiring (Eyes):** Standard Black, Red, White servo cables.
* **Servo Configuration:**
    * **Eye X-Axis (Horizontal):**
        * Connected to Port: `D0`
        * Minimum Position: `64`
        * Maximum Position: `126`
    * **Eye Y-Axis (Vertical):**
        * Connected to Port: `D1`
        * Minimum Position: `19`
        * Maximum Position: `64`

### 2.2. Jaw Mechanism
The jaw is designed to open and close, actuated by a single servo.

* **Servo:** H-King HK15298.
* **Wiring (Jaw):** Brown, Red, Yellow servo cable.
* **Connected to Port:** `D6`
* **Known Issue:** The jaw exhibits bad tolerances and, as a result, does not close completely. This may require future adjustments or re-printing of parts.

### 2.3. Head Pivot (Neck-X Rotation)
The entire head can pivot horizontally (left and right).

* **Servo:** HS-805BB.
* **Wiring (Neck-X):** Twisted Black, Red, Yellow servo cable.
* **Connected to Port:** `D2`
* **Minimum Position:** `44`
* **Maximum Position:** `110`

## 3. Neck and Torso Assembly

The torso assembly follows the general InMoov instructions, which can be found at [InMoov Neck and Jaw Instructions](https://inmoov.fr/neck-and-jaw/). However, our neck mechanism features a custom design.

### 3.1. Custom Neck Design
Our neck utilizes a 3-piston system for head movement, differing from the standard InMoov neck.

* **Pistons:**
    1.  **Nodding Piston (1x):** Moves the head up and down.
    2.  **Yaw Pistons (2x):** Tilt the head left and right (referred to as "Right Yaw" and "Left Yaw"). These are configured to work as a master-slave system; as one contracts, the other extends.

### 3.2. Neck Servo Configuration and Details

* **Right Yaw Piston:**
    * **Servo Type:** H-King HK15298 (same as jaw servo).
    * **Connected to Port:** `D3` (This is the servo on the robot's right side; it would appear as the left servo if the torso is facing you).
    * **Minimum Position:** `44`
    * **Maximum Position:** `110`

* **Left Yaw Piston:**
    * **Servo Type:** H-King HK15298 (same as jaw servo).
    * **Connected to Port:** `D4`
    * **Minimum Position:** `49`
    * **Maximum Position:** `63`
    * **Critical Note:** The position ranges for the Left and Right Yaw servos are significantly different. This disparity could lead to operational problems if not carefully calibrated. **It is crucial to measure all tolerances and ranges meticulously before extensive operation to prevent binding or damage.**

* **Inside Neck Piston (Nodding):**
    * **Servo Type:** HS-805BB (same as Neck-X pivot servo).
    * **Connected to Port:** `D5`
    * **Minimum Position:** `33`
    * **Maximum Position:** `166`
    * **Known Issue:** The printed part that holds the screw for this piston has a split down the middle, making it prone to breaking under stress. This component may need reinforcement or re-design.

## 4. Head Tracking System

The head tracking system uses the left eye camera to identify and follow objects. The logic is implemented in Python.

### 4.1. Python Code for Head Tracking

can be found in "eyeTracking.py"


### 4.2. Code Explanation
Constants:
NECK_SERVO_PIN: Specifies the digital port (D2) for the head pivot servo.
INITIAL_NECK_POS: The default starting position (94) for the neck pivot.
NECK_SPEED: Sets the movement speed/acceleration for the neck servo.
CAMERA_CENTER_X: Defines the target X-coordinate (160) for the camera's field of view. Note: Given a 30x240 pixel camera, the true horizontal center would be 120 if using the full width. This value might be based on a cropped image or specific calibration.
TRACKING_THRESHOLD: The tolerance (70 pixels) for how far an object can be from CAMERA_CENTER_X before the neck moves.
NECK_STEP_SIZE: The amount (10 units) the servo moves in each adjustment step.
NECK_MIN_POS / NECK_MAX_POS: Defines the operational limits (42 to 100) for the neck pivot servo to prevent over-rotation.
SLEEP_TIME: A pause (500 ms) after each servo movement to allow the physical movement to complete and prevent rapid, jerky motions.
initialize_neck(pin, start_pos, speed) Function:
This function is called once at startup.
It sets the neck servo to its INITIAL_NECK_POS.
Servo.WaitForPositionEquals() ensures the script waits until the servo has physically reached the target position before proceeding.
It then sets the NECK_SPEED for subsequent movements.
adjust_neck_for_tracking(pin, object_center_x) Function:
This is the core logic for tracking.
It calculates delta, the difference between the detected object's X-coordinate (object_center_x) and the desired CAMERA_CENTER_X.
Movement Logic:
If delta is less than -TRACKING_THRESHOLD (object is significantly to the left), the function attempts to move the neck to the right by NECK_STEP_SIZE (incrementing the servo position), provided it's not already at NECK_MAX_POS.
If delta is greater than TRACKING_THRESHOLD (object is significantly to the right), it moves the neck to the left (decrementing servo position), provided it's not at NECK_MIN_POS.
The original code comments noted a correction: "Swapped Increment/Decrement to fix direction issue." This means the current logic (incrementing to move right, decrementing to move left, assuming higher servo values mean "right") is the corrected version.
sleep(SLEEP_TIME) is used after a movement command, replacing Servo.WaitForMove from potential earlier versions. This provides a simple delay.
Main Program Logic:
Calls initialize_neck() to set up the servo.
Enters an infinite while True loop for continuous operation.
Inside the loop, it checks getVar("$CameraIsTracking"). This implies an external system or variable that indicates if the camera's object detection is active.
If tracking, it retrieves the object's X-coordinate using getVar("$CameraObjectCenterX").
If obj_x is valid, it calls adjust_neck_for_tracking() to move the head.
Includes a try...except KeyboardInterrupt block to allow the user to stop the script cleanly using Ctrl+C.
5. Future Considerations and Todos
Address jaw tolerance issues.
Reinforce or redesign the nodding piston's screw holder.
Carefully calibrate Left and Right Yaw neck servos due to differing position ranges.
Verify CAMERA_CENTER_X constant against actual camera output and processing.
Further refine TRACKING_THRESHOLD and NECK_STEP_SIZE for smoother tracking.
Consider adding feedback or limits for eye servos in the tracking logic if they also participate
