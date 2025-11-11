#!/usr/bin/env python3
"""
Snake Game

Classic snake game for the Peanut 3000 Calculator.
"""

import time
import random


# Constants
GRID_SIZE = 8  # Size of each grid cell
INITIAL_LENGTH = 3
INITIAL_SPEED_MS = 200  # milliseconds
SPEED_INCREMENT = 10  # Speed up by this much per food
MIN_SPEED_MS = 50  # Maximum speed (minimum delay)

# Colors (RGB565)
COLOR_BACKGROUND = 0x0000  # Black
COLOR_SNAKE = 0x07E0       # Green
COLOR_FOOD = 0xF800        # Red
COLOR_TEXT = 0xFFFF        # White
COLOR_BORDER = 0x07FF      # Cyan

# Directions
DIR_UP = 0
DIR_DOWN = 1
DIR_LEFT = 2
DIR_RIGHT = 3


class Snake:
    """Snake game logic."""
    
    def __init__(self, screen_width: int, screen_height: int):
        """Initialize snake game.
        
        Args:
            screen_width: Display width in pixels
            screen_height: Display height in pixels
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Calculate grid dimensions (leave space for score at top)
        self.score_height = 20
        self.grid_width = (screen_width - 2) // GRID_SIZE
        self.grid_height = (screen_height - self.score_height - 2) // GRID_SIZE
        
        # Adjust for centering
        self.offset_x = (screen_width - self.grid_width * GRID_SIZE) // 2
        self.offset_y = self.score_height + (screen_height - self.score_height - self.grid_height * GRID_SIZE) // 2
        
        self.reset()
    
    def reset(self):
        """Reset game state."""
        # Snake starts in middle, moving right
        center_x = self.grid_width // 2
        center_y = self.grid_height // 2
        
        self.body = [
            (center_x, center_y),
            (center_x - 1, center_y),
            (center_x - 2, center_y)
        ]
        self.direction = DIR_RIGHT
        self.next_direction = DIR_RIGHT
        self.score = 0
        self.speed_ms = INITIAL_SPEED_MS
        self.game_over = False
        
        # Spawn initial food
        self.spawn_food()
    
    def spawn_food(self):
        """Spawn food at random location not occupied by snake."""
        while True:
            x = random.randint(0, self.grid_width - 1)
            y = random.randint(0, self.grid_height - 1)
            if (x, y) not in self.body:
                self.food = (x, y)
                break
    
    def change_direction(self, new_direction: int):
        """Change snake direction (queued for next update).
        
        Args:
            new_direction: New direction (DIR_UP, DIR_DOWN, DIR_LEFT, DIR_RIGHT)
        """
        # Can't reverse into itself
        if new_direction == DIR_UP and self.direction != DIR_DOWN:
            self.next_direction = new_direction
        elif new_direction == DIR_DOWN and self.direction != DIR_UP:
            self.next_direction = new_direction
        elif new_direction == DIR_LEFT and self.direction != DIR_RIGHT:
            self.next_direction = new_direction
        elif new_direction == DIR_RIGHT and self.direction != DIR_LEFT:
            self.next_direction = new_direction
    
    def update(self):
        """Update game state (move snake, check collisions).
        
        Returns:
            True if game continues, False if game over
        """
        if self.game_over:
            return False
        
        # Apply queued direction change
        self.direction = self.next_direction
        
        # Calculate new head position
        head_x, head_y = self.body[0]
        
        if self.direction == DIR_UP:
            new_head = (head_x, head_y - 1)
        elif self.direction == DIR_DOWN:
            new_head = (head_x, head_y + 1)
        elif self.direction == DIR_LEFT:
            new_head = (head_x - 1, head_y)
        else:  # DIR_RIGHT
            new_head = (head_x + 1, head_y)
        
        # Check wall collision
        if (new_head[0] < 0 or new_head[0] >= self.grid_width or
            new_head[1] < 0 or new_head[1] >= self.grid_height):
            self.game_over = True
            return False
        
        # Check self collision
        if new_head in self.body:
            self.game_over = True
            return False
        
        # Add new head
        self.body.insert(0, new_head)
        
        # Check if food eaten
        if new_head == self.food:
            self.score += 10
            # Increase speed (decrease delay)
            self.speed_ms = max(MIN_SPEED_MS, self.speed_ms - SPEED_INCREMENT)
            self.spawn_food()
        else:
            # Remove tail (move forward)
            self.body.pop()
        
        return True


def render_snake(display, game: Snake):
    """Render the snake game.
    
    Args:
        display: DisplayManager instance
        game: Snake game instance
    """
    # Clear screen
    display.clear(COLOR_BACKGROUND)
    
    # Draw border around play area
    border_x = game.offset_x - 1
    border_y = game.offset_y - 1
    border_w = game.grid_width * GRID_SIZE + 2
    border_h = game.grid_height * GRID_SIZE + 2
    display.draw_rect(border_x, border_y, border_w, border_h, COLOR_BORDER)
    
    # Draw score
    score_text = f"Score: {game.score}"
    display.draw_text(5, 5, score_text, COLOR_TEXT)
    
    # Draw snake body
    for x, y in game.body:
        pixel_x = game.offset_x + x * GRID_SIZE
        pixel_y = game.offset_y + y * GRID_SIZE
        display.fill_rect(pixel_x, pixel_y, GRID_SIZE - 1, GRID_SIZE - 1, COLOR_SNAKE)
    
    # Draw food
    food_x = game.offset_x + game.food[0] * GRID_SIZE
    food_y = game.offset_y + game.food[1] * GRID_SIZE
    display.fill_rect(food_x, food_y, GRID_SIZE - 1, GRID_SIZE - 1, COLOR_FOOD)
    
    # Update display
    display.show(force=True)


def show_game_over(display, score: int):
    """Show game over screen.
    
    Args:
        display: DisplayManager instance
        score: Final score
    """
    display.clear(COLOR_BACKGROUND)
    
    # Center text
    display.draw_text(80, 100, "GAME OVER", COLOR_TEXT)
    display.draw_text(70, 120, f"Final Score: {score}", COLOR_TEXT)
    display.draw_text(40, 140, "Press any key to exit", COLOR_TEXT)
    
    display.show(force=True)
    
    # Wait a moment
    time.sleep_ms(500)


def play_snake(display, keypad):
    """Play snake game.
    
    Args:
        display: DisplayManager instance for rendering
        keypad: KeypadManager instance for input
    """
    game = Snake(display.width, display.height)
    running = True
    paused = False
    last_update = time.ticks_ms()
    
    # Initial render
    render_snake(display, game)
    
    while running:
        # Get input events
        events = keypad.get_events()
        
        for key, event_type in events:
            if event_type in ('tap', 'down'):
                # Get key label
                label = keypad.get_key_label(key, False)
                
                # Handle controls
                # Snake: 2=Up, 8=Down, 4=Left, 6=Right, 5=Pause, C=Exit
                if label == '2':
                    game.change_direction(DIR_UP)
                elif label == '8':
                    game.change_direction(DIR_DOWN)
                elif label == '4':
                    game.change_direction(DIR_LEFT)
                elif label == '6':
                    game.change_direction(DIR_RIGHT)
                elif label == '5':
                    paused = not paused
                elif label == 'C' or label == 'ON':
                    running = False
                    break
        
        # Update game state based on timing
        now = time.ticks_ms()
        if not paused and time.ticks_diff(now, last_update) >= game.speed_ms:
            last_update = now
            
            # Update game
            if not game.update():
                # Game over
                show_game_over(display, game.score)
                
                # Wait for any key to exit
                waiting = True
                while waiting:
                    events = keypad.get_events()
                    if events:
                        waiting = False
                        running = False
                break
            
            # Render
            render_snake(display, game)
        
        # Small delay to prevent busy loop
        time.sleep_ms(10)
    
    # Clear screen before exiting
    display.clear(COLOR_BACKGROUND)
    display.show(force=True)
