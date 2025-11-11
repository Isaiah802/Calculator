"""
Scientific Calculator Module

This module provides scientific calculator functionality including:
- Trigonometric functions (sin, cos, tan, asin, acos, atan)
- Inverse trigonometric functions
- Hyperbolic functions (sinh, cosh, tanh)
- Inverse hyperbolic functions (asinh, acosh, atanh)
- Logarithmic and exponential functions (log, ln, exp, pow, sqrt)
- Statistical calculations (mean, median, std_dev, variance)
- Angle mode management (degrees/radians)
- Additional mathematical functions (factorial, degrees/radians conversion)
"""

from .functions import ScientificCalculator, create_scientific_calculator

__all__ = ['ScientificCalculator', 'create_scientific_calculator']
