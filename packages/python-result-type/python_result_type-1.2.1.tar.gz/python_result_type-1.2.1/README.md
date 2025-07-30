# Python Result Type

[![PyPI version](https://badge.fury.io/py/python-result-type.svg)](https://badge.fury.io/py/python-result-type)
[![Python Support](https://img.shields.io/pypi/pyversions/python-result-type.svg)](https://pypi.org/project/python-result-type/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/yourusername/python-result-type/workflows/tests/badge.svg)](https://github.com/yourusername/python-result-type/actions)

A functional programming **Result type** for Python, inspired by Rust's `Result<T, E>` and similar to PyMonad's Either, but with more intuitive naming (`Success`/`Failure` instead of `Right`/`Left`).

## 🚀 Features

- **Intuitive API**: `Success` and `Failure` instead of cryptic `Right`/`Left`
- **Rust-like Aliases**: Optional `Ok` and `Err` aliases for Rust developers
- **Type Safe**: Full generic type support with `Result[T, E]`  
- **Chainable Operations**: Use `.then()` method or `>>` operator for clean chaining
- **Exception Safety**: Automatic exception handling in chained operations
- **Async/Await Support**: Full async support with `AsyncResult` wrapper
- **Zero Dependencies**: Pure Python with no external dependencies
- **Comprehensive**: Includes helper functions and decorators for common patterns
- **Well Tested**: 100% test coverage with extensive edge case testing

## 📦 Installation

```bash
pip install python-result-type
```

## 🎯 Quick Start

### Basic Usage

```python
from result_type import Success, Failure, Result

def divide(a: float, b: float) -> Result[float, str]:
    if b == 0:
        return Failure("Division by zero")
    return Success(a / b)

# Success case
result = divide(10, 2)
if result.is_success():
    print(f"Result: {result.value}")  # Result: 5.0
else:
    print(f"Error: {result.error}")

# Failure case  
result = divide(10, 0)
if result.is_failure():
    print(f"Error: {result.error}")  # Error: Division by zero
```

### Chaining Operations

Chain operations that can fail using `.then()` or the `>>` operator:

```python
from result_type import Success, Failure

def divide(a: float, b: float) -> Result[float, str]:
    if b == 0:
        return Failure("Division by zero")
    return Success(a / b)

def multiply_by_2(x: float) -> Result[float, str]:
    return Success(x * 2)

def subtract_1(x: float) -> Result[float, str]:
    if x < 1:
        return Failure("Result would be negative")
    return Success(x - 1)

# Method 1: Using .then() method
result = (
    divide(10, 2)
    .then(multiply_by_2)
    .then(subtract_1)
    .map(lambda x: x + 5)
)

# Method 2: Using >> operator (cleaner syntax)
result = divide(10, 2) >> multiply_by_2 >> subtract_1

# Method 3: Mixed approach
result = (
    divide(10, 2)
    >> multiply_by_2
    .map(lambda x: x + 10)  # Transform without failure
    >> subtract_1
)

if result.is_success():
    print(f"Final result: {result.value}")
else:
    print(f"Error occurred: {result.error}")
```

### Safe Function Calls

Automatically handle exceptions with `safe_call`:

```python
from result_type import safe_call

# Wrap risky function calls
result = safe_call(
    lambda: 10 / 0,
    "Math operation failed"
)

if result.is_failure():
    print(result.error)  # "Math operation failed: division by zero"

# Use as decorator
from result_type import safe_call_decorator

@safe_call_decorator("Database error")
def risky_database_operation():
    # Some operation that might throw
    return fetch_user_from_db()

result = risky_database_operation()
```

### Rust-like Aliases (Ok/Err)

For developers familiar with Rust's `Result<T, E>`, this library provides `Ok` and `Err` aliases for `Success` and `Failure`:

```python
from result_type import Ok, Err, ok, err

def divide_rust_style(a: float, b: float):
    if b == 0:
        return Err("Division by zero")
    return Ok(a / b)

# Usage is identical to Success/Failure
result = divide_rust_style(10, 2)
if result.is_success():
    print(f"Result: {result.value}")  # Result: 5.0

# Chain operations using Rust-style
def multiply_by_2(x):
    return Ok(x * 2)

def validate_positive(x):
    if x > 0:
        return Ok(x)
    return Err("Must be positive")

result = Ok(5) >> multiply_by_2 >> validate_positive
if result.is_success():
    print(f"Final: {result.value}")  # Final: 10

# Helper functions with Rust naming
success_result = ok(42)      # Same as Success(42)
error_result = err("oops")   # Same as Failure("oops")

# Mix and match - they're the same types!
mixed_result = Ok(10) >> (lambda x: Success(x * 2))  # Works perfectly
print(Ok(42) == Success(42))  # True
```

## 📚 Complete API Reference

### Core Types

#### `Result[T, E]`
Abstract base class representing either success or failure.

**Methods:**
- `is_success() -> bool` - Check if result is Success
- `is_failure() -> bool` - Check if result is Failure  
- `then(func: Callable[[T], Result[U, E]]) -> Result[U, E]` - Chain operations
- `map(func: Callable[[T], U]) -> Result[U, E]` - Transform success value
- `map_error(func: Callable[[E], F]) -> Result[T, F]` - Transform error value
- `unwrap() -> T` - Extract value or raise exception
- `unwrap_or(default: T) -> T` - Extract value or return default
- `unwrap_or_else(func: Callable[[E], T]) -> T` - Extract value or compute from error

#### `Success[T]`
Represents successful result containing a value.

```python
success_result = Success(42)
print(success_result.value)  # 42
print(success_result.is_success())  # True
```

#### `Failure[E]`  
Represents failed result containing an error.

```python
failure_result = Failure("Something went wrong")
print(failure_result.error)  # "Something went wrong"
print(failure_result.is_failure())  # True
```

### Rust-like Aliases

#### `Ok` and `Err`
Type aliases for `Success` and `Failure` respectively.

```python
from result_type import Ok, Err

# These are identical to Success/Failure
ok_result = Ok(42)          # Same as Success(42)
err_result = Err("error")   # Same as Failure("error")
```

#### `ok(value: T) -> Success[T]` and `err(error: E) -> Failure[E]`
Helper functions with Rust-style naming.

```python
from result_type import ok, err

result = ok(42)        # Same as success(42) or Success(42)
error = err("oops")    # Same as failure("oops") or Failure("oops")
```

### Helper Functions

#### `success(value: T) -> Success[T]`
Create a Success result.

```python
from result_type import success
result = success(42)  # Same as Success(42)
```

#### `failure(error: E) -> Failure[E]`
Create a Failure result.

```python
from result_type import failure
result = failure("error")  # Same as Failure("error")
```

#### `safe_call(func: Callable[[], T], error_msg: str = None) -> Result[T, str]`
Safely call a function that might raise exceptions.

```python
from result_type import safe_call

result = safe_call(lambda: risky_operation())
if result.is_failure():
    print(f"Operation failed: {result.error}")
```

#### `safe_call_decorator(error_msg: str = None)`
Decorator version of safe_call.

```python
from result_type import safe_call_decorator

@safe_call_decorator("API call failed")
def call_external_api():
    return requests.get("https://api.example.com").json()

result = call_external_api()  # Returns Result[dict, str]
```

## 🔄 Chaining Operations

### Error Propagation

When chaining operations, errors automatically propagate:

```python
result = (
    Success(10)
    >> (lambda x: Failure("Something went wrong"))  # This fails
    >> (lambda x: Success(x * 2))  # This won't execute
    >> (lambda x: Success(x + 1))  # Neither will this
)

print(result.error)  # "Something went wrong"
```

### Exception Handling in Chains

Exceptions in chained operations are automatically converted to Failure:

```python
def risky_operation(x: int) -> Result[int, str]:
    return Success(x / 0)  # This will raise ZeroDivisionError

result = Success(10) >> risky_operation

print(result.is_failure())  # True  
print(type(result.error))   # <class 'ZeroDivisionError'>
```

## 🔄 Async/Await Support

The library includes full async/await support for modern Python applications with the `AsyncResult` wrapper:

### Basic Async Usage

```python
import asyncio
from result_type import Success, Failure, Result
from result_type.async_result import AsyncResult, async_safe_call

async def fetch_user(user_id: int) -> Result[dict, str]:
    await asyncio.sleep(0.1)  # Simulate API call
    if user_id <= 0:
        return Failure("Invalid user ID")
    return Success({"id": user_id, "name": f"User {user_id}"})

# Use async operations
result = await fetch_user(123)
if result.is_success():
    print(f"Found user: {result.value}")
```

### Async Chaining

Chain async and sync operations seamlessly:

```python
async def fetch_user_posts(user: dict) -> Result[list, str]:
    await asyncio.sleep(0.1)
    return Success([f"Post {i}" for i in range(3)])

def format_summary(posts: list) -> Result[str, str]:
    return Success(f"User has {len(posts)} posts")

# Chain async and sync operations
pipeline = (AsyncResult(fetch_user(123))
           .then_async(fetch_user_posts)    # Async operation
           .then_sync(format_summary))      # Sync operation

result = await pipeline.resolve()
if result.is_success():
    print(result.value)  # "User has 3 posts"
```

### Async Safe Calls

Handle async exceptions safely:

```python
from result_type.async_result import async_safe_call, async_safe_call_decorator

# Function approach
async def risky_api_call():
    # Might raise an exception
    return await some_external_api()

result = await async_safe_call(risky_api_call, "API Error")

# Decorator approach
@async_safe_call_decorator("Database Error")
async def database_operation():
    return await db.fetch_data()

result = await database_operation()  # Returns Result[Any, str]
```

### Gathering Multiple Async Results

Process multiple async operations concurrently:

```python
from result_type.async_result import gather_results

async def fetch_data(source: str) -> Result[str, str]:
    await asyncio.sleep(0.1)
    return Success(f"Data from {source}")

# Gather results - stops at first failure
async_operations = [
    AsyncResult(fetch_data("source1")),
    AsyncResult(fetch_data("source2")),
    AsyncResult(fetch_data("source3")),
]

combined = await gather_results(*async_operations)
if combined.is_success():
    print(combined.value)  # ["Data from source1", "Data from source2", "Data from source3"]
```

### Converting Regular Awaitables

Convert any awaitable to an AsyncResult:

```python
from result_type.async_result import from_awaitable

async def regular_async_function():
    return {"data": "success"}

# Convert to AsyncResult with error handling
async_result = await from_awaitable(regular_async_function(), "Operation failed")
result = await async_result.resolve()
```

## 🆚 Comparison with Alternatives

### vs PyMonad Either

```python
# PyMonad Either (less intuitive)
from pymonad.either import Left, Right

result = Right(42)  # Success
result = Left("error")  # Failure

# This library (more readable)
from result_type import Success, Failure

result = Success(42)  # Clear success intent
result = Failure("error")  # Clear failure intent
```

### vs Exception Handling

```python
# Traditional exception handling
try:
    result = risky_operation()
    result = transform(result)
    result = another_transform(result)
except Exception as e:
    handle_error(e)

# With Result type
result = (
    safe_call(risky_operation)
    >> safe_transform
    >> safe_another_transform
)

if result.is_failure():
    handle_error(result.error)
```

## 🧪 Real-World Examples

### Database Operations

```python
from result_type import Result, Success, Failure

def fetch_user(user_id: str) -> Result[dict, str]:
    try:
        user = database.users.find_one({"_id": user_id})
        if not user:
            return Failure("User not found")
        return Success(user)
    except Exception as e:
        return Failure(f"Database error: {e}")

def validate_user(user: dict) -> Result[dict, str]:
    if not user.get("is_active"):
        return Failure("User is inactive")
    return Success(user)

def get_user_permissions(user: dict) -> Result[list, str]:
    permissions = user.get("permissions", [])
    if not permissions:
        return Failure("User has no permissions")
    return Success(permissions)

# Chain the operations
result = (
    fetch_user("user123")
    >> validate_user
    >> get_user_permissions
)

if result.is_success():
    print(f"User permissions: {result.value}")
else:
    print(f"Failed to get permissions: {result.error}")
```

### API Calls

```python
import requests
from result_type import safe_call, Result, Success, Failure

def fetch_weather(city: str) -> Result[dict, str]:
    return safe_call(
        lambda: requests.get(f"http://api.weather.com/{city}").json(),
        f"Failed to fetch weather for {city}"
    )

def extract_temperature(weather_data: dict) -> Result[float, str]:
    try:
        temp = weather_data["current"]["temperature"]
        return Success(float(temp))
    except (KeyError, ValueError, TypeError) as e:
        return Failure(f"Invalid weather data: {e}")

def celsius_to_fahrenheit(celsius: float) -> Result[float, str]:
    return Success(celsius * 9/5 + 32)

# Chain API call and transformations
result = (
    fetch_weather("London")
    >> extract_temperature
    >> celsius_to_fahrenheit
)

if result.is_success():
    print(f"Temperature in Fahrenheit: {result.value}")
else:
    print(f"Error: {result.error}")
```

### File Operations

```python
from pathlib import Path
from result_type import safe_call, Result

def read_config_file(path: str) -> Result[dict, str]:
    def _read_and_parse():
        content = Path(path).read_text()
        return json.loads(content)
    
    return safe_call(_read_and_parse, f"Failed to read config from {path}")

def validate_config(config: dict) -> Result[dict, str]:
    required_fields = ["api_key", "database_url", "port"]
    missing = [field for field in required_fields if field not in config]
    
    if missing:
        return Failure(f"Missing required fields: {missing}")
    return Success(config)

def start_application(config: dict) -> Result[str, str]:
    # Application startup logic here
    return Success(f"Application started on port {config['port']}")

# Chain configuration loading and validation
result = (
    read_config_file("config.json")
    >> validate_config
    >> start_application
)

if result.is_success():
    print(result.value)  # "Application started on port 8080"
else:
    print(f"Startup failed: {result.error}")
```

## 🧪 Testing

```bash
# Install development dependencies
pip install python-result-type[dev]

# Run tests
pytest

# Run tests with coverage
pytest --cov=result_type --cov-report=html

# Run type checking
mypy result_type

# Format code
black result_type tests
```

## 📄 Type Safety

This library is fully typed and compatible with mypy:

```python
from result_type import Result

def typed_operation(x: int) -> Result[str, str]:
    if x < 0:
        return Failure("Negative numbers not allowed")
    return Success(str(x))

# mypy will catch type errors
result: Result[str, str] = typed_operation(42)
```

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality  
4. Ensure all tests pass
5. Submit a pull request

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by [Rust's Result type](https://doc.rust-lang.org/std/result/)
- Similar concepts from [PyMonad](https://pypi.org/project/PyMonad/)
- Functional programming patterns from Haskell's Either type

## 📈 Changelog

### 1.2.1

- **Fixed**: Mypy warning `"Result[T, E]" has no attribute "error"` when accessing `result.error`
- **Fixed**: Mypy warning `"Result[T, E]" has no attribute "value"` when accessing `result.value`
- **Enhanced**: Added `value` and `error` properties to the abstract `Result` class for better type checking
- **Improved**: Better mypy compatibility and type safety throughout the codebase
- **Maintained**: Full backward compatibility - no breaking changes to existing code

### 1.2.0

- **New**: Rust-like aliases `Ok` and `Err` for `Success` and `Failure`
- **New**: Helper functions `ok()` and `err()` with Rust-style naming
- **Enhanced**: Full compatibility between Rust aliases and original naming
- **Improved**: Better developer experience for Rust developers
- **Added**: Comprehensive tests and examples for Rust-style usage

### 1.1.0

- **New**: Full async/await support with `AsyncResult` wrapper
- **New**: `async_safe_call` and `async_safe_call_decorator` for async exception handling
- **New**: Async chaining operations with `.then_async()` and `.then_sync()`
- **New**: `gather_results()` for concurrent async operations
- **New**: `from_awaitable()` to convert regular awaitables to AsyncResult
- **Improved**: Enhanced type annotations for better IDE support
- **Enhanced**: Better error messages and stack traces

### 1.0.0

- Initial release
- Core Result, Success, and Failure types
- Chaining with `.then()` and `>>` operator
- Helper functions and decorators
- Comprehensive test suite
- Full type annotations
