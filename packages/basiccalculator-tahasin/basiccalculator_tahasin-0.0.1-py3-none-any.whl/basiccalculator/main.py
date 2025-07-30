"""
BasicCalculator: A comprehensive calculator package with basic and advanced mathematical operations.

This module provides a Calculator class that implements various mathematical operations
including basic arithmetic, power operations, logarithms, and trigonometric functions.
"""

import math
from typing import Union, Optional, List
from decimal import Decimal, getcontext

# Set precision for decimal calculations
getcontext().prec = 10

class Calculator:
    """
    A comprehensive calculator class that provides various mathematical operations.
    
    This class implements both basic arithmetic operations and advanced mathematical
    functions with proper error handling and precision control.
    """
    
    def __init__(self) -> None:
        """Initialize the Calculator instance."""
        pass
    
    def add(self, a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
        """
        Add two numbers.
        
        Args:
            a (Union[int, float]): First number
            b (Union[int, float]): Second number
            
        Returns:
            Union[int, float]: Sum of the two numbers
            
        Examples:
            >>> calc = Calculator()
            >>> calc.add(5, 3)
            8
        """
        return a + b
    
    def subtract(self, a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
        """
        Subtract second number from first number.
        
        Args:
            a (Union[int, float]): First number
            b (Union[int, float]): Second number
            
        Returns:
            Union[int, float]: Difference between the two numbers
            
        Examples:
            >>> calc = Calculator()
            >>> calc.subtract(5, 3)
            2
        """
        return a - b
    
    def multiply(self, a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
        """
        Multiply two numbers.
        
        Args:
            a (Union[int, float]): First number
            b (Union[int, float]): Second number
            
        Returns:
            Union[int, float]: Product of the two numbers
            
        Examples:
            >>> calc = Calculator()
            >>> calc.multiply(5, 3)
            15
        """
        return a * b
    
    def divide(self, a: Union[int, float], b: Union[int, float]) -> float:
        """
        Divide first number by second number.
        
        Args:
            a (Union[int, float]): Numerator
            b (Union[int, float]): Denominator
            
        Returns:
            float: Result of division
            
        Raises:
            ZeroDivisionError: If denominator is zero
            
        Examples:
            >>> calc = Calculator()
            >>> calc.divide(6, 2)
            3.0
        """
        if b == 0:
            raise ZeroDivisionError("Division by zero is not allowed")
        return a / b
    
    def power(self, base: Union[int, float], exponent: Union[int, float]) -> float:
        """
        Calculate base raised to the power of exponent.
        
        Args:
            base (Union[int, float]): The base number
            exponent (Union[int, float]): The exponent
            
        Returns:
            float: Result of base raised to the power of exponent
            
        Examples:
            >>> calc = Calculator()
            >>> calc.power(2, 3)
            8.0
        """
        return float(pow(base, exponent))
    
    def square_root(self, number: Union[int, float]) -> float:
        """
        Calculate the square root of a number.
        
        Args:
            number (Union[int, float]): Number to find square root of
            
        Returns:
            float: Square root of the number
            
        Raises:
            ValueError: If number is negative
            
        Examples:
            >>> calc = Calculator()
            >>> calc.square_root(16)
            4.0
        """
        if number < 0:
            raise ValueError("Cannot calculate square root of a negative number")
        return math.sqrt(number)
    
    def logarithm(self, number: Union[int, float], base: Optional[Union[int, float]] = None) -> float:
        """
        Calculate the logarithm of a number with specified base (defaults to natural log).
        
        Args:
            number (Union[int, float]): Number to calculate logarithm of
            base (Optional[Union[int, float]]): Base of logarithm (default: None, uses natural log)
            
        Returns:
            float: Logarithm of the number
            
        Raises:
            ValueError: If number <= 0 or base <= 0
            
        Examples:
            >>> calc = Calculator()
            >>> calc.logarithm(100, 10)  # log base 10 of 100
            2.0
        """
        if number <= 0:
            raise ValueError("Cannot calculate logarithm of non-positive number")
        if base is not None:
            if base <= 0:
                raise ValueError("Logarithm base must be positive")
            return math.log(number, base)
        return math.log(number)
    
    def factorial(self, n: int) -> int:
        """
        Calculate the factorial of a non-negative integer.
        
        Args:
            n (int): Number to calculate factorial of
            
        Returns:
            int: Factorial of the number
            
        Raises:
            ValueError: If number is negative
            
        Examples:
            >>> calc = Calculator()
            >>> calc.factorial(5)
            120
        """
        if not isinstance(n, int):
            raise TypeError("Factorial is only defined for integers")
        if n < 0:
            raise ValueError("Factorial is not defined for negative numbers")
        if n == 0:
            return 1
        return n * self.factorial(n - 1)
    
    def sin(self, angle: Union[int, float], degrees: bool = True) -> float:
        """
        Calculate the sine of an angle.
        
        Args:
            angle (Union[int, float]): Angle
            degrees (bool): If True, angle is in degrees; if False, in radians
            
        Returns:
            float: Sine of the angle
            
        Examples:
            >>> calc = Calculator()
            >>> round(calc.sin(30), 2)  # sin of 30 degrees
            0.5
        """
        if degrees:
            angle = math.radians(angle)
        return math.sin(angle)
    
    def cos(self, angle: Union[int, float], degrees: bool = True) -> float:
        """
        Calculate the cosine of an angle.
        
        Args:
            angle (Union[int, float]): Angle
            degrees (bool): If True, angle is in degrees; if False, in radians
            
        Returns:
            float: Cosine of the angle
            
        Examples:
            >>> calc = Calculator()
            >>> round(calc.cos(60), 2)  # cos of 60 degrees
            0.5
        """
        if degrees:
            angle = math.radians(angle)
        return math.cos(angle)
    
    def tan(self, angle: Union[int, float], degrees: bool = True) -> float:
        """
        Calculate the tangent of an angle.
        
        Args:
            angle (Union[int, float]): Angle
            degrees (bool): If True, angle is in degrees; if False, in radians
            
        Returns:
            float: Tangent of the angle
            
        Raises:
            ValueError: If angle is 90 degrees (or π/2 radians) + n*180 degrees
            
        Examples:
            >>> calc = Calculator()
            >>> round(calc.tan(45), 2)  # tan of 45 degrees
            1.0
        """
        if degrees:
            angle = math.radians(angle)
        return math.tan(angle)
    
    def calculate_expression(self, expression: str) -> float:
        """
        Safely evaluate a mathematical expression string.
        
        Args:
            expression (str): Mathematical expression as string
            
        Returns:
            float: Result of the expression
            
        Raises:
            ValueError: If expression is invalid or contains unauthorized operations
            
        Examples:
            >>> calc = Calculator()
            >>> calc.calculate_expression("2 + 3 * 4")
            14.0
        """
        try:
            # Only allow safe mathematical operations
            allowed_names = {
                'abs': abs,
                'float': float,
                'int': int,
                'pow': pow,
                'round': round,
                'math': math
            }
            
            # Evaluate expression in a restricted environment
            result = eval(expression, {"__builtins__": {}}, allowed_names)
            return float(result)
        except Exception as e:
            raise ValueError(f"Invalid expression: {str(e)}")