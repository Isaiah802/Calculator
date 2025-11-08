#!/usr/bin/env python3
"""
================================================================================
🧠 ENHANCED MATHEMATICAL ENGINE - PHASE 4 IMPLEMENTATION
================================================================================
Advanced Mathematical Engine for Peanut 3000 Calculator
- Complex number support with full arithmetic operations
- Comprehensive statistical analysis functions
- Matrix operations and linear algebra
- Advanced unit conversion system
- Enhanced precision and numerical stability

Author: Peanut 3000 Development Team - Phase 4
Version: 2.1.0
Date: November 6, 2025
================================================================================
"""

import math
import cmath
import re

# MicroPython doesn't have typing, statistics, decimal, fractions modules
# We'll implement basic stats functions ourselves

# Basic statistics functions for MicroPython
def _mean(data):
    """Calculate mean/average"""
    return sum(data) / len(data)

def _median(data):
    """Calculate median"""
    sorted_data = sorted(data)
    n = len(sorted_data)
    mid = n // 2
    if n % 2 == 0:
        return (sorted_data[mid - 1] + sorted_data[mid]) / 2
    return sorted_data[mid]

def _mode(data):
    """Calculate mode - most common value"""
    from collections import Counter
    counts = {}
    for item in data:
        counts[item] = counts.get(item, 0) + 1
    max_count = max(counts.values())
    modes = [k for k, v in counts.items() if v == max_count]
    if len(modes) == len(data):
        raise ValueError("No unique mode")
    return modes[0] if len(modes) == 1 else modes

def _variance(data):
    """Calculate variance"""
    m = _mean(data)
    return sum((x - m) ** 2 for x in data) / (len(data) - 1)

def _stdev(data):
    """Calculate standard deviation"""
    return math.sqrt(_variance(data))

def _quantiles(data, n=4):
    """Calculate quantiles (simplified version)"""
    sorted_data = sorted(data)
    result = []
    for i in range(1, n):
        pos = i * len(sorted_data) / n
        if pos == int(pos):
            result.append(sorted_data[int(pos)])
        else:
            lower = sorted_data[int(pos)]
            upper = sorted_data[int(pos) + 1] if int(pos) + 1 < len(sorted_data) else sorted_data[int(pos)]
            result.append((lower + upper) / 2)
    return result

def _correlation(x, y):
    """Calculate Pearson correlation coefficient"""
    n = len(x)
    mean_x = _mean(x)
    mean_y = _mean(y)
    
    numerator = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n))
    denom_x = sum((x[i] - mean_x) ** 2 for i in range(n))
    denom_y = sum((y[i] - mean_y) ** 2 for i in range(n))
    
    if denom_x == 0 or denom_y == 0:
        return 0
    
    return numerator / math.sqrt(denom_x * denom_y)

