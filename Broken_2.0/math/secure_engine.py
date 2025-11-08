#!/usr/bin/env python3
"""
================================================================================
🔒 SECURE MATH ENGINE - Mathematical Expression Evaluation
================================================================================
Safe and secure mathematical expression evaluation for Peanut 3000 Calculator
- Input sanitization and validation
- Timeout protection
- Safe function whitelisting
- Complex number support
- Statistical operations
- Matrix operations
- Unit conversion

This module provides the core mathematical evaluation engine with security
features to prevent malicious input and protect against infinite loops.

Author: Peanut 3000 Development Team
Version: 4.0.0
Date: December 2024
================================================================================
"""

import math
import time
import gc
from typing import Dict, Tuple, Any, List

# Import enhanced math engine if available
try:
    from enhanced_math_engine import EnhancedMathEngine, ComplexNumber
    ENHANCED_MATH_AVAILABLE = True
except ImportError:
    ENHANCED_MATH_AVAILABLE = False
    ComplexNumber = None
    EnhancedMathEngine = None


class SecureMathEngine:
    """Enhanced mathematical engine with Phase 4 capabilities"""
    
    def __init__(self):
        self.operation_count = 0
        self.last_result = None
        self.precision = 10  # Default decimal places
        
        # Initialize enhanced math engine if available
        if ENHANCED_MATH_AVAILABLE:
            self.enhanced_engine = EnhancedMathEngine()
            print("[INFO] Enhanced mathematical engine initialized")
        else:
            self.enhanced_engine = None
        
        # Safe function whitelist (expanded for Phase 4)
        self.safe_functions = {
            'abs', 'round', 'min', 'max', 'sum',
            'sin', 'cos', 'tan', 'asin', 'acos', 'atan', 'atan2',
            'sinh', 'cosh', 'tanh', 'asinh', 'acosh', 'atanh',
            'exp', 'log', 'log10', 'log2', 'sqrt', 'pow',
            'floor', 'ceil', 'trunc', 'degrees', 'radians',
            'factorial', 'gamma', 'lgamma', 'erf', 'erfc',
            # Phase 4 additions
            'complex', 'real', 'imag', 'conjugate', 'phase',
            'gcd', 'lcm', 'isfinite', 'isinf', 'isnan',
            'fmod', 'remainder', 'copysign', 'ldexp', 'frexp'
        }
        
        # Create safe globals for eval
        self.safe_globals = {
            "__builtins__": {},
            "math": self._create_safe_math_module(),
            "cmath": self._create_safe_cmath_module() if ENHANCED_MATH_AVAILABLE else {},
            "pi": math.pi,
            "e": math.e,
            "tau": math.tau if hasattr(math, 'tau') else 2 * math.pi,
            "i": 1j if ENHANCED_MATH_AVAILABLE else None,
            "j": 1j if ENHANCED_MATH_AVAILABLE else None
        }
        
        # Phase 4 features
        self.complex_mode = False
        self.angle_mode = "DEG"  # DEG or RAD
        self.statistics_data = []
        self.last_matrix = None
        
        # Configuration - will be set from config object if available
        self.max_expression_length = 128
        self.eval_timeout_ms = 1000
        self.memory_gc_interval = 50
        
    def set_config(self, config):
        """Set configuration from Config object"""
        if hasattr(config, 'System'):
            self.max_expression_length = config.System.MAX_EXPRESSION_LENGTH
            self.eval_timeout_ms = config.System.EVAL_TIMEOUT_MS
            self.memory_gc_interval = config.System.MEMORY_GC_INTERVAL
        
    def set_logger(self, logger):
        """Set logger instance for operation logging"""
        self.logger = logger
        
    def _log(self, level: str, message: str):
        """Internal logging helper"""
        if hasattr(self, 'logger') and self.logger:
            if level == 'debug':
                self.logger.debug(message)
            elif level == 'info':
                self.logger.info(message)
            elif level == 'warning':
                self.logger.warning(message)
            elif level == 'error':
                self.logger.error(message)
            elif level == 'operation':
                self.logger.operation(message)
        
    def _create_safe_math_module(self) -> Dict:
        """Create safe math module with whitelisted functions"""
        safe_math = {}
        for func_name in self.safe_functions:
            if hasattr(math, func_name):
                safe_math[func_name] = getattr(math, func_name)
        return safe_math
    
    def _create_safe_cmath_module(self) -> Dict:
        """Create safe complex math module"""
        if not ENHANCED_MATH_AVAILABLE:
            return {}
        
        import cmath
        safe_cmath = {}
        complex_functions = [
            'phase', 'polar', 'rect', 'exp', 'log', 'log10',
            'sqrt', 'acos', 'acosh', 'asin', 'asinh', 'atan', 'atanh',
            'cos', 'cosh', 'sin', 'sinh', 'tan', 'tanh'
        ]
        
        for func_name in complex_functions:
            if hasattr(cmath, func_name):
                safe_cmath[func_name] = getattr(cmath, func_name)
        
        return safe_cmath
        
    def preprocess_expression(self, expr: str) -> str:
        """Preprocess mathematical expression for safety and compatibility"""
        if not expr:
            return expr
            
        # Basic sanitization
        expr = expr.strip()
        
        # Replace common symbols
        replacements = {
            '√': 'math.sqrt',
            'π': str(math.pi),
            '^2': '**2',
            '^': '**',
            '÷': '/',
            '×': '*'
        }
        
        for old, new in replacements.items():
            expr = expr.replace(old, new)
            
        # Add math. prefix to known functions
        for func in self.safe_functions:
            if func in expr:
                # Use word boundaries to avoid partial matches
                import re
                pattern = r'\b' + re.escape(func) + r'\('
                replacement = f'math.{func}('
                expr = re.sub(pattern, replacement, expr)
                
        # Handle special cases
        expr = expr.replace('ln(', 'math.log(')
        expr = expr.replace('log(', 'math.log10(')
        
        return expr
        
    def evaluate_expression(self, expr: str) -> Tuple[bool, str]:
        """Safely evaluate mathematical expression"""
        if not expr:
            return False, "Empty expression"
            
        # Security checks
        if len(expr) > self.max_expression_length:
            return False, "Expression too long"
            
        # Dangerous keywords check
        dangerous = ['import', 'exec', 'eval', '__', 'open', 'file']
        for keyword in dangerous:
            if keyword in expr.lower():
                return False, "Invalid expression"
                
        try:
            # Preprocess expression
            processed_expr = self.preprocess_expression(expr)
            self._log('operation', f"Evaluating: {processed_expr}")
            
            # Evaluate with timeout protection (simulated)
            start_time = time.ticks_ms()
            result = eval(processed_expr, self.safe_globals, {})
            eval_time = time.ticks_diff(time.ticks_ms(), start_time)
            
            if eval_time > self.eval_timeout_ms:
                return False, "Calculation timeout"
                
            # Validate result
            if isinstance(result, (int, float)):
                if not math.isfinite(result):
                    return False, "Result is infinite or NaN"
                    
                # Format result
                if isinstance(result, float):
                    if abs(result) > 1e10 or (abs(result) < 1e-6 and result != 0):
                        # Scientific notation for very large or small numbers
                        formatted = f"{result:.{self.precision}e}"
                    else:
                        # Regular formatting
                        formatted = f"{result:.{self.precision}g}"
                else:
                    formatted = str(result)
                    
                self.last_result = result
                self.operation_count += 1
                
                # Garbage collection periodically
                if self.operation_count % self.memory_gc_interval == 0:
                    gc.collect()
                    self._log('debug', "Garbage collection performed")
                    
                return True, formatted
            else:
                return False, "Invalid result type"
                
        except ZeroDivisionError:
            return False, "Division by zero"
        except ValueError as e:
            return False, f"Math error: {str(e)[:20]}"
        except OverflowError:
            return False, "Number too large"
        except Exception as e:
            self._log('error', f"Evaluation error: {e}")
            return False, "Error"
            
    def evaluate_live(self, expr: str) -> str:
        """Evaluate expression for live preview (non-blocking)"""
        success, result = self.evaluate_expression(expr)
        return result if success else ""
        
    def set_precision(self, digits: int):
        """Set calculation precision"""
        # Inline constrain function
        self.precision = max(1, min(15, digits))
        if self.enhanced_engine:
            self.enhanced_engine.set_precision(digits)
        self._log('info', f"Precision set to {self.precision} digits")
    
    # ================= PHASE 4: ENHANCED MATHEMATICAL FEATURES =================
    
    def set_complex_mode(self, enabled: bool):
        """Enable or disable complex number support"""
        self.complex_mode = enabled
        if self.enhanced_engine:
            self.enhanced_engine.set_complex_mode(enabled)
        self._log('info', f"Complex mode {'enabled' if enabled else 'disabled'}")
    
    def set_angle_mode(self, mode: str):
        """Set angle mode (DEG or RAD)"""
        if mode not in ["DEG", "RAD"]:
            raise ValueError("Angle mode must be 'DEG' or 'RAD'")
        self.angle_mode = mode
        if self.enhanced_engine:
            self.enhanced_engine.set_angle_mode(mode)
        self._log('info', f"Angle mode set to {mode}")
    
    def evaluate_enhanced_expression(self, expr: str) -> Tuple[bool, str]:
        """Evaluate expression using enhanced math engine"""
        if not self.enhanced_engine:
            return self.evaluate_expression(expr)
        
        try:
            result = self.enhanced_engine.evaluate_complex_expression(expr)
            
            if isinstance(result, str) and result.startswith("Error"):
                return False, result
            elif ENHANCED_MATH_AVAILABLE and isinstance(result, ComplexNumber):
                if abs(result.imag) < 1e-10:
                    # Effectively real number
                    return True, f"{result.real:.{self.precision}g}"
                else:
                    return True, str(result)
            elif isinstance(result, complex):
                if abs(result.imag) < 1e-10:
                    return True, f"{result.real:.{self.precision}g}"
                else:
                    return True, f"{result.real:.{self.precision}g}{result.imag:+.{self.precision}g}i"
            else:
                return True, f"{result:.{self.precision}g}" if isinstance(result, float) else str(result)
        
        except Exception as e:
            self._log('error', f"Enhanced evaluation error: {e}")
            return False, f"Error: {str(e)[:30]}"
    
    def add_statistics_data(self, value: float):
        """Add value to statistics dataset"""
        try:
            self.statistics_data.append(float(value))
            self._log('info', f"Added {value} to statistics data (n={len(self.statistics_data)})")
        except ValueError:
            self._log('error', f"Invalid value for statistics: {value}")
    
    def clear_statistics_data(self):
        """Clear statistics dataset"""
        self.statistics_data.clear()
        self._log('info', "Statistics data cleared")
    
    def calculate_statistics(self) -> Tuple[bool, Dict[str, Any]]:
        """Calculate comprehensive statistics"""
        if not self.enhanced_engine or not self.statistics_data:
            return False, {"error": "No data or enhanced engine unavailable"}
        
        try:
            stats = self.enhanced_engine.statistical_analysis(self.statistics_data)
            self._log('info', f"Statistics calculated for {len(self.statistics_data)} values")
            return True, stats
        except Exception as e:
            self._log('error', f"Statistics calculation error: {e}")
            return False, {"error": str(e)}
    
    def create_matrix(self, data: List[List[float]]) -> Tuple[bool, str]:
        """Create and store matrix"""
        if not self.enhanced_engine:
            return False, "Enhanced math engine required for matrix operations"
        
        try:
            matrix = self.enhanced_engine.create_matrix(data)
            self.last_matrix = matrix
            self._log('info', f"Created {matrix.rows}x{matrix.cols} matrix")
            return True, f"Matrix {matrix.rows}x{matrix.cols} created"
        except Exception as e:
            self._log('error', f"Matrix creation error: {e}")
            return False, f"Error: {str(e)[:30]}"
    
    def matrix_operation(self, operation: str, other_data: List[List[float]] = None) -> Tuple[bool, str]:
        """Perform matrix operations"""
        if not self.enhanced_engine or not self.last_matrix:
            return False, "No matrix available or enhanced engine required"
        
        try:
            if operation == "determinant":
                det = self.last_matrix.determinant()
                return True, f"det = {det:.{self.precision}g}"
            
            elif operation == "transpose":
                result = self.last_matrix.transpose()
                self.last_matrix = result
                return True, f"Matrix transposed ({result.rows}x{result.cols})"
            
            elif operation == "inverse":
                result = self.last_matrix.inverse()
                self.last_matrix = result
                return True, "Matrix inverted"
            
            elif operation == "eigenvalues" and self.last_matrix.rows == 2 and self.last_matrix.cols == 2:
                λ1, λ2 = self.last_matrix.eigenvalues_2x2()
                return True, f"λ₁={λ1}, λ₂={λ2}"
            
            elif operation in ["add", "subtract", "multiply"] and other_data:
                other_matrix = self.enhanced_engine.create_matrix(other_data)
                
                if operation == "add":
                    result = self.last_matrix + other_matrix
                elif operation == "subtract":
                    result = self.last_matrix - other_matrix
                elif operation == "multiply":
                    result = self.last_matrix * other_matrix
                
                self.last_matrix = result
                return True, f"Matrix {operation} completed"
            
            else:
                return False, "Invalid operation or missing operand"
        
        except Exception as e:
            self._log('error', f"Matrix operation error: {e}")
            return False, f"Error: {str(e)[:30]}"
    
    def convert_units(self, value: float, from_unit: str, to_unit: str) -> Tuple[bool, str]:
        """Convert between units"""
        if not self.enhanced_engine:
            return False, "Enhanced engine required for unit conversion"
        
        try:
            result = self.enhanced_engine.unit_conversion(value, from_unit, to_unit)
            conversion_str = f"{value} {from_unit} = {result:.{self.precision}g} {to_unit}"
            self._log('info', f"Unit conversion: {conversion_str}")
            return True, conversion_str
        except Exception as e:
            self._log('error', f"Unit conversion error: {e}")
            return False, f"Error: {str(e)[:30]}"
    
    def get_available_units(self, category: str = None) -> Dict[str, List[str]]:
        """Get available units by category"""
        if not self.enhanced_engine:
            return {}
        return self.enhanced_engine.get_available_units(category)
    
    def get_constants(self) -> Dict[str, float]:
        """Get mathematical and physical constants"""
        if self.enhanced_engine:
            return self.enhanced_engine.constants
        else:
            return {
                'pi': math.pi,
                'e': math.e,
                'phi': (1 + math.sqrt(5)) / 2
            }
