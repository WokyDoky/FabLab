# File: Ball.py
import pygame

class Ball:
    """Represents a movable ball in the game."""
    # Revert __init__ to previous working version (no speed parameter)
    def __init__(self, config, color, start_x=None, start_y=None):
        """Initialize the ball's properties."""
        self.config = config
        self.color = color
        self.x = start_x if start_x is not None else self.config.SCREEN_WIDTH // 2
        self.y = start_y if start_y is not None else self.config.SCREEN_HEIGHT // 2
        self.radius = self.config.BALL_RADIUS
        # Speed is handled by the Game class (base speed in config, current speed in Game.ball_speeds)

    # REMOVE the move(self, keys) and _move(self, direction) methods

    def update(self, box_rect):
        """Update ball state, including boundary checks."""
        # Horizontal boundaries
        left_boundary = box_rect.left + self.config.BORDER_WIDTH + self.radius
        right_boundary = box_rect.right - self.config.BORDER_WIDTH - self.radius
        if self.x < left_boundary:
            self.x = left_boundary
        elif self.x > right_boundary:
            self.x = right_boundary

        # Vertical boundaries (Corrected logic)
        top_boundary = box_rect.top + self.config.BORDER_WIDTH + self.radius
        bottom_boundary = box_rect.bottom - self.config.BORDER_WIDTH - self.radius
        if self.y < top_boundary:
            self.y = top_boundary
        elif self.y > bottom_boundary:
            self.y = bottom_boundary

    def draw(self, surface):
        """Draw the ball on the provided surface."""
        pygame.draw.circle(surface, self.color, (self.x, self.y), self.radius)

    def get_rect(self):
        """Return a pygame.Rect representing the ball's bounding box."""
        return pygame.Rect(self.x - self.radius, self.y - self.radius,
                          self.radius * 2, self.radius * 2)

    def get_position(self):
        """Return the current (x, y) coordinates of the ball's center."""
        return self.x, self.y

    # Keep set_size if needed
    def set_size(self, r):
        self.radius = r