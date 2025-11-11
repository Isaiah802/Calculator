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
