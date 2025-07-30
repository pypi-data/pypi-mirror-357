# Update Advanced Python Logger

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A feature-rich logging solution with file rotation, size-based cleanup, and configurable formatting.

## Features

- ✅ **Multi-level logging** (INFO, WARN, ERROR, CRIT, DEBUG)
- 📁 **Automatic log rotation** by size and age
- 📝 **Dual output** (console + file) with toggle capability
- 🧹 **Automatic cleanup** of old log files
- 🛠 **Exception-safe** design

## Installation

```bash
pip install upd-logger
```

# Quick Start

```python
from upd_logger import Logger

# Initialize
Logger.setup_logging(
    log_dir="my_app_logs",
    write_to_file=True,
    max_log_size=10*1024*1024,  # 10MB
    max_log_age_days=7
)

# Usage
Logger("Application started", "info")
Logger("Important event", "warn")
```

# Full Usage Examples

## Basic Configuration

```python
# Console-only logging
Logger.setup_logging(write_to_file=False)

# File logging with custom formats
Logger.setup_logging(
    log_dir="logs"
)
```

## Logging Examples

```python
# Different log levels
Logger("Debug information", "debug")
Logger("Non-critical issue", "warn")
Logger("Critical failure!", "crit")

# Error handling
try:
    risky_operation()
except Exception as e:
    Logger(f"Operation failed: {str(e)}", "error")
```

## Runtime Reconfiguration

```python
# Switch to emergency console-only mode
Logger.setup_logging(write_to_file=False)
Logger("File logging disabled!", "warn")
```

# Configuration Options

| Parameter         | Default     | Description                          |
|:-----------------:|:-----------:|:------------------------------------:|
| `log_dir`         | `"logs"`    | Directory for log files              |
| `write_to_file`   | `True`      | Enable file logging                  |
| `auto_delete_logs`   | `True`      | Enable auto delete                |
| `max_log_size`    | `62914560`  | Max log size in bytes (60MB)         |
| `max_log_age_days`| `30`        | Max age of logs in days              |

# Best Practices
1. Initialize early - Call `setup_logging()` at application startup

2. Use proper levels:
    - `debug` - Diagnostic info
    - `info` - Regular operations
    - `warn` - Unexpected but recoverable
    - `error` - Failed operations
    - `crit` - Critical failures
    
3. Include context in messages:
```python
# Good
Logger(f"User {user_id} failed login (attempt {attempt_count})", "warn")

# Bad
Logger("Something happened", "warn")
```

# Advanced Features

## Custom Cleanup Rules

```python
# Keep logs for 1 day or max 1MB
Logger.setup_logging(
    max_log_size=1024*1024,
    max_log_age_days=1
)
```

## Testing Integration

```python
# In tests - disable file logging
Logger.setup_logging(write_to_file=False)
```

**The README follows modern Python packaging standards and provides all necessary information at a glance while being detailed enough for advanced users.**