class ComplexNumber:
    """Enhanced complex number implementation with better formatting"""
    
    def __init__(self, real: float = 0, imag: float = 0):
        """Initialize complex number
        
        Args:
            real: Real part
            imag: Imaginary part
        """
        self.real = float(real)
        self.imag = float(imag)
        self._complex = complex(self.real, self.imag)
    
    def __str__(self) -> str:
        """String representation of complex number"""
        if self.imag == 0:
            return f"{self.real:g}"
        elif self.real == 0:
            return f"{self.imag:g}i"
        elif self.imag > 0:
            return f"{self.real:g}+{self.imag:g}i"
        else:
            return f"{self.real:g}{self.imag:g}i"
    
    def __repr__(self) -> str:
        return f"ComplexNumber({self.real}, {self.imag})"
    
    def __add__(self, other):
        """Addition"""
        if isinstance(other, (int, float)):
            return ComplexNumber(self.real + other, self.imag)
        elif isinstance(other, ComplexNumber):
            return ComplexNumber(self.real + other.real, self.imag + other.imag)
        elif isinstance(other, complex):
            return ComplexNumber(self.real + other.real, self.imag + other.imag)
        return NotImplemented
    
    def __sub__(self, other):
        """Subtraction"""
        if isinstance(other, (int, float)):
            return ComplexNumber(self.real - other, self.imag)
        elif isinstance(other, ComplexNumber):
            return ComplexNumber(self.real - other.real, self.imag - other.imag)
        elif isinstance(other, complex):
            return ComplexNumber(self.real - other.real, self.imag - other.imag)
        return NotImplemented
    
    def __mul__(self, other):
        """Multiplication"""
        if isinstance(other, (int, float)):
            return ComplexNumber(self.real * other, self.imag * other)
        elif isinstance(other, ComplexNumber):
            result = self._complex * other._complex
            return ComplexNumber(result.real, result.imag)
        elif isinstance(other, complex):
            result = self._complex * other
            return ComplexNumber(result.real, result.imag)
        return NotImplemented
    
    def __truediv__(self, other):
        """Division"""
        if isinstance(other, (int, float)):
            if other == 0:
                raise ZeroDivisionError("Division by zero")
            return ComplexNumber(self.real / other, self.imag / other)
        elif isinstance(other, (ComplexNumber, complex)):
            if isinstance(other, ComplexNumber):
                other_complex = other._complex
            else:
                other_complex = other
            
            if abs(other_complex) == 0:
                raise ZeroDivisionError("Division by zero")
            
            result = self._complex / other_complex
            return ComplexNumber(result.real, result.imag)
        return NotImplemented
    
    def magnitude(self) -> float:
        """Calculate magnitude (absolute value)"""
        return abs(self._complex)
    
    def phase(self) -> float:
        """Calculate phase angle in radians"""
        return cmath.phase(self._complex)
    
    def conjugate(self):
        """Complex conjugate"""
        return ComplexNumber(self.real, -self.imag)
    
    def to_polar(self) :
        """Convert to polar form (magnitude, phase)"""
        return (self.magnitude(), self.phase())
    
    @classmethod
    def from_polar(cls, magnitude: float, phase: float):
        """Create from polar coordinates"""
        real = magnitude * math.cos(phase)
        imag = magnitude * math.sin(phase)
        return cls(real, imag)

