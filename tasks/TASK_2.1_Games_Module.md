# Task 2.1: Implement Games Module

## Task Information
- **ID:** 2.1
- **Category:** Feature Implementation
- **Priority:** Medium
- **Complexity:** Medium
- **Estimated Lines:** 400
- **Estimated Time:** 6-8 hours

## Context
- **Project:** Peanut 3000 Calculator
- **Repository:** Isaiah802/Calculator
- **Working Directory:** `Broken_2.0/`

## Objective
Implement Snake and Pong games that are referenced in the main calculator code but currently don't exist. The games should use the display and keypad hardware to provide entertainment functionality.

## Current State
In `calculator.py`:
```python
try:
    from snake import play_snake
    from pong import play_pong
    GAMES_AVAILABLE = True
except ImportError:
    GAMES_AVAILABLE = False
    print("[WARNING] Game modules not found - games disabled")
```

Currently:
- `Broken_2.0/games/` directory exists with only `__init__.py` and `README.md`
- Games are imported but modules don't exist
- `GAMES_AVAILABLE = False`

## Requirements

### 1. Implement Snake Game
**File:** `Broken_2.0/games/snake.py`

**Features:**
- Classic snake game mechanics
- Snake grows when eating food
- Game over on wall collision or self-collision
- Score tracking
- Speed increases with score
- Pause functionality

**Controls:**
- Arrow keys for direction (from keypad)
- Any key to start
- Specific key for pause
- Specific key to exit

**Display:**
- Snake body rendering
- Food rendering
- Score display
- Game over message
- Simple graphics using DisplayManager

### 2. Implement Pong Game
**File:** `Broken_2.0/games/pong.py`

**Features:**
- Single player vs AI
- Paddle movement
- Ball physics
- Score tracking
- Ball speed increases over time
- AI opponent with difficulty settings

**Controls:**
- Up/Down keys for paddle (from keypad)
- Any key to start
- Specific key for pause
- Specific key to exit

**Display:**
- Paddles rendering
- Ball rendering
- Score display
- Game over message

### 3. Update Games Package
**File:** `Broken_2.0/games/__init__.py`

```python
"""
Games Module

Provides entertainment features for the calculator.

Games:
- Snake: Classic snake game
- Pong: Single player pong vs AI
"""

from .snake import play_snake
from .pong import play_pong

__all__ = ['play_snake', 'play_pong']
```

## Dependencies

### Required Before This Task
- **Task 1.1:** Extract Hardware Layer (DisplayManager, KeypadManager)

### Blocks These Tasks
- None (games are optional features)

## Deliverables

- [ ] `Broken_2.0/games/snake.py` - Snake game implementation
- [ ] `Broken_2.0/games/pong.py` - Pong game implementation
- [ ] Updated `Broken_2.0/games/__init__.py` - Proper exports
- [ ] Games accessible from calculator menu
- [ ] All controls working
- [ ] Smooth gameplay

## Implementation Details

### Snake Game Structure

```python
#!/usr/bin/env python3
"""
Snake Game

Classic snake game for the Peanut 3000 Calculator.
"""

from hardware import DisplayManager, KeypadManager
from typing import List, Tuple
import time
import random

# Constants
GRID_SIZE = 10  # Size of each grid cell
INITIAL_LENGTH = 3
INITIAL_SPEED = 200  # milliseconds
SPEED_INCREMENT = 10  # Speed up by this much per food

class Snake:
    """Snake game logic."""
    
    def __init__(self):
        """Initialize snake game."""
        self.reset()
    
    def reset(self):
        """Reset game state."""
        # Snake starts in middle, moving right
        # Food spawns randomly
        # Score = 0
        pass
    
    def update(self):
        """Update game state (move snake, check collisions)."""
        pass
    
    def change_direction(self, direction: str):
        """Change snake direction."""
        pass
    
    def check_food_collision(self) -> bool:
        """Check if snake ate food."""
        pass
    
    def check_wall_collision(self) -> bool:
        """Check if snake hit wall."""
        pass
    
    def check_self_collision(self) -> bool:
        """Check if snake hit itself."""
        pass
    
    def spawn_food(self):
        """Spawn food at random location."""
        pass

def play_snake(display: DisplayManager, keypad: KeypadManager):
    """
    Play snake game.
    
    Args:
        display: Display manager for rendering
        keypad: Keypad manager for input
    """
    game = Snake()
    running = True
    paused = False
    
    while running:
        # Get input
        key = keypad.get_key()
        
        # Handle input (direction, pause, quit)
        
        # Update game state
        if not paused:
            game.update()
        
        # Render
        render_snake(display, game)
        
        # Check game over
        if game.check_wall_collision() or game.check_self_collision():
            show_game_over(display, game.score)
            break
        
        # Delay based on speed
        time.sleep_ms(game.speed)
```

