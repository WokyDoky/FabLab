# File: Game.py
import math

import pygame
import sys

from scipy.stats import arcsine

import Config
import Ball
import numpy as np

class Game:
    def __init__(self):
        # ... (Initialization remains the same, ensure Ball() calls are correct) ...
        pygame.init()
        self.config = Config.Config()
        self.screen = pygame.display.set_mode((self.config.SCREEN_WIDTH, self.config.SCREEN_HEIGHT))
        pygame.display.set_caption("Move the Balls! (OOP)")

        # Box setup
        box_x = (self.config.SCREEN_WIDTH - self.config.BOX_WIDTH) // 2
        box_y = (self.config.SCREEN_HEIGHT - self.config.BOX_HEIGHT) // 2
        self.box_rect = pygame.Rect(box_x, box_y, self.config.BOX_WIDTH, self.config.BOX_HEIGHT)

        # Smaller movement area
        smaller_box_x = (self.config.SCREEN_WIDTH - self.config.SMALLER_BOX_WIDTH) // 2
        smaller_box_y = (self.config.SCREEN_HEIGHT - self.config.SMALLER_BOX_HEIGHT) // 2
        self.smaller_box_rect = pygame.Rect(smaller_box_x, smaller_box_y, self.config.SMALLER_BOX_WIDTH, self.config.SMALLER_BOX_HEIGHT)

        # Orbit
        # orbit_x = (self.config.BALL_RADIUS - self.config.MICRO_BOX_WIDTH) //2
        # orbit_y = (self.config.BALL_RADIUS - self.config.MICRO_BOX_HEIGHT) // 2
        # self.orbit = pygame.Rect(orbit_x, orbit_y, self.config.MICRO_BOX_WIDTH, self.config.MICRO_BOX_HEIGHT)
        # Target area setup
        target_x = self.box_rect.right - self.config.TARGET_WIDTH - self.config.BORDER_WIDTH - 10
        target_y = self.box_rect.top + self.config.BORDER_WIDTH + 10
        self.target_rect = pygame.Rect(target_x, target_y, self.config.TARGET_WIDTH, self.config.TARGET_HEIGHT)
        self.target_color = self.config.TARGET_COLOR_NORMAL

        # Create the balls (ensure these calls match the corrected Ball.__init__)
        self.ball1 = Ball.Ball(self.config, self.config.RED)
        start_x_ball2 = self.config.SCREEN_WIDTH // 2
        start_y_ball2 = self.config.SCREEN_HEIGHT // 2 + self.config.BALL_RADIUS * 3
        self.ball2 = Ball.Ball(self.config, self.config.BLUE, start_x=start_x_ball2, start_y=start_y_ball2)

        start_x_ball3 = start_x_ball2 + self.config.BALL_RADIUS * 2
        start_y_ball3 = start_y_ball2 + self.config.BALL_RADIUS * 2
        #self.ball3 = Ball.Ball(self.config, self.config.NICE_BLUE, start_x=start_x_ball3, start_y=start_y_ball3)
        self.ball3 = Ball.Ball(self.config, self.config.NICE_BLUE,
                               start_x=start_x_ball2 + self.config.ORBIT_RADIUS,  # Initial offset
                               start_y=start_y_ball2,)  # Use smaller radius

        self.ball3.set_size(self.config.BALL_RADIUS/2)
        # Use a dictionary to track current speeds
        self.ball_speeds = {
            self.ball1: self.config.BALL_SPEED,
            self.ball2: self.config.BALL_SPEED,
            self.ball3: self.config.BALL_SPEED #remove?
        }

        self.orbit_angle = 0.0
        self.clock = pygame.time.Clock()

    # --- Update handle_ball_movement ---
    def handle_ball_movement(self, ball, keys):
        """Handles movement logic (keys, acceleration, speed cap) for a given ball."""
        base_speed = self.config.BALL_SPEED
        acceleration = self.config.BALL_ACCELERATION
        max_speed = base_speed * 2

        # Determine keys for this ball
        left_key, right_key, up_key, down_key = None, None, None, None
        if ball is self.ball1:
            # Arrow keys for ball 1
            left_key, right_key, up_key, down_key = pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN
        elif ball is self.ball2:
            # WASD keys for ball 2
            left_key, right_key, up_key, down_key = pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s
        else:
            return # Unknown ball

        # Determine movement directions
        direction_x = 0
        direction_y = 0 # Add y direction
        moving = False
        if keys[left_key]:
            direction_x = -1
            moving = True
        if keys[right_key]:
            direction_x = 1 # Right overrides left
            moving = True
        if keys[up_key]:
            direction_y = -1 # Pygame y-axis is 0 at top
            moving = True
        if keys[down_key]:
            direction_y = 1 # Down overrides up
            moving = True

        # Get current speed from the dictionary
        current_speed = self.ball_speeds[ball]

        # Apply acceleration or reset speed (only if moving in any direction)
        if moving:
            current_speed += acceleration
            # Cap speed
            if current_speed > max_speed:
                current_speed = max_speed
        else:
            # Reset speed if not moving
            current_speed = base_speed

        # Store the updated speed back in the dictionary
        self.ball_speeds[ball] = current_speed

        # Apply movement to the ball object (both x and y)
        # Note: This makes diagonal movement faster. Normalize if needed.
        ball.x += direction_x * current_speed
        ball.y += direction_y * current_speed # Apply vertical movement

    # --- Methods run, _handle_events, _handle_input, _update, _check_*, _draw, _quit_game remain the same ---
    # Make sure _handle_input calls handle_ball_movement for both balls as before.

    def run(self):
        """Starts the main game loop."""
        running = True
        while running:
            running = self._handle_events()
            if not running:
                break
            self._handle_input()
            self._update()
            self._draw()
            self.clock.tick(self.config.FPS)
        self._quit_game()

    def _handle_events(self):
        """Process Pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
        return True

    def _handle_input(self):
        """Check keyboard state and call handler for each ball."""
        keys = pygame.key.get_pressed()
        self.handle_ball_movement(self.ball1, keys)
        self.handle_ball_movement(self.ball2, keys)

    def _update(self):
        """Update all game objects."""
        self.ball1.update(self.box_rect)
        self.ball2.update(self.smaller_box_rect)


        # Calculate new x, y using trigonometry
        self.smaller_ball_chaser()
        # ---
        self.ball3.update(self.box_rect)
        self.ball_chaser()

    def _check_target_area(self, ball_to_check):
        """Check for collision with the target rectangle."""
        ball_rect = ball_to_check.get_rect()
        if ball_rect.colliderect(self.target_rect):
            if ball_to_check is self.ball1:
                print("here")
                self.target_color = self.config.TARGET_COLOR_HIT
        elif ball_to_check is self.ball1:
             self.target_color = self.config.TARGET_COLOR_NORMAL

    def _check_hello_point(self, ball_to_check):
        """Check if the ball's x-coordinate is near the HELLO_POINT_X."""
        if ball_to_check is self.ball1:
            ball_x, _ = ball_to_check.get_position()
            if abs(ball_x - self.config.HELLO_POINT_X) <= self.config.HELLO_POINT_TOLERANCE:
                print("hello")

    def _draw(self):
        """Draw all game elements to the screen."""
        self.screen.fill(self.config.BLACK)
        pygame.draw.rect(self.screen, self.config.BOX_COLOR, self.box_rect)
        pygame.draw.rect(self.screen, self.config.BORDER_COLOR, self.box_rect, self.config.BORDER_WIDTH)
        # pygame.draw.rect(self.screen, self.target_color, self.target_rect)
        self.ball1.draw(self.screen)
        self.ball2.draw(self.screen)
        self.ball3.draw(self.screen)
        pygame.display.flip()

    def _quit_game(self):
        """Clean up and quit Pygame."""
        pygame.quit()
        sys.exit()

    def move_ball_programmatically(self, ball, direction):
        """
        Moves a specific ball object one step in the given direction ('L', 'R', 'U', 'D')
        using the base speed, and applies boundary checks immediately.
        """
        if not ball:  # Check if a valid ball object was passed
            print("Error: Invalid ball object provided.")
            return

        speed = self.config.BALL_SPEED  # Use the base speed for this simple move

        if direction == "L":
            ball.x -= speed
        elif direction == "R":
            ball.x += speed
        elif direction == "U":
            ball.y -= speed  # Remember y=0 is top
        elif direction == "D":
            ball.y += speed
        else:
            print(f"Warning: Unknown direction '{direction}' sent to move_ball_programmatically.")
            return  # Do nothing if direction is unknown

        # --- Crucial: Apply boundary checks immediately ---
        # This ensures the programmatic move doesn't push the ball out of bounds
        # before the next main update cycle.
        ball.update(self.box_rect)

    def ball_chaser(self):
        pos1 = self.ball1.get_position()  # Gets (x1, y1)
        pos2 = self.ball2.get_position()  # Gets (x2, y2)
        # pos3 = self.ball3.get_position()

        x1 = pos1[0]  # Extract x-coordinate of ball 1
        x2 = pos2[0]  # Extract x-coordinate of ball 2
        # x3 = pos3[0]  # Extract x-coords fo ball 3

        delta_x = x1 - x2  # Calculate the difference
        # delta_xX = x1 - x3

        if abs(delta_x) > 10:
            print("Ball position doesn't match the ball2 position.")
            if delta_x > 0:
                self.move_ball_programmatically(self.ball2, "R")
            if delta_x < 0:
                self.move_ball_programmatically(self.ball2, "L")

    def smaller_ball_chaser(self):
        # --- Calculate Orbiting Ball (ball3) Position ---
        center_x, center_y = self.ball2.get_position()  # Orbit around ball2's center
        #self.orbit_angle += self.config.ORBIT_SPEED  # Increment angle
        #self.ball3.x = center_x + self.config.ORBIT_RADIUS * math.cos(self.orbit_angle)
        #self.ball3.y = center_y + self.config.ORBIT_RADIUS * math.sin(self.orbit_angle)

        # --- Calculate Orbiting Ball (ball3) Position ---
        # Get center positions
        b1_x, b1_y = self.ball1.get_position()
        b2_x, b2_y = self.ball2.get_position()

        # Calculate vector components from ball2 TOWARDS ball1
        delta_x = b1_x - b2_x
        delta_y = b1_y - b2_y

        # Calculate the angle from ball2 towards ball1 using atan2(y, x)
        # Add a small check to prevent issues if balls are exactly on top of each other
        if delta_x == 0 and delta_y == 0:
            # Keep previous position or default if desired, here we just skip update
            pass  # Or set ball3 position relative to ball2 arbitrarily
        else:
            angle_to_ball1 = math.atan2(delta_y, delta_x)  # Angle in radians

            # Calculate ball3's position: center of ball2 + offset towards ball1
            orbit_radius = self.config.ORBIT_RADIUS
            self.ball3.x = b2_x + orbit_radius * math.cos(angle_to_ball1)
            self.ball3.y = b2_y + orbit_radius * math.sin(angle_to_ball1)
if __name__ == "__main__":
    game = Game()
    game.run()