class StatisticalEngine:
    """Comprehensive statistical analysis engine"""
    
    @staticmethod
    def descriptive_stats(data) :
        """Calculate comprehensive descriptive statistics
        
        Args:
            data: List of numerical values
            
        Returns:
            Dictionary with statistical measures
        """
        if not data:
            raise ValueError("Cannot calculate statistics for empty dataset")
        
        n = len(data)
        sorted_data = sorted(data)
        
        # Basic measures
        mean_val = _mean(data)
        median_val = _median(data)
        
        # Mode (handle multimodal cases)
        try:
            mode_val = _mode(data)
        except ValueError:
            mode_val = "No unique mode"
        
        # Variance and standard deviation
        if n > 1:
            variance_val = _variance(data)
            stdev_val = _stdev(data)
        else:
            variance_val = 0
            stdev_val = 0
        
        # Range and quartiles
        min_val = min(data)
        max_val = max(data)
        range_val = max_val - min_val
        
        q1 = _quantiles(data, n=4)[0] if n > 3 else sorted_data[0]
        q3 = _quantiles(data, n=4)[2] if n > 3 else sorted_data[-1]
        iqr = q3 - q1
        
        # Advanced measures
        skewness = StatisticalEngine._calculate_skewness(data, mean_val, stdev_val)
        kurtosis = StatisticalEngine._calculate_kurtosis(data, mean_val, stdev_val)
        
        return {
            'count': n,
            'mean': mean_val,
            'median': median_val,
            'mode': mode_val,
            'min': min_val,
            'max': max_val,
            'range': range_val,
            'variance': variance_val,
            'std_dev': stdev_val,
            'q1': q1,
            'q3': q3,
            'iqr': iqr,
            'skewness': skewness,
            'kurtosis': kurtosis
        }
    
    @staticmethod
    def _calculate_skewness(data, mean: float, stdev: float) -> float:
        """Calculate skewness (third moment)"""
        if stdev == 0:
            return 0
        n = len(data)
        return sum(((x - mean) / stdev) ** 3 for x in data) / n
    
    @staticmethod
    def _calculate_kurtosis(data, mean: float, stdev: float) -> float:
        """Calculate kurtosis (fourth moment)"""
        if stdev == 0:
            return 0
        n = len(data)
        return sum(((x - mean) / stdev) ** 4 for x in data) / n - 3
    
    @staticmethod
    def correlation(x, y) -> float:
        """Calculate Pearson correlation coefficient"""
        if len(x) != len(y):
            raise ValueError("Datasets must have equal length")
        if len(x) < 2:
            raise ValueError("Need at least 2 data points")
        
        return _correlation(x, y)
    
    @staticmethod
    def linear_regression(x, y) :
        """Calculate linear regression parameters"""
        if len(x) != len(y):
            raise ValueError("Datasets must have equal length")
        if len(x) < 2:
            raise ValueError("Need at least 2 data points")
        
        n = len(x)
        mean_x = _mean(x)
        mean_y = _mean(y)
        
        # Calculate slope (b1) and intercept (b0)
        numerator = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n))
        denominator = sum((x[i] - mean_x) ** 2 for i in range(n))
        
        if denominator == 0:
            raise ValueError("Cannot perform regression: no variation in x")
        
        slope = numerator / denominator
        intercept = mean_y - slope * mean_x
        
        # Calculate R-squared
        y_pred = [intercept + slope * xi for xi in x]
        ss_res = sum((y[i] - y_pred[i]) ** 2 for i in range(n))
        ss_tot = sum((y[i] - mean_y) ** 2 for i in range(n))
        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 1
        
        return {
            'slope': slope,
            'intercept': intercept,
            'r_squared': r_squared,
            'equation': f"y = {slope:.6f}x + {intercept:.6f}"
        }
    
    @staticmethod
    def probability_distributions(data) :
        """Test data against common probability distributions"""
        stats = StatisticalEngine.descriptive_stats(data)
        
        # Normal distribution parameters
        normal_params = {
            'mean': stats['mean'],
            'std_dev': stats['std_dev']
        }
        
        # Test for normality (simplified Shapiro-Wilk approximation)
        normality_score = StatisticalEngine._test_normality(data)
        
        return {
            'normal': normal_params,
            'normality_score': normality_score,
            'is_likely_normal': normality_score > 0.05
        }
    
    @staticmethod
    def _test_normality(data) -> float:
        """Simplified normality test"""
        # This is a simplified version - in practice, use scipy.stats
        stats = StatisticalEngine.descriptive_stats(data)
        
        # Check if skewness and kurtosis are close to normal distribution values
        skew_score = 1 - min(1, abs(stats['skewness']) / 2)
        kurt_score = 1 - min(1, abs(stats['kurtosis']) / 4)
        
        return (skew_score + kurt_score) / 2

