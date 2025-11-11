#!/usr/bin/env python3
"""
Pong Game

Single player pong vs AI for the Peanut 3000 Calculator.
"""

import time
import random


# Constants
PADDLE_WIDTH = 4
PADDLE_HEIGHT = 30
BALL_SIZE = 4
BALL_SPEED_X = 3
BALL_SPEED_Y = 2
PADDLE_SPEED = 4
AI_DIFFICULTY = 0.7  # 0-1, higher = harder (chance AI will track ball)
WINNING_SCORE = 5

# Colors (RGB565)
COLOR_BACKGROUND = 0x0000  # Black
COLOR_PADDLE = 0xFFFF      # White
COLOR_BALL = 0xFFFF        # White
COLOR_TEXT = 0xFFFF        # White
COLOR_DIVIDER = 0x4208     # Gray


class Pong:
    """Pong game logic."""
    
    def __init__(self, screen_width: int, screen_height: int):
        """Initialize pong game.
        
        Args:
            screen_width: Display width in pixels
            screen_height: Display height in pixels
        """
        self.width = screen_width
        self.height = screen_height
        
        # Score area at top
        self.score_height = 20
        self.play_height = screen_height - self.score_height
        
        self.reset()
    
    def reset(self):
        """Reset game state."""
        # Ball in center, random direction
        self.ball_x = self.width // 2
        self.ball_y = self.score_height + self.play_height // 2
        
        # Random initial direction
        self.ball_dx = BALL_SPEED_X * (1 if random.random() > 0.5 else -1)
        self.ball_dy = BALL_SPEED_Y * (1 if random.random() > 0.5 else -1)
        
        # Paddles at sides, centered vertically
        self.player_y = self.score_height + (self.play_height - PADDLE_HEIGHT) // 2
        self.ai_y = self.score_height + (self.play_height - PADDLE_HEIGHT) // 2
        
        # Paddle X positions
        self.player_x = 10
        self.ai_x = self.width - 10 - PADDLE_WIDTH
        
        # Scores
        self.player_score = 0
        self.ai_score = 0
        
        self.game_over = False
        self.winner = None
    
    def update(self):
        """Update game state.
        
        Returns:
            True if game continues, False if game over
        """
        if self.game_over:
            return False
        
        # Move ball
        self.ball_x += self.ball_dx
        self.ball_y += self.ball_dy
        
        # Ball collision with top/bottom walls
        if self.ball_y <= self.score_height:
            self.ball_y = self.score_height
            self.ball_dy = abs(self.ball_dy)
        elif self.ball_y >= self.height - BALL_SIZE:
            self.ball_y = self.height - BALL_SIZE
            self.ball_dy = -abs(self.ball_dy)
        
        # Ball collision with player paddle
        if (self.ball_x <= self.player_x + PADDLE_WIDTH and
            self.ball_y + BALL_SIZE >= self.player_y and
            self.ball_y <= self.player_y + PADDLE_HEIGHT):
            self.ball_x = self.player_x + PADDLE_WIDTH
            self.ball_dx = abs(self.ball_dx)
            # Add some variation based on where ball hits paddle
            hit_pos = (self.ball_y - self.player_y) / PADDLE_HEIGHT
            self.ball_dy = int((hit_pos - 0.5) * BALL_SPEED_Y * 2)
        
        # Ball collision with AI paddle
        if (self.ball_x + BALL_SIZE >= self.ai_x and
            self.ball_y + BALL_SIZE >= self.ai_y and
            self.ball_y <= self.ai_y + PADDLE_HEIGHT):
            self.ball_x = self.ai_x - BALL_SIZE
            self.ball_dx = -abs(self.ball_dx)
            # Add some variation based on where ball hits paddle
            hit_pos = (self.ball_y - self.ai_y) / PADDLE_HEIGHT
            self.ball_dy = int((hit_pos - 0.5) * BALL_SPEED_Y * 2)
        
        # Check scoring (ball goes off left or right edge)
        if self.ball_x < 0:
            # AI scores
            self.ai_score += 1
            self._reset_ball()
            if self.ai_score >= WINNING_SCORE:
                self.game_over = True
                self.winner = "AI"
        elif self.ball_x > self.width:
            # Player scores
            self.player_score += 1
            self._reset_ball()
            if self.player_score >= WINNING_SCORE:
                self.game_over = True
                self.winner = "Player"
        
        # Update AI paddle
        self.update_ai()
        
        return not self.game_over
    
    def _reset_ball(self):
        """Reset ball to center with random direction."""
        self.ball_x = self.width // 2
        self.ball_y = self.score_height + self.play_height // 2
        self.ball_dx = BALL_SPEED_X * (1 if random.random() > 0.5 else -1)
        self.ball_dy = BALL_SPEED_Y * (1 if random.random() > 0.5 else -1)
    
    def move_player_paddle(self, direction: int):
        """Move player paddle (-1 up, +1 down).
        
        Args:
            direction: -1 for up, +1 for down
        """
        self.player_y += direction * PADDLE_SPEED
        
        # Clamp to screen bounds
        if self.player_y < self.score_height:
            self.player_y = self.score_height
        elif self.player_y > self.height - PADDLE_HEIGHT:
            self.player_y = self.height - PADDLE_HEIGHT
    
    def update_ai(self):
        """Update AI paddle position."""
        # Simple AI: follow ball with some randomness
        if random.random() < AI_DIFFICULTY:
            # Track ball
            ball_center = self.ball_y + BALL_SIZE // 2
            paddle_center = self.ai_y + PADDLE_HEIGHT // 2
            
            if ball_center < paddle_center - 2:
                self.ai_y -= PADDLE_SPEED
            elif ball_center > paddle_center + 2:
                self.ai_y += PADDLE_SPEED
        
        # Clamp to screen bounds
        if self.ai_y < self.score_height:
            self.ai_y = self.score_height
        elif self.ai_y > self.height - PADDLE_HEIGHT:
            self.ai_y = self.height - PADDLE_HEIGHT


