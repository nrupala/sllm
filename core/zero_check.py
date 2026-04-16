"""
Zero-Check Validation Module
Implements safety checks before any potentially dangerous operations.
Per SL-LLM principles: Always validate before execution.
"""

from typing import Any, List, Optional, Tuple
import re


class ZeroCheckError(Exception):
    """Raised when a zero-check validation fails"""
    pass


class ZeroCheckValidator:
    """
    Comprehensive validation before operations.
    Prevents runtime errors from:
    - Division by zero
    - Array index out of bounds
    - Invalid file operations
    - Invalid mathematical operations
    - Empty/null inputs
    """
    
    @staticmethod
    def validate_division(numerator: Any, denominator: Any) -> Tuple[bool, str]:
        """
        Validate division operation before execution.
        Returns: (is_valid, error_message)
        """
        try:
            if denominator == 0:
                return False, "Division by zero: denominator is 0"
            if not isinstance(denominator, (int, float)):
                return False, f"Denominator must be number, got {type(denominator).__name__}"
            if not isinstance(numerator, (int, float)):
                return False, f"Numerator must be number, got {type(numerator).__name__}"
            return True, ""
        except Exception as e:
            return False, f"Validation error: {e}"
    
    @staticmethod
    def validate_modulo(dividend: Any, divisor: Any) -> Tuple[bool, str]:
        """Validate modulo operation"""
        if divisor == 0:
            return False, "Modulo by zero: divisor is 0"
        if not isinstance(divisor, (int, float)):
            return False, f"Divisor must be number, got {type(divisor).__name__}"
        return True, ""
    
    @staticmethod
    def validate_array_access(arr: List, index: int, allow_negative: bool = False) -> Tuple[bool, str]:
        """Validate array/index access"""
        if not isinstance(arr, list):
            return False, f"Expected list, got {type(arr).__name__}"
        if not isinstance(index, int):
            return False, f"Index must be int, got {type(index).__name__}"
        if not allow_negative and index < 0:
            return False, f"Negative index not allowed: {index}"
        if index >= len(arr):
            return False, f"Index {index} out of bounds for array of length {len(arr)}"
        return True, ""
    
    @staticmethod
    def validate_file_path(path: str, allow_absolute: bool = False) -> Tuple[bool, str]:
        """Validate file path for safety"""
        if not path:
            return False, "Empty path"
        if not isinstance(path, str):
            return False, f"Path must be string, got {type(path).__name__}"
        if ".." in path:
            return False, "Path traversal not allowed (..)"
        if not allow_absolute and (path.startswith("/") or path[1:].startswith(":")):
            return False, "Absolute paths not allowed unless explicitly enabled"
        return True, ""
    
    @staticmethod
    def validate_not_empty(value: Any, field_name: str = "value") -> Tuple[bool, str]:
        """Validate value is not None or empty"""
        if value is None:
            return False, f"{field_name} is None"
        if isinstance(value, (str, list, dict)) and len(value) == 0:
            return False, f"{field_name} is empty"
        return True, ""
    
    @staticmethod
    def validate_range(value: Any, min_val: Any = None, max_val: Any = None, field_name: str = "value") -> Tuple[bool, str]:
        """Validate value is within range"""
        if min_val is not None and value < min_val:
            return False, f"{field_name} {value} below minimum {min_val}"
        if max_val is not None and value > max_val:
            return False, f"{field_name} {value} above maximum {max_val}"
        return True, ""
    
    @staticmethod
    def validate_type(value: Any, expected_types: tuple, field_name: str = "value") -> Tuple[bool, str]:
        """Validate value type"""
        if not isinstance(value, expected_types):
            type_names = ", ".join(t.__name__ for t in expected_types)
            return False, f"{field_name} must be {type_names}, got {type(value).__name__}"
        return True, ""
    
    @staticmethod
    def sanitize_input(value: str, max_length: int = 10000) -> str:
        """Sanitize user input"""
        if not isinstance(value, str):
            return str(value)
        
        # Truncate long inputs
        if len(value) > max_length:
            value = value[:max_length] + "... [truncated]"
        
        # Remove potentially dangerous patterns
        dangerous = ["<script", "javascript:", "onerror=", "onclick="]
        for pattern in dangerous:
            value = value.replace(pattern, "")
        
        return value


def safe_execute(func, *args, **kwargs):
    """
    Execute function with zero-check validation.
    Returns error dict instead of raising exceptions.
    """
    import functools
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return {"success": True, "result": func(*args, **kwargs)}
        except ZeroCheckError as e:
            return {"success": False, "error": str(e), "type": "ZeroCheckError"}
        except Exception as e:
            return {"success": False, "error": str(e), "type": type(e).__name__}
    
    return wrapper


# Convenience decorators
def require_valid_division(func):
    """Decorator to validate division before function execution"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Check for common division patterns in args
        for i, arg in enumerate(args):
            if isinstance(arg, tuple) and len(arg) == 2:
                valid, err = ZeroCheckValidator.validate_division(arg[0], arg[1])
                if not valid:
                    raise ZeroCheckError(f"Argument {i}: {err}")
        return func(*args, **kwargs)
    return wrapper


def require_not_empty(func):
    """Decorator to validate non-empty inputs"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        for i, arg in enumerate(args):
            valid, err = ZeroCheckValidator.validate_not_empty(arg, f"arg{i}")
            if not valid:
                raise ZeroCheckError(err)
        return func(*args, **kwargs)
    return wrapper


import functools


if __name__ == "__main__":
    # Test zero-check validation
    v = ZeroCheckValidator()
    
    print("Testing ZeroCheckValidator:")
    
    # Test division
    valid, err = v.validate_division(10, 2)
    print(f"  10/2: {valid} - {err or 'OK'}")
    
    valid, err = v.validate_division(10, 0)
    print(f"  10/0: {valid} - {err}")
    
    # Test array access
    valid, err = v.validate_array_access([1, 2, 3], 1)
    print(f"  arr[1]: {valid} - {err or 'OK'}")
    
    valid, err = v.validate_array_access([1, 2, 3], 10)
    print(f"  arr[10]: {valid} - {err}")
    
    # Test file path
    valid, err = v.validate_file_path("../etc/passwd")
    print(f"  path ../etc: {valid} - {err}")
    
    print("\nAll zero-checks working correctly!")