class MatrixEngine:
    """Matrix operations and linear algebra"""
    
    def __init__(self, data):
        """Initialize matrix
        
        Args:
            data: 2D list representing matrix rows
        """
        if not data or not data[0]:
            raise ValueError("Matrix cannot be empty")
        
        # Validate rectangular matrix
        rows = len(data)
        cols = len(data[0])
        
        for row in data:
            if len(row) != cols:
                raise ValueError("All matrix rows must have same length")
        
        self.data = [row[:] for row in data]  # Deep copy
        self.rows = rows
        self.cols = cols
    
    def __str__(self) -> str:
        """String representation of matrix"""
        return '\n'.join(['[' + ', '.join(f'{val:8.3f}' for val in row) + ']' 
                         for row in self.data])
    
    def __add__(self, other):
        """Matrix addition"""
        if not isinstance(other, MatrixEngine):
            raise TypeError("Can only add matrices to matrices")
        
        if self.rows != other.rows or self.cols != other.cols:
            raise ValueError("Matrices must have same dimensions for addition")
        
        result = []
        for i in range(self.rows):
            row = []
            for j in range(self.cols):
                row.append(self.data[i][j] + other.data[i][j])
            result.append(row)
        
        return MatrixEngine(result)
    
    def __sub__(self, other):
        """Matrix subtraction"""
        if not isinstance(other, MatrixEngine):
            raise TypeError("Can only subtract matrices from matrices")
        
        if self.rows != other.rows or self.cols != other.cols:
            raise ValueError("Matrices must have same dimensions for subtraction")
        
        result = []
        for i in range(self.rows):
            row = []
            for j in range(self.cols):
                row.append(self.data[i][j] - other.data[i][j])
            result.append(row)
        
        return MatrixEngine(result)
    
    def __mul__(self, other):
        """Matrix multiplication or scalar multiplication"""
        if isinstance(other, (int, float)):
            # Scalar multiplication
            result = []
            for i in range(self.rows):
                row = []
                for j in range(self.cols):
                    row.append(self.data[i][j] * other)
                result.append(row)
            return MatrixEngine(result)
        
        elif isinstance(other, MatrixEngine):
            # Matrix multiplication
            if self.cols != other.rows:
                raise ValueError("Number of columns in first matrix must equal number of rows in second")
            
            result = []
            for i in range(self.rows):
                row = []
                for j in range(other.cols):
                    sum_val = 0
                    for k in range(self.cols):
                        sum_val += self.data[i][k] * other.data[k][j]
                    row.append(sum_val)
                result.append(row)
            
            return MatrixEngine(result)
        
        else:
            raise TypeError("Can only multiply matrix by scalar or matrix")
    
    def transpose(self):
        """Matrix transpose"""
        result = []
        for j in range(self.cols):
            row = []
            for i in range(self.rows):
                row.append(self.data[i][j])
            result.append(row)
        
        return MatrixEngine(result)
    
    def determinant(self) -> float:
        """Calculate matrix determinant (for square matrices)"""
        if self.rows != self.cols:
            raise ValueError("Determinant only defined for square matrices")
        
        return self._determinant_recursive(self.data)
    
    def _determinant_recursive(self, matrix):
        """Recursive determinant calculation"""
        n = len(matrix)
        
        if n == 1:
            return matrix[0][0]
        
        if n == 2:
            return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]
        
        det = 0
        for j in range(n):
            # Create minor matrix
            minor = []
            for i in range(1, n):
                row = []
                for k in range(n):
                    if k != j:
                        row.append(matrix[i][k])
                minor.append(row)
            
            # Calculate cofactor
            cofactor = ((-1) ** j) * matrix[0][j] * self._determinant_recursive(minor)
            det += cofactor
        
        return det
    
    def inverse(self):
        """Calculate matrix inverse using Gauss-Jordan elimination"""
        if self.rows != self.cols:
            raise ValueError("Inverse only defined for square matrices")
        
        n = self.rows
        det = self.determinant()
        
        if abs(det) < 1e-10:
            raise ValueError("Matrix is singular (determinant is zero)")
        
        # Create augmented matrix [A|I]
        augmented = []
        for i in range(n):
            row = self.data[i][:] + [0] * n
            row[n + i] = 1  # Identity matrix on right side
            augmented.append(row)
        
        # Gauss-Jordan elimination
        for i in range(n):
            # Find pivot
            max_row = i
            for k in range(i + 1, n):
                if abs(augmented[k][i]) > abs(augmented[max_row][i]):
                    max_row = k
            
            # Swap rows
            augmented[i], augmented[max_row] = augmented[max_row], augmented[i]
            
            # Make diagonal element 1
            pivot = augmented[i][i]
            if abs(pivot) < 1e-10:
                raise ValueError("Matrix is singular")
            
            for j in range(2 * n):
                augmented[i][j] /= pivot
            
            # Eliminate column
            for k in range(n):
                if k != i:
                    factor = augmented[k][i]
                    for j in range(2 * n):
                        augmented[k][j] -= factor * augmented[i][j]
        
        # Extract inverse matrix
        inverse_data = []
        for i in range(n):
            inverse_data.append(augmented[i][n:])
        
        return MatrixEngine(inverse_data)
    
    def eigenvalues_2x2(self) :
        """Calculate eigenvalues for 2x2 matrix"""
        if self.rows != 2 or self.cols != 2:
            raise ValueError("This method only works for 2x2 matrices")
        
        a = self.data[0][0]
        b = self.data[0][1]
        c = self.data[1][0]
        d = self.data[1][1]
        
        # Characteristic polynomial: λ² - (a+d)λ + (ad-bc) = 0
        trace = a + d
        det = a * d - b * c
        
        discriminant = trace * trace - 4 * det
        
        if discriminant >= 0:
            sqrt_disc = math.sqrt(discriminant)
            lambda1 = (trace + sqrt_disc) / 2
            lambda2 = (trace - sqrt_disc) / 2
        else:
            sqrt_disc = math.sqrt(-discriminant)
            lambda1 = complex(trace / 2, sqrt_disc / 2)
            lambda2 = complex(trace / 2, -sqrt_disc / 2)
        
        return lambda1, lambda2

