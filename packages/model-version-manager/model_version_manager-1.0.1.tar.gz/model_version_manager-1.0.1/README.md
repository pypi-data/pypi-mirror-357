# Version Class (Python Implementation)

A Python implementation of version number management inspired by .NET's `Version` class, providing robust version number handling and comparison capabilities.

## Features

- Multiple constructors for flexible version creation
- String parsing and validation
- Component-based comparison operations
- Strict type and value checking
- Comprehensive error handling

## Installation

```bash
pip install model_version_manager
```

# Basic Usage

```python
from model_version_manager import Version

# Different ways to create versions
v1 = Version()           # 0.0
v2 = Version(1, 2)       # 1.2
v3 = Version(1, 2, 3)    # 1.2.3
v4 = Version("1.2.3.4")  # From string

# Access components
print(f"{v4.major}.{v4.minor}.{v4.build}.{v4.revision}")

# Comparison
print(v2 == Version(1, 2))  # True
print(v3 < Version(1, 3))   # True
print(v1 > v2)              # False
```

# API Reference

```python
Version()   # 0.0
Version(major: int, minor: int) 
Version(major: int, minor: int, build: int) 
Version(major: int, minor: int, build: int, revision: int)
Version(version_string: str)  # Parses "major.minor.build.revision"
```

# Properies

- `major`: int - Major version number

- `minor`: int - Minor version number

- `build`: int - Build number (-1 if not specified)

- `revision`: int - Revision number (-1 if not specified)

# Methods

- `__str__()`: Returns string representation (e.g. "1.2.3.4")

- `__eq__()`, `__lt__()`, etc.: Comparison operators

- `parse(version_string)`: Classmethod to parse version strings

# Comparison Rules

Versions are compared component by component in order:

1. Major

2. Minor

3. Build

4. Revision

Missing components (represented by -1) are considered older than any specified component.

# Examples

See complete examples in the examples/ directory:

- `basic_usage.py` - Basic functionality