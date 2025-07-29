# SaveKit

**SaveKit** is a lightweight and easy-to-use key-value storage toolkit using JSON files for persistence. 
It's ideal for storing configurations, user preferences, flags, or simple state data in any Python project.

## Features

- ✅ Simple JSON-based key-value storage
- 🐍 Pure Python, no dependencies
- 💾 Persistent across executions
- 🔄 Lazy loading (loads only when accessed)
- 🧪 Ready for testing and packaging

## Installation

```bash
pip install savekit
```

## Usage

```python
from savekit import SaveKit

db = SaveKit()

# Store a value
db.put("theme", "dark")

# Retrieve a value
print(db.get("theme"))  # Output: dark

# Remove a value
db.remove("theme")

# Get all stored data
print(db.get_all())

# Reset everything
db.reset()
```

## License

This project is licensed under the MIT License.