class UnitConverter:
    """Comprehensive unit conversion system"""
    
    def __init__(self):
        """Initialize unit conversion database"""
        # Define unit conversion factors (all relative to base SI units)
        self.conversions = {
            'length': {
                'base': 'm',  # meter
                'units': {
                    'mm': 0.001,
                    'cm': 0.01,
                    'm': 1.0,
                    'km': 1000.0,
                    'in': 0.0254,
                    'ft': 0.3048,
                    'yd': 0.9144,
                    'mi': 1609.344,
                    'nmi': 1852.0,  # nautical mile
                    'Å': 1e-10,     # angstrom
                    'μm': 1e-6,     # micrometer
                    'nm': 1e-9,     # nanometer
                    'pm': 1e-12,    # picometer
                    'ly': 9.461e15, # light year
                    'au': 1.496e11, # astronomical unit
                    'pc': 3.086e16  # parsec
                }
            },
            'mass': {
                'base': 'kg',  # kilogram
                'units': {
                    'mg': 1e-6,
                    'g': 0.001,
                    'kg': 1.0,
                    'oz': 0.0283495,
                    'lb': 0.453592,
                    'ton': 1000.0,
                    'u': 1.66054e-27,  # atomic mass unit
                    'slug': 14.5939,
                    'stone': 6.35029
                }
            },
            'time': {
                'base': 's',   # second
                'units': {
                    'ns': 1e-9,
                    'μs': 1e-6,
                    'ms': 0.001,
                    's': 1.0,
                    'min': 60.0,
                    'h': 3600.0,
                    'day': 86400.0,
                    'week': 604800.0,
                    'month': 2.628e6,  # average month
                    'year': 3.156e7,   # average year
                    'decade': 3.156e8,
                    'century': 3.156e9,
                    'millennium': 3.156e10
                }
            },
            'temperature': {
                'base': 'K',   # Kelvin
                'special': True  # Requires special conversion logic
            },
            'area': {
                'base': 'm²',
                'units': {
                    'mm²': 1e-6,
                    'cm²': 1e-4,
                    'm²': 1.0,
                    'km²': 1e6,
                    'in²': 6.4516e-4,
                    'ft²': 0.092903,
                    'yd²': 0.836127,
                    'mi²': 2.59e6,
                    'acre': 4046.86,
                    'ha': 10000.0,  # hectare
                    'barn': 1e-28   # nuclear cross-section
                }
            },
            'volume': {
                'base': 'm³',
                'units': {
                    'mm³': 1e-9,
                    'cm³': 1e-6,
                    'dm³': 0.001,
                    'm³': 1.0,
                    'L': 0.001,     # liter
                    'mL': 1e-6,
                    'in³': 1.6387e-5,
                    'ft³': 0.0283168,
                    'gal': 0.00378541,  # US gallon
                    'qt': 0.000946353,  # US quart
                    'pt': 0.000473176,  # US pint
                    'cup': 0.000236588,
                    'fl_oz': 2.9574e-5, # US fluid ounce
                    'tbsp': 1.4787e-5,  # tablespoon
                    'tsp': 4.9289e-6,   # teaspoon
                    'bbl': 0.158987,    # barrel (oil)
                }
            },
            'energy': {
                'base': 'J',   # joule
                'units': {
                    'J': 1.0,
                    'kJ': 1000.0,
                    'MJ': 1e6,
                    'GJ': 1e9,
                    'cal': 4.184,      # calorie
                    'kcal': 4184.0,    # kilocalorie
                    'eV': 1.602e-19,   # electron volt
                    'keV': 1.602e-16,
                    'MeV': 1.602e-13,
                    'GeV': 1.602e-10,
                    'Wh': 3600.0,      # watt hour
                    'kWh': 3.6e6,
                    'BTU': 1055.06,    # British thermal unit
                    'thm': 1.055e8,    # therm
                    'erg': 1e-7,
                    'ft⋅lb': 1.35582   # foot-pound
                }
            },
            'power': {
                'base': 'W',   # watt
                'units': {
                    'mW': 0.001,
                    'W': 1.0,
                    'kW': 1000.0,
                    'MW': 1e6,
                    'GW': 1e9,
                    'hp': 745.7,       # mechanical horsepower
                    'PS': 735.5,       # metric horsepower
                    'BTU/h': 0.293071,
                    'cal/s': 4.184,
                    'kcal/h': 1.163,
                    'ft⋅lb/s': 1.35582
                }
            },
            'pressure': {
                'base': 'Pa',  # pascal
                'units': {
                    'Pa': 1.0,
                    'kPa': 1000.0,
                    'MPa': 1e6,
                    'GPa': 1e9,
                    'bar': 100000.0,
                    'mbar': 100.0,
                    'atm': 101325.0,   # standard atmosphere
                    'psi': 6894.76,    # pounds per square inch
                    'Torr': 133.322,   # torr (mmHg)
                    'mmHg': 133.322,
                    'inHg': 3386.39,   # inches of mercury
                    'mmH2O': 9.80665,  # millimeters of water
                    'inH2O': 249.089   # inches of water
                }
            },
            'frequency': {
                'base': 'Hz',  # hertz
                'units': {
                    'Hz': 1.0,
                    'kHz': 1000.0,
                    'MHz': 1e6,
                    'GHz': 1e9,
                    'THz': 1e12,
                    'rpm': 1/60.0,     # revolutions per minute
                    'rad/s': 1/(2*math.pi),  # radians per second
                }
            }
        }
    
    def convert(self, value: float, from_unit: str, to_unit: str) -> float:
        """Convert between units
        
        Args:
            value: Value to convert
            from_unit: Source unit
            to_unit: Target unit
            
        Returns:
            Converted value
        """
        # Find which category these units belong to
        from_category = None
        to_category = None
        
        for category, data in self.conversions.items():
            if category == 'temperature':
                continue  # Handle temperature separately
            
            if from_unit in data['units']:
                from_category = category
            if to_unit in data['units']:
                to_category = category
        
        if from_category != to_category or from_category is None:
            # Check if it's temperature conversion
            if self._is_temperature_unit(from_unit) and self._is_temperature_unit(to_unit):
                return self._convert_temperature(value, from_unit, to_unit)
            else:
                raise ValueError(f"Cannot convert between {from_unit} and {to_unit}")
        
        # Convert to base unit, then to target unit
        category_data = self.conversions[from_category]
        from_factor = category_data['units'][from_unit]
        to_factor = category_data['units'][to_unit]
        
        # value * from_factor = base_value
        # base_value / to_factor = target_value
        return value * from_factor / to_factor
    
    def _is_temperature_unit(self, unit: str) -> bool:
        """Check if unit is a temperature unit"""
        temp_units = ['K', 'C', 'F', 'R']  # Kelvin, Celsius, Fahrenheit, Rankine
        return unit in temp_units
    
    def _convert_temperature(self, value: float, from_unit: str, to_unit: str) -> float:
        """Convert between temperature units"""
        # First convert to Kelvin
        if from_unit == 'K':
            kelvin = value
        elif from_unit == 'C':
            kelvin = value + 273.15
        elif from_unit == 'F':
            kelvin = (value - 32) * 5/9 + 273.15
        elif from_unit == 'R':
            kelvin = value * 5/9
        else:
            raise ValueError(f"Unknown temperature unit: {from_unit}")
        
        # Then convert from Kelvin to target unit
        if to_unit == 'K':
            return kelvin
        elif to_unit == 'C':
            return kelvin - 273.15
        elif to_unit == 'F':
            return (kelvin - 273.15) * 9/5 + 32
        elif to_unit == 'R':
            return kelvin * 9/5
        else:
            raise ValueError(f"Unknown temperature unit: {to_unit}")
    
    def get_units_in_category(self, category: str) :
        """Get all units in a given category"""
        if category not in self.conversions:
            raise ValueError(f"Unknown category: {category}")
        
        if category == 'temperature':
            return ['K', 'C', 'F', 'R']
        else:
            return list(self.conversions[category]['units'].keys())
    
    def get_all_categories(self) :
        """Get all available unit categories"""
        return list(self.conversions.keys())

