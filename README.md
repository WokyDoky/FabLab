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

```python
# --- Constants ---
# Define constants for configuration values to make the code easier to read and modify.
NECK_SERVO_PIN = D2 # Pin identifier for the neck servo (controls head pivot)
INITIAL_NECK_POS = 94 # Starting position for the neck
NECK_SPEED = 3 # Speed setting for the servo
CAMERA_CENTER_X = 160 # Assumed horizontal center of the camera's view (30x240 camera, so 160 might be a typo, or based on a cropped/processed image width)
TRACKING_THRESHOLD = 70 # Minimum difference (delta) from center to trigger movement
NECK_STEP_SIZE = 10 # How much to move the neck servo each time
NECK_MIN_POS = 42 # Minimum allowed servo position (most left for Neck-X)
NECK_MAX_POS = 100 # Maximum allowed servo position (most right for Neck-X)
SLEEP_TIME = 500 # Milliseconds to pause after a servo movement

# --- Function Definitions ---

def initialize_neck(pin, start_pos, speed):
  """
  Sets the initial position and speed for the neck servo.
  Waits for the servo to reach the starting position.
  """
  print(f"Initializing neck servo on pin {pin}...")
  Servo.SetPosition(pin, start_pos)
  Servo.WaitForPositionEquals(pin, start_pos) # Wait for initial positioning
  Servo.SetSpeed(pin, speed);
  print(f"Neck servo initialized to position {start_pos} with speed {speed}.")

def adjust_neck_for_tracking(pin, object_center_x):
  """
  Calculates the tracking error (delta) and adjusts the neck servo
  left or right if the object is outside the threshold, respecting limits.
  Correction: Swapped Increment/Decrement logic to ensure correct movement direction.
  """
  # Calculate the difference between the object's horizontal center and the camera's assumed center.
  delta = object_center_x - CAMERA_CENTER_X
  print(f"Tracking Delta: {delta}")

  current_pos = Servo.GetPosition(pin)

  # Object is significantly to the LEFT of camera center (negative delta)
  # -> Move the neck RIGHT (Increment servo position value towards NECK_MAX_POS)
  if delta < -TRACKING_THRESHOLD:
    if current_pos < NECK_MAX_POS: # Check if neck is not already at its maximum right position
      print(f"Object Left ({delta}). Moving neck Right from {current_pos}.")
      Servo.Increment(pin, NECK_STEP_SIZE) # Move servo to the right
      sleep(SLEEP_TIME) # Pause to allow servo to move and system to stabilize
    else:
      print(f"Object Left ({delta}), but neck already at max right limit ({current_pos}).")

  # Object is significantly to the RIGHT of camera center (positive delta)
  # -> Move the neck LEFT (Decrement servo position value towards NECK_MIN_POS)
  elif delta > TRACKING_THRESHOLD:
    if current_pos > NECK_MIN_POS: # Check if neck is not already at its maximum left position
      print(f"Object Right ({delta}). Moving neck Left from {current_pos}.")
      Servo.Decrement(pin, NECK_STEP_SIZE) # Move servo to the left
      sleep(SLEEP_TIME) # Pause
    else:
      print(f"Object Right ({delta}), but neck already at min left limit ({current_pos}).")

  # Object is within the central threshold (close to center)
  else:
    # print(f"Object centered ({delta}). Holding position {current_pos}.") # Optional: for debugging
    pass # Do nothing if the object is centered

# --- Main Program Logic ---

# Initialize the neck servo system once at the start of the program
initialize_neck(NECK_SERVO_PIN, INITIAL_NECK_POS, NECK_SPEED)

print("Starting tracking loop...")
try:
  # Main control loop that runs continuously
  while True:
    # Check if the camera is currently tracking an object
    # (Assumes getVar("$CameraIsTracking") returns a boolean or equivalent)
    if getVar("$CameraIsTracking"):
      # Get the horizontal center position (x-coordinate) of the tracked object
      # (Assumes getVar("$CameraObjectCenterX") returns the x-coordinate)
      obj_x = getVar("$CameraObjectCenterX")

      # Ensure a valid position was retrieved
      if obj_x is not None:
        # Adjust the neck position based on the object's detected x-coordinate
        adjust_neck_for_tracking(NECK_SERVO_PIN, obj_x)
      else:
        # Log a warning if the object's center X could not be retrieved
        print("Warning: Could not retrieve $CameraObjectCenterX")
        # Optional: Consider adding a small delay here if this warning occurs frequently
        # import time
        # time.sleep(0.1)

    # Optional: If the camera is not tracking, a small delay can prevent the loop
    # from consuming excessive CPU resources.
    # else:
      # import time
      # time.sleep(0.05)

except KeyboardInterrupt:
  # Handle a Ctrl+C command to gracefully exit the program
  print("\nExiting program due to user request.")
  # Optional: Add cleanup code here, such as returning the servo to a neutral position.
  # Servo.SetPosition(NECK_SERVO_PIN, INITIAL_NECK_POS)
  # Servo.WaitForMove(NECK_SERVO_PIN) # Or Servo.WaitForPositionEquals


4.2. Code Explanation
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
