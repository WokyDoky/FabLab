
class Config:
    """Holds all static configuration variables for the game."""
    # Screen dimensions
    SCREEN_WIDTH = 600
    SCREEN_HEIGHT = 400

    # Colors (R, G, B)
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    BLUE = (0, 0, 255)
    GREEN = (0, 255, 0)
    GRAY = (209, 209, 209)
    NICE_BLUE = (0, 153, 153)
    DARK_GRAY = (128, 128, 128)

    # Box properties
    BOX_WIDTH = 400
    BOX_HEIGHT = 300
    BORDER_WIDTH = 2
    BOX_COLOR = WHITE
    BORDER_COLOR = BLACK

    # Ball properties
    BALL_RADIUS = 20
    BALL_COLOR = RED
    BALL_SPEED = 6
    BALL_ACCELERATION = 0.2

    # Target Area properties
    TARGET_WIDTH = 50
    TARGET_HEIGHT = 50
    TARGET_COLOR_NORMAL = BLUE
    TARGET_COLOR_HIT = GREEN

    # "Hello" point properties
    HELLO_POINT_X = 200 # The specific x-coordinate to trigger "hello"
    HELLO_POINT_TOLERANCE = 3 # Allow a small range around the point

    # Frame rate
    FPS = 60

    # Second ball margin
    SMALLER_BOX_WIDTH = 100
    SMALLER_BOX_HEIGHT = 50
    SMALLER_BORDER_WIDTH = 2
    SMALLER_BOX_COLOR = GRAY

    # --- Orbiting Ball (ball3) Config ---
    MICRO_BALL_RADIUS = 8 # Radius for the orbiting ball
    ORBIT_RADIUS = 40     # Distance from center of ball2 to center of ball3
    ORBIT_SPEED = 0.05    # Radians per frame (adjust for faster/slower orbit)
    # ---