class EnhancedMathEngine:
    """Main enhanced mathematical engine combining all advanced features"""
    
    def __init__(self):
        """Initialize enhanced math engine"""
        self.complex_mode = False
        self.angle_mode = "DEG"  # DEG or RAD
        self.precision = 15
        self.unit_converter = UnitConverter()
        
        # Constants
        self.constants = {
            'pi': math.pi,
            'e': math.e,
            'phi': (1 + math.sqrt(5)) / 2,  # Golden ratio
            'c': 299792458,                 # Speed of light (m/s)
            'h': 6.62607e-34,              # Planck constant
            'k': 1.38065e-23,              # Boltzmann constant
            'NA': 6.02214e23,              # Avogadro's number
            'R': 8.31446,                  # Gas constant
            'g': 9.80665,                  # Standard gravity
            'G': 6.67430e-11,              # Gravitational constant
        }
    
    def evaluate_complex_expression(self, expression: str) :
        """Evaluate expression with complex number support"""
        try:
            # Handle special functions and constants
            processed_expr = self._preprocess_expression(expression)
            
            # Parse complex numbers in expression
            processed_expr = self._parse_complex_notation(processed_expr)
            
            # Evaluate safely
            result = self._safe_evaluate(processed_expr)
            
            if self.complex_mode and isinstance(result, complex):
                return ComplexNumber(result.real, result.imag)
            elif isinstance(result, complex) and result.imag == 0:
                return result.real
            elif isinstance(result, complex):
                return ComplexNumber(result.real, result.imag)
            else:
                return result
        
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _preprocess_expression(self, expr: str) -> str:
        """Preprocess expression to handle special functions and constants"""
        # Replace constants
        for name, value in self.constants.items():
            expr = re.sub(r'\b' + name + r'\b', str(value), expr)
        
        # Handle angle mode for trig functions
        if self.angle_mode == "DEG":
            # Convert degrees to radians for trig functions
            trig_functions = ['sin', 'cos', 'tan', 'asin', 'acos', 'atan']
            for func in trig_functions:
                if func in expr:
                    if func.startswith('a'):  # Inverse functions
                        # Convert result from radians to degrees
                        expr = re.sub(f'{func}\\(', f'math.degrees(math.{func}(', expr)
                    else:
                        # Convert input from degrees to radians
                        expr = re.sub(f'{func}\\(', f'math.{func}(math.radians(', expr)
                        expr = re.sub(f'math\\.{func}\\(math\\.radians\\(([^)]+)\\)', 
                                    f'math.{func}(math.radians(\\1))', expr)
        
        return expr
    
    def _parse_complex_notation(self, expr: str) -> str:
        """Parse complex number notation (e.g., 3+4i, 2-5j)"""
        # Replace 'i' or 'j' with Python's 'j' for imaginary unit
        expr = re.sub(r'(\d+(?:\.\d+)?)i\b', r'\1j', expr)
        expr = re.sub(r'i\b', 'j', expr)
        
        return expr
    
    def _safe_evaluate(self, expr: str) :
        """Safely evaluate mathematical expression"""
        # Define safe namespace for evaluation
        safe_dict = {
            '__builtins__': {},
            'abs': abs,
            'pow': pow,
            'round': round,
            'math': math,
            'cmath': cmath,
            'complex': complex,
            'sqrt': math.sqrt,
            'sin': math.sin,
            'cos': math.cos,
            'tan': math.tan,
            'asin': math.asin,
            'acos': math.acos,
            'atan': math.atan,
            'sinh': math.sinh,
            'cosh': math.cosh,
            'tanh': math.tanh,
            'log': math.log10,
            'ln': math.log,
            'exp': math.exp,
            'factorial': math.factorial,
            'degrees': math.degrees,
            'radians': math.radians,
            'pi': math.pi,
            'e': math.e,
        }
        
        return eval(expr, safe_dict, {})
    
    def create_matrix(self, data):
        """Create matrix from data"""
        return MatrixEngine(data)
    
    def create_complex(self, real: float = 0, imag: float = 0) -> ComplexNumber:
        """Create complex number"""
        return ComplexNumber(real, imag)
    
    def statistical_analysis(self, data) :
        """Perform comprehensive statistical analysis"""
        return StatisticalEngine.descriptive_stats(data)
    
    def unit_conversion(self, value: float, from_unit: str, to_unit: str) -> float:
        """Convert between units"""
        return self.unit_converter.convert(value, from_unit, to_unit)
    
    def get_available_units(self, category=None):
        """Get available units by category"""
        if category:
            return {category: self.unit_converter.get_units_in_category(category)}
        else:
            result = {}
            for cat in self.unit_converter.get_all_categories():
                if cat == 'temperature':
                    result[cat] = ['K', 'C', 'F', 'R']
                else:
                    result[cat] = self.unit_converter.get_units_in_category(cat)
            return result
    
    def set_angle_mode(self, mode: str):
        """Set angle mode (DEG or RAD)"""
        if mode not in ["DEG", "RAD"]:
            raise ValueError("Angle mode must be 'DEG' or 'RAD'")
        self.angle_mode = mode
    
    def set_complex_mode(self, enabled: bool):
        """Enable or disable complex number mode"""
        self.complex_mode = enabled
    
    def set_precision(self, precision: int):
        """Set decimal precision"""
        if precision < 1 or precision > 50:
            raise ValueError("Precision must be between 1 and 50")
        self.precision = precision
        # Note: MicroPython doesn't have decimal.getcontext(), so precision is just stored

