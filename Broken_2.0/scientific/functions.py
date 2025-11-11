#!/usr/bin/env python3
"""
Scientific Calculator Functions Module

This module provides scientific calculator functions including:
- Trigonometric functions (sin, cos, tan, etc.)
- Inverse trigonometric functions (asin, acos, atan)
- Hyperbolic functions (sinh, cosh, tanh)
- Logarithmic and exponential functions
- Statistical functions
- Angle mode conversion (degrees/radians)

The module integrates with the EnhancedMathEngine for advanced calculations.
"""

import math

class ScientificCalculator:
    """Scientific calculator functions with angle mode support."""
    
    def __init__(self, enhanced_math_engine=None):
        """
        Initialize scientific calculator.
        
        Args:
            enhanced_math_engine: Optional EnhancedMathEngine instance for advanced features
        """
        self.angle_mode = "deg"  # "deg" or "rad"
        self.enhanced_engine = enhanced_math_engine
    
    # Trigonometric functions
    def sin(self, x):
        """
        Calculate sine of x (respects angle mode).
        
        Args:
            x: Angle value
            
        Returns:
            Sine of x
        """
        if self.angle_mode == "deg":
            x = math.radians(x)
        return math.sin(x)
    
    def cos(self, x):
        """
        Calculate cosine of x (respects angle mode).
        
        Args:
            x: Angle value
            
        Returns:
            Cosine of x
        """
        if self.angle_mode == "deg":
            x = math.radians(x)
        return math.cos(x)
    
    def tan(self, x):
        """
        Calculate tangent of x (respects angle mode).
        
        Args:
            x: Angle value
            
        Returns:
            Tangent of x
        """
        if self.angle_mode == "deg":
            x = math.radians(x)
        return math.tan(x)
    
    # Inverse trigonometric functions
    def asin(self, x):
        """
        Calculate arcsine of x (returns in current angle mode).
        
        Args:
            x: Value between -1 and 1
            
        Returns:
            Arcsine of x in current angle mode
        """
        result = math.asin(x)
        if self.angle_mode == "deg":
            result = math.degrees(result)
        return result
    
    def acos(self, x):
        """
        Calculate arccosine of x (returns in current angle mode).
        
        Args:
            x: Value between -1 and 1
            
        Returns:
            Arccosine of x in current angle mode
        """
        result = math.acos(x)
        if self.angle_mode == "deg":
            result = math.degrees(result)
        return result
    
    def atan(self, x):
        """
        Calculate arctangent of x (returns in current angle mode).
        
        Args:
            x: Any real number
            
        Returns:
            Arctangent of x in current angle mode
        """
        result = math.atan(x)
        if self.angle_mode == "deg":
            result = math.degrees(result)
        return result
    
    def atan2(self, y, x):
        """
        Calculate arctangent of y/x using signs to determine quadrant.
        
        Args:
            y: Y coordinate
            x: X coordinate
            
        Returns:
            Arctangent in current angle mode
        """
        result = math.atan2(y, x)
        if self.angle_mode == "deg":
            result = math.degrees(result)
        return result
    
    # Hyperbolic functions
    def sinh(self, x):
        """
        Calculate hyperbolic sine of x.
        
        Args:
            x: Real number
            
        Returns:
            Hyperbolic sine of x
        """
        return math.sinh(x)
    
    def cosh(self, x):
        """
        Calculate hyperbolic cosine of x.
        
        Args:
            x: Real number
            
        Returns:
            Hyperbolic cosine of x
        """
        return math.cosh(x)
    
    def tanh(self, x):
        """
        Calculate hyperbolic tangent of x.
        
        Args:
            x: Real number
            
        Returns:
            Hyperbolic tangent of x
        """
        return math.tanh(x)
    
    # Inverse hyperbolic functions
    def asinh(self, x):
        """
        Calculate inverse hyperbolic sine of x.
        
        Args:
            x: Real number
            
        Returns:
            Inverse hyperbolic sine of x
        """
        return math.asinh(x)
    
    def acosh(self, x):
        """
        Calculate inverse hyperbolic cosine of x.
        
        Args:
            x: Real number >= 1
            
        Returns:
            Inverse hyperbolic cosine of x
        """
        return math.acosh(x)
    
    def atanh(self, x):
        """
        Calculate inverse hyperbolic tangent of x.
        
        Args:
            x: Real number, -1 < x < 1
            
        Returns:
            Inverse hyperbolic tangent of x
        """
        return math.atanh(x)
    
    # Logarithmic and exponential functions
    def log(self, x, base=10):
        """
        Calculate logarithm of x with specified base (default 10).
        
        Args:
            x: Positive real number
            base: Logarithm base (default 10)
            
        Returns:
            Logarithm of x to the given base
        """
        return math.log(x, base)
    
    def ln(self, x):
        """
        Calculate natural logarithm of x.
        
        Args:
            x: Positive real number
            
        Returns:
            Natural logarithm of x
        """
        return math.log(x)
    
    def log10(self, x):
        """
        Calculate base-10 logarithm of x.
        
        Args:
            x: Positive real number
            
        Returns:
            Base-10 logarithm of x
        """
        return math.log10(x)
    
    def log2(self, x):
        """
        Calculate base-2 logarithm of x.
        
        Args:
            x: Positive real number
            
        Returns:
            Base-2 logarithm of x
        """
        # MicroPython might not have log2, use log(x, 2) instead
        try:
            return math.log2(x)
        except AttributeError:
            return math.log(x, 2)
    
    def exp(self, x):
        """
        Calculate e^x.
        
        Args:
            x: Real number
            
        Returns:
            e raised to the power of x
        """
        return math.exp(x)
    
    def pow(self, x, y):
        """
        Calculate x^y.
        
        Args:
            x: Base
            y: Exponent
            
        Returns:
            x raised to the power of y
        """
        return math.pow(x, y)
    
    def sqrt(self, x):
        """
        Calculate square root of x.
        
        Args:
            x: Non-negative real number
            
        Returns:
            Square root of x
        """
        return math.sqrt(x)
    
    # Additional mathematical functions
    def factorial(self, n):
        """
        Calculate factorial of n.
        
        Args:
            n: Non-negative integer
            
        Returns:
            n! (factorial of n)
        """
        if not isinstance(n, int) or n < 0:
            raise ValueError("Factorial requires non-negative integer")
        
        result = 1
        for i in range(2, n + 1):
            result *= i
        return result
    
    def degrees(self, x):
        """
        Convert radians to degrees.
        
        Args:
            x: Angle in radians
            
        Returns:
            Angle in degrees
        """
        return math.degrees(x)
    
    def radians(self, x):
        """
        Convert degrees to radians.
        
        Args:
            x: Angle in degrees
            
        Returns:
            Angle in radians
        """
        return math.radians(x)
    
    # Angle mode management
    def set_angle_mode(self, mode):
        """
        Set angle mode for trigonometric functions.
        
        Args:
            mode: Either "deg" or "rad"
            
        Raises:
            ValueError: If mode is not "deg" or "rad"
        """
        if mode not in ["deg", "rad"]:
            raise ValueError(f"Invalid angle mode: {mode}. Use 'deg' or 'rad'")
        self.angle_mode = mode
    
    def get_angle_mode(self):
        """
        Get current angle mode.
        
        Returns:
            Current angle mode ("deg" or "rad")
        """
        return self.angle_mode
    
    def toggle_angle_mode(self):
        """
        Toggle between degrees and radians mode.
        
        Returns:
            New angle mode
        """
        self.angle_mode = "rad" if self.angle_mode == "deg" else "deg"
        return self.angle_mode
    
    # Statistical functions (if enhanced engine available)
    def mean(self, data):
        """
        Calculate mean of data.
        
        Args:
            data: List of numeric values
            
        Returns:
            Mean (average) of the data
        """
        if not data:
            raise ValueError("Cannot calculate mean of empty data")
        
        if self.enhanced_engine:
            # Use enhanced engine if available
            try:
                from enhanced_math_engine import _mean
                return _mean(data)
            except (ImportError, AttributeError):
                pass
        
        # Fallback implementation
        return sum(data) / len(data)
    
    def median(self, data):
        """
        Calculate median of data.
        
        Args:
            data: List of numeric values
            
        Returns:
            Median of the data
        """
        if not data:
            raise ValueError("Cannot calculate median of empty data")
        
        if self.enhanced_engine:
            # Use enhanced engine if available
            try:
                from enhanced_math_engine import _median
                return _median(data)
            except (ImportError, AttributeError):
                pass
        
        # Fallback implementation
        sorted_data = sorted(data)
        n = len(sorted_data)
        mid = n // 2
        if n % 2 == 0:
            return (sorted_data[mid-1] + sorted_data[mid]) / 2
        return sorted_data[mid]
    
    def std_dev(self, data):
        """
        Calculate standard deviation of data.
        
        Args:
            data: List of numeric values
            
        Returns:
            Standard deviation of the data
        """
        if not data:
            raise ValueError("Cannot calculate standard deviation of empty data")
        
        if self.enhanced_engine:
            # Use enhanced engine if available
            try:
                from enhanced_math_engine import _stdev
                return _stdev(data)
            except (ImportError, AttributeError):
                pass
        
        # Fallback implementation
        mean_val = self.mean(data)
        variance = sum((x - mean_val) ** 2 for x in data) / (len(data) - 1 if len(data) > 1 else 1)
        return math.sqrt(variance)
    
    def variance(self, data):
        """
        Calculate variance of data.
        
        Args:
            data: List of numeric values
            
        Returns:
            Variance of the data
        """
        if not data:
            raise ValueError("Cannot calculate variance of empty data")
        
        if self.enhanced_engine:
            # Use enhanced engine if available
            try:
                from enhanced_math_engine import _variance
                return _variance(data)
            except (ImportError, AttributeError):
                pass
        
        # Fallback implementation
        mean_val = self.mean(data)
        return sum((x - mean_val) ** 2 for x in data) / (len(data) - 1 if len(data) > 1 else 1)


