# Awesome Environment Manager

A Python utility for automatically managing environment variables with type safety and easy configuration.

## Description

Environment Manager provides a simple yet powerful way to handle environment variables in Python applications through type-hinted class attributes. It automatically loads environment variables and converts them to the correct types based on your type hints.

## Features

- 🔒 Type-safe environment variable handling
- 🔄 Automatic type conversion
- 📝 Support for `.env` files (via python-dotenv)
- 🎯 Support for various data types:
  - Basic types (str, int, float, etc.)
  - Boolean values with flexible input formats
  - Lists with type hints (using semicolon as separator)
  - Dictionaries (key-value pairs)

## Installation

```bash
bash pip install awesome-environment-manager
```

### or using uv

```bash
uv pip install awesome-environment-manager
```

## Quick Start

```python
from aem import EnvironmentClass

class AppConfig(EnvironmentClass):
  DATABASE_URL: str = "postgresql://localhost"
  PORT: int = 8080
  DEBUG: bool = False
  ALLOWED_HOSTS: list[str] = ["localhost", "127.0.0.1", "example.com"]
  DB_CONFIG: dict = {"host": "localhost", "port": "5432", "name": "mydb"}
```

# Create an instance - environment variables will be loaded automatically

```python
os.environ["PORT"] = 8282

config = AppConfig()
print(config.DATABASE_URL) # => postgresql://localhost
print(config.PORT) # => 8282
```

## Environment Variable Formats

- **Strings**: Simple string values
  ```
  DATABASE_URL=postgresql://localhost:5432/db
  ```

- **Numbers**: Will be converted to int/float
  ```
  PORT=8080
  ```

- **Booleans**: Supports various formats
  ```
  DEBUG=true  # Also accepts: 1, yes, y, on
  ```

- **Lists**: Use semicolons as separators
  ```
  ALLOWED_HOSTS=localhost;127.0.0.1;example.com
  ```

- **Dictionaries**: Use semicolons between pairs and colons between keys and values
  ```
  DB_CONFIG=host:localhost;port:5432;name:mydb
  ```

## .env Support

The package automatically supports `.env` files if `python-dotenv` is installed:

```bash
pip install python-dotenv
```

Then create a `.env` file:

```
DATABASE_URL=postgresql://11.22.33.44
DEBUG=1
```

Result

```python
config = AppConfig()
print(config.DATABASE_URL) # => postgresql://11.22.33.44
print(config.PORT) # => 8080
print(config.DEBUG) # => True
```

## License

This project is licensed under the European Union Public License v1.2 (EUPL-1.2).