### Pong Game Structure

```python
#!/usr/bin/env python3
"""
Pong Game

Single player pong vs AI for the Peanut 3000 Calculator.
"""

from hardware import DisplayManager, KeypadManager
from typing import Tuple
import time
import random

# Constants
PADDLE_WIDTH = 5
PADDLE_HEIGHT = 40
BALL_SIZE = 5
BALL_SPEED = 5
PADDLE_SPEED = 8
AI_DIFFICULTY = 0.7  # 0-1, higher = harder

class Pong:
    """Pong game logic."""
    
    def __init__(self, screen_width: int, screen_height: int):
        """Initialize pong game."""
        self.width = screen_width
        self.height = screen_height
        self.reset()
    
    def reset(self):
        """Reset game state."""
        # Ball in center, random direction
        # Paddles at sides
        # Score = 0
        pass
    
    def update(self):
        """Update game state."""
        # Move ball
        # Move AI paddle
        # Check collisions
        pass
    
    def move_player_paddle(self, direction: int):
        """Move player paddle (-1 up, +1 down)."""
        pass
    
    def update_ai(self):
        """Update AI paddle position."""
        # Simple AI: follow ball with some delay
        pass
    
    def check_paddle_collision(self) -> bool:
        """Check ball-paddle collision."""
        pass
    
    def check_wall_collision(self) -> bool:
        """Check ball-wall collision."""
        pass
    
    def check_score(self) -> Tuple[bool, bool]:
        """Check if anyone scored."""
        pass

def play_pong(display: DisplayManager, keypad: KeypadManager):
    """
    Play pong game.
    
    Args:
        display: Display manager for rendering
        keypad: Keypad manager for input
    """
    game = Pong(display.width, display.height)
    running = True
    paused = False
    
    while running:
        # Get input
        key = keypad.get_key()
        
        # Handle input (up/down, pause, quit)
        
        # Update game state
        if not paused:
            game.update()
        
        # Render
        render_pong(display, game)
        
        # Check win condition
        if game.player_score >= 10 or game.ai_score >= 10:
            show_game_over(display, game.player_score, game.ai_score)
            break
        
        # Small delay for consistent frame rate
        time.sleep_ms(16)  # ~60 FPS
```

## Testing Criteria

### Syntax Tests
- [ ] `python3 -m py_compile Broken_2.0/games/snake.py`
- [ ] `python3 -m py_compile Broken_2.0/games/pong.py`
- [ ] `python3 -m py_compile Broken_2.0/games/__init__.py`

### Functional Tests

#### Snake Game
- [ ] Game starts correctly
- [ ] Snake moves in all 4 directions
- [ ] Snake can't reverse into itself
- [ ] Food spawns in valid locations
- [ ] Snake grows when eating food
- [ ] Collision detection works (walls, self)
- [ ] Score increments correctly
- [ ] Game over displays properly
- [ ] Can exit game cleanly

#### Pong Game
- [ ] Game starts correctly
- [ ] Player paddle moves up/down
- [ ] AI paddle follows ball
- [ ] Ball bounces off walls
- [ ] Ball bounces off paddles
- [ ] Scoring works correctly
- [ ] Game over displays properly
- [ ] Can exit game cleanly

### Integration Tests
- [ ] Games launch from calculator menu
- [ ] Games return to calculator properly
- [ ] Display state restored after game
- [ ] No memory leaks
- [ ] Keypad input doesn't interfere with calculator

## Keypad Mapping

Assuming standard calculator keypad layout:
```
[1] [2] [3] [+]
[4] [5] [6] [-]
[7] [8] [9] [*]
[C] [0] [=] [/]
```

Game controls:
- **Snake:** 2=Up, 8=Down, 4=Left, 6=Right, 5=Pause, C=Exit
- **Pong:** 2=Up, 8=Down, 5=Pause, C=Exit

## Success Criteria

✅ Task is complete when:
1. Both games implemented and working
2. Games accessible from calculator menu
3. All controls responsive
4. Games run smoothly (good FPS)
5. Proper game over handling
6. Clean exit back to calculator
7. Code follows existing patterns
8. No crashes or hangs

## Notes

- Keep games simple - this is a calculator, not a gaming device
- Optimize for small display (320x240)
- Handle memory efficiently
- Use DisplayManager methods for rendering
- Test on actual hardware if possible
- Make games fun but not too complex

## Related Documentation
- See ARCHITECTURE.md for system design
- See AI_AGENT_GUIDE.md for code patterns
- Review hardware/display.py for rendering methods
- Review hardware/keypad.py for input methods

---

**Have fun implementing these games! 🎮**
