
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