# Convenience functions for direct use
def create_scientific_calculator(enhanced_math_engine=None):
    """
    Create and return a ScientificCalculator instance.
    
    Args:
        enhanced_math_engine: Optional EnhancedMathEngine instance
        
    Returns:
        ScientificCalculator instance
    """
    return ScientificCalculator(enhanced_math_engine)


if __name__ == '__main__':
    """Test scientific calculator functions."""
    print("Testing Scientific Calculator Module")
    
    sci_calc = ScientificCalculator()
    
    # Test trigonometric functions in degrees
    print("\n=== Trigonometric Functions (Degrees) ===")
    print(f"sin(30°) = {sci_calc.sin(30):.4f} (expected ~0.5000)")
    print(f"cos(0°) = {sci_calc.cos(0):.4f} (expected 1.0000)")
    print(f"tan(45°) = {sci_calc.tan(45):.4f} (expected ~1.0000)")
    
    # Test angle mode switching
    sci_calc.set_angle_mode("rad")
    print("\n=== Trigonometric Functions (Radians) ===")
    print(f"sin(π/2) = {sci_calc.sin(math.pi/2):.4f} (expected 1.0000)")
    print(f"cos(π) = {sci_calc.cos(math.pi):.4f} (expected -1.0000)")
    
    # Switch back to degrees
    sci_calc.set_angle_mode("deg")
    
    # Test inverse trig functions
    print("\n=== Inverse Trigonometric Functions ===")
    print(f"asin(0.5) = {sci_calc.asin(0.5):.4f}° (expected 30°)")
    print(f"acos(0) = {sci_calc.acos(0):.4f}° (expected 90°)")
    print(f"atan(1) = {sci_calc.atan(1):.4f}° (expected 45°)")
    
    # Test logarithms
    print("\n=== Logarithmic Functions ===")
    print(f"log(100) = {sci_calc.log(100):.4f} (expected 2.0000)")
    print(f"ln(e) = {sci_calc.ln(math.e):.4f} (expected 1.0000)")
    print(f"log2(8) = {sci_calc.log2(8):.4f} (expected 3.0000)")
    
    # Test exponential functions
    print("\n=== Exponential Functions ===")
    print(f"exp(1) = {sci_calc.exp(1):.4f} (expected ~2.7183)")
    print(f"sqrt(16) = {sci_calc.sqrt(16):.4f} (expected 4.0000)")
    print(f"pow(2, 3) = {sci_calc.pow(2, 3):.4f} (expected 8.0000)")
    
    # Test hyperbolic functions
    print("\n=== Hyperbolic Functions ===")
    print(f"sinh(0) = {sci_calc.sinh(0):.4f} (expected 0.0000)")
    print(f"cosh(0) = {sci_calc.cosh(0):.4f} (expected 1.0000)")
    print(f"tanh(0) = {sci_calc.tanh(0):.4f} (expected 0.0000)")
    
    # Test statistical functions
    print("\n=== Statistical Functions ===")
    test_data = [1, 2, 3, 4, 5]
    print(f"mean([1,2,3,4,5]) = {sci_calc.mean(test_data):.4f} (expected 3.0000)")
    print(f"median([1,2,3,4,5]) = {sci_calc.median(test_data):.4f} (expected 3.0000)")
    print(f"std_dev([1,2,3,4,5]) = {sci_calc.std_dev(test_data):.4f} (expected ~1.5811)")
    
    # Test factorial
    print("\n=== Other Functions ===")
    print(f"factorial(5) = {sci_calc.factorial(5)} (expected 120)")
    print(f"degrees(π) = {sci_calc.degrees(math.pi):.4f} (expected 180.0000)")
    print(f"radians(180) = {sci_calc.radians(180):.4f} (expected ~3.1416)")
    
    print("\n✅ All tests completed successfully!")