# Test function for demonstration
def test_enhanced_math_engine():
    """Test the enhanced mathematical engine"""
    engine = EnhancedMathEngine()
    
    print("🧠 Enhanced Mathematical Engine Test Suite")
    print("=" * 50)
    
    # Test complex numbers
    print("\n📐 Complex Number Operations:")
    engine.set_complex_mode(True)
    
    z1 = engine.create_complex(3, 4)
    z2 = engine.create_complex(1, -2)
    
    print(f"z1 = {z1}")
    print(f"z2 = {z2}")
    print(f"z1 + z2 = {z1 + z2}")
    print(f"z1 * z2 = {z1 * z2}")
    print(f"|z1| = {z1.magnitude():.3f}")
    print(f"∠z1 = {z1.phase():.3f} radians")
    
    # Test statistical analysis
    print("\n📊 Statistical Analysis:")
    data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    stats = engine.statistical_analysis(data)
    
    print(f"Data: {data}")
    print(f"Mean: {stats['mean']:.3f}")
    print(f"Median: {stats['median']:.3f}")
    print(f"Std Dev: {stats['std_dev']:.3f}")
    print(f"Skewness: {stats['skewness']:.3f}")
    
    # Test matrix operations
    print("\n🔢 Matrix Operations:")
    matrix_data = [[1, 2], [3, 4]]
    matrix = engine.create_matrix(matrix_data)
    
    print(f"Matrix A:")
    print(matrix)
    print(f"Determinant: {matrix.determinant()}")
    
    try:
        inverse = matrix.inverse()
        print(f"Inverse:")
        print(inverse)
    except ValueError as e:
        print(f"Inverse error: {e}")
    
    # Test unit conversions
    print("\n📏 Unit Conversions:")
    print(f"100 cm = {engine.unit_conversion(100, 'cm', 'm')} m")
    print(f"32 °F = {engine.unit_conversion(32, 'F', 'C'):.1f} °C")
    print(f"1 hp = {engine.unit_conversion(1, 'hp', 'W'):.1f} W")
    
    # Test advanced expressions
    print("\n🧮 Advanced Expression Evaluation:")
    engine.set_angle_mode("DEG")
    expressions = [
        "sin(30) + cos(60)",
        "sqrt(-1)",
        "e^(pi*i) + 1",
        "log(100) + ln(e)"
    ]
    
    for expr in expressions:
        result = engine.evaluate_complex_expression(expr)
        print(f"{expr} = {result}")

if __name__ == "__main__":
    test_enhanced_math_engine()
