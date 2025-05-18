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
This Python code is designed to control a servo motor, specifically a "neck" servo, to make a camera (or a device with a camera) automatically track a moving object. It does this by adjusting the neck's horizontal angle to keep the detected object in the center of the camera's view.

#### 4.2.1. Function Definitions (`# --- Function Definitions ---`)

#### `initialize_neck(pin, start_pos, speed)`

* **Purpose**: This function sets up the neck servo at the beginning of the program.
* **Parameters**:
    * `pin`: The pin the servo is connected to.
    * `start_pos`: The desired initial position.
    * `speed`: The desired movement speed.
* **Actions**:
    * Prints an initialization message.
    * `Servo.SetPosition(pin, start_pos)`: Sends a command to the servo library to move the servo on the specified `pin` to the `start_pos`. (This implies the existence of a `Servo` object or module with these methods).
    * `Servo.WaitForPositionEquals(pin, start_pos)`: Pauses the execution of the script until the servo on the given `pin` reports that it has reached the `start_pos`. This ensures the servo is in place before proceeding.
    * `Servo.SetSpeed(pin, speed)`: Sets the movement speed for the servo.
    * Prints a confirmation message.

#### `adjust_neck_for_tracking(pin, object_center_x)`

* **Purpose**: This is the core logic for tracking. It determines if and how the neck servo should move based on the detected object's horizontal position.
* **Parameters**:
    * `pin`: The pin the servo is connected to.
    * `object_center_x`: The current horizontal (x-coordinate) position of the center of the tracked object, as detected by the camera.
* **Actions**:
    1.  `delta = object_center_x - CAMERA_CENTER_X`: Calculates the "error" or difference between the object's current horizontal position and the desired center of the camera's view.
        * A negative `delta` means the object is to the left of the center.
        * A positive `delta` means the object is to the right of the center.
        * A `delta` near zero means the object is centered.
    2.  `current_pos = Servo.GetPosition(pin)`: Gets the current reported position of the servo.
    3.  **Movement Logic**:
        * `if delta < -TRACKING_THRESHOLD`: If the object is significantly to the *left* (delta is more negative than the negative threshold).
            * `if current_pos < NECK_MAX_POS`: Checks if the neck is not already at its maximum *right* limit.
            * `Servo.Increment(pin, NECK_STEP_SIZE)`: Moves the neck servo to the *right* by `NECK_STEP_SIZE`. The comment correctly notes that to move the camera view to the left (to follow an object that is left of center), the servo itself needs to move to bring the camera view towards the object. The code logic "Move neck Right" is correct for this scenario if "Increment" increases the servo's angular value, and a higher angular value corresponds to the neck pointing more to its right.
            * `sleep(SLEEP_TIME)`: Pauses.
        * `elif delta > TRACKING_THRESHOLD`: If the object is significantly to the *right* (delta is more positive than the threshold).
            * `if current_pos > NECK_MIN_POS`: Checks if the neck is not already at its maximum *left* limit.
            * `Servo.Decrement(pin, NECK_STEP_SIZE)`: Moves the neck servo to the *left* by `NECK_STEP_SIZE`.
            * `sleep(SLEEP_TIME)`: Pauses.
        * `else`: If the object is within the `TRACKING_THRESHOLD` (i.e., considered centered), it does nothing (`pass`).

#### 4.2.2. Main Program Logic (`# --- Main Program Logic ---`)

* **Initialization**:
    * `initialize_neck(NECK_SERVO_PIN, INITIAL_NECK_POS, NECK_SPEED)`: Calls the initialization function once at the start to set up the neck servo.
* **Tracking Loop**:
    * `print("Starting tracking loop...")`
    * `try...except KeyboardInterrupt`: This structure allows the program to run an infinite loop but be stopped gracefully by pressing `Ctrl+C` on the keyboard.
    * `while True:`: This creates an infinite loop, meaning the tracking logic will run continuously until the program is interrupted.
        * `if getVar("$CameraIsTracking")`: Checks a system variable (presumably from the environment the script is running in, like a robot's operating system or a specific vision processing software). This variable indicates whether the camera system is currently successfully tracking any object.
            * `obj_x = getVar("$CameraObjectCenterX")`: If the camera is tracking, it retrieves another system variable, `$CameraObjectCenterX`, which is assumed to hold the horizontal coordinate of the tracked object's center.
            * `if obj_x is not None`: Checks if a valid x-coordinate was retrieved.
                * `adjust_neck_for_tracking(NECK_SERVO_PIN, obj_x)`: Calls the function to adjust the neck servo based on the object's position.
            * `else`: If `obj_x` couldn't be retrieved, it prints a warning.
        * The commented-out `else` block for `if getVar("$CameraIsTracking")` suggests an optional small delay if the camera is not tracking, to reduce CPU usage by not looping too rapidly.
* **Graceful Exit**:
    * `except KeyboardInterrupt:`: If `Ctrl+C` is pressed.
        * `print("\nExiting program due to user request.")`: Informs the user.
        * The commented-out lines suggest optional cleanup actions, like returning the servo to its initial position before exiting.

#### Assumptions and Dependencies:

* **Servo Library**: The code relies on an external `Servo` object or module that is provided by the "arc" ez robot software. 
* **`sleep()` function**: It uses a `sleep()` function to pause execution. The argument is in milliseconds.
* **`getVar()` function**: This function is used to read variables from the system or environment where the script is running (e.g., `$CameraIsTracking`, `$CameraObjectCenterX`). Implmenetaion provided by "ARC"
* **`D2`**: This implies a hardware context where `D2` is a recognized identifier for a digital pin.