def render_pong(display, game: Pong):
    """Render the pong game.
    
    Args:
        display: DisplayManager instance
        game: Pong game instance
    """
    # Clear screen
    display.clear(COLOR_BACKGROUND)
    
    # Draw center divider
    for y in range(game.score_height, game.height, 10):
        display.draw_vline(game.width // 2, y, 5, COLOR_DIVIDER)
    
    # Draw scores
    player_score_text = str(game.player_score)
    ai_score_text = str(game.ai_score)
    display.draw_text(game.width // 4, 5, player_score_text, COLOR_TEXT)
    display.draw_text(3 * game.width // 4, 5, ai_score_text, COLOR_TEXT)
    
    # Draw player paddle (left)
    display.fill_rect(game.player_x, game.player_y, PADDLE_WIDTH, PADDLE_HEIGHT, COLOR_PADDLE)
    
    # Draw AI paddle (right)
    display.fill_rect(game.ai_x, game.ai_y, PADDLE_WIDTH, PADDLE_HEIGHT, COLOR_PADDLE)
    
    # Draw ball
    display.fill_rect(game.ball_x, game.ball_y, BALL_SIZE, BALL_SIZE, COLOR_BALL)
    
    # Update display
    display.show(force=True)


def show_game_over(display, winner: str, player_score: int, ai_score: int):
    """Show game over screen.
    
    Args:
        display: DisplayManager instance
        winner: "Player" or "AI"
        player_score: Player's final score
        ai_score: AI's final score
    """
    display.clear(COLOR_BACKGROUND)
    
    # Center text
    if winner == "Player":
        display.draw_text(70, 90, "YOU WIN!", COLOR_TEXT)
    else:
        display.draw_text(70, 90, "AI WINS!", COLOR_TEXT)
    
    display.draw_text(60, 110, f"Score: {player_score} - {ai_score}", COLOR_TEXT)
    display.draw_text(40, 140, "Press any key to exit", COLOR_TEXT)
    
    display.show(force=True)
    
    # Wait a moment
    time.sleep_ms(500)


def play_pong(display, keypad):
    """Play pong game.
    
    Args:
        display: DisplayManager instance for rendering
        keypad: KeypadManager instance for input
    """
    game = Pong(display.width, display.height)
    running = True
    paused = False
    last_update = time.ticks_ms()
    frame_time_ms = 16  # ~60 FPS
    
    # Initial render
    render_pong(display, game)
    
    while running:
        # Get input events
        events = keypad.get_events()
        
        for key, event_type in events:
            if event_type in ('tap', 'down'):
                # Get key label
                label = keypad.get_key_label(key, False)
                
                # Handle controls
                # Pong: 2=Up, 8=Down, 5=Pause, C=Exit
                if label == '2':
                    game.move_player_paddle(-1)
                elif label == '8':
                    game.move_player_paddle(1)
                elif label == '5':
                    paused = not paused
                elif label == 'C' or label == 'ON':
                    running = False
                    break
        
        # Update game state based on timing
        now = time.ticks_ms()
        if not paused and time.ticks_diff(now, last_update) >= frame_time_ms:
            last_update = now
            
            # Update game
            if not game.update():
                # Game over
                show_game_over(display, game.winner, game.player_score, game.ai_score)
                
                # Wait for any key to exit
                waiting = True
                while waiting:
                    events = keypad.get_events()
                    if events:
                        waiting = False
                        running = False
                break
            
            # Render
            render_pong(display, game)
        
        # Small delay to prevent busy loop
        time.sleep_ms(5)
    
    # Clear screen before exiting
    display.clear(COLOR_BACKGROUND)
    display.show(force=True)
