# data_handler.py - Data Management Module

## Overview
The `data_handler.py` module provides robust JSON file handling, validation, and data management utilities for the Trip Recommendation application.

## Functions

### Core Functions

#### `load_json_file(filename: str) -> Union[Dict, List, None]`
Loads data from a JSON file with error handling.

**Parameters:**
- `filename` (str): Path to the JSON file to load

**Returns:**
- Dict or List: Parsed JSON data
- None: If file doesn't exist, is empty, or contains invalid JSON

**Raises:**
- IOError: If file cannot be read (permission issues)
- json.JSONDecodeError: If JSON is malformed

**Example:**
```python
data = load_json_file('data/users.json')
if data:
    print(f"Loaded {len(data)} users")
else:
    print("Failed to load users or file is empty")
```

---

#### `save_json_file(filename: str, data: Union[Dict, List]) -> bool`
Saves data to a JSON file with automatic directory creation.

**Parameters:**
- `filename` (str): Path to the JSON file to save to
- `data` (Dict or List): Data to save (must be JSON serializable)

**Returns:**
- True: If save successful
- False: If save failed

**Raises:**
- IOError: If file cannot be written (permission issues)
- TypeError: If data is not JSON serializable

**Example:**
```python
users = {'john1234': {'password': 'hash123', 'trips': []}}
if save_json_file('data/users.json', users):
    print("Users saved successfully")
else:
    print("Failed to save users")
```

---

#### `validate_data_structure(data: Any, data_type: str = 'unknown') -> bool`
Validates that data has the correct structure for the specified type.

**Parameters:**
- `data` (Any): Data to validate
- `data_type` (str): Type of data to validate. Options:
  - 'users': User account data
  - 'trips': Trip data
  - 'forum': Forum posts
  - 'city': City data
  - 'unknown': Generic dict/list validation

**Returns:**
- True: If data structure is valid
- False: If data structure is invalid

**Supported Structures:**

##### Users Structure
```python
{
    'username1234': {
        'password': 'hashed_password_or_hash_string',
        'trips': [...]
    },
    ...
}
```

##### Forum Structure
```python
[
    {
        'id': 1,
        'username': 'user1234',
        'title': 'Post Title',
        'content': 'Post content',
        'city': 'Paris',
        'created_at': '2024-01-01 10:00:00',
        'replies': [
            {
                'username': 'user5678',
                'content': 'Reply content',
                'created_at': '2024-01-01 11:00:00'
            }
        ]
    },
    ...
]
```

##### City Structure
```python
{
    'Paris': {
        'name': 'Paris',
        'places': [
            {
                'name': 'Eiffel Tower',
                'category': 'Sightseeing',
                'cost': 10,
                'duration': '2 hours',
                'description': 'Iconic landmark'
            }
        ],
        'categories': ['Sightseeing', 'Food', 'Shopping']
    },
    ...
}
```

**Example:**
```python
users = load_json_file('data/users.json')
if validate_data_structure(users, 'users'):
    print("Users data is valid")
else:
    print("Users data structure is invalid")
```

---

### Utility Functions

#### `load_json_file_safe(filename: str, data_type: str = 'unknown', default: Any = None) -> Any`
Loads and validates JSON file with fallback to default value.

**Parameters:**
- `filename` (str): Path to JSON file
- `data_type` (str): Type of data for validation
- `default` (Any): Default value if load/validation fails

**Returns:**
- Loaded data if valid
- default value if load or validation fails

**Example:**
```python
users = load_json_file_safe('data/users.json', 'users', default={})
# Returns loaded users or empty dict if file doesn't exist or is invalid
```

---

#### `merge_json_data(existing_data: Dict, new_data: Dict, overwrite: bool = False) -> Dict`
Merges new JSON data with existing data (deep merge for nested dicts).

**Parameters:**
- `existing_data` (Dict): Existing data to merge into
- `new_data` (Dict): New data to merge
- `overwrite` (bool): If True, new data overwrites existing; if False, keeps existing values

**Returns:**
- Dict: Merged data

**Example:**
```python
# Without overwrite (keeps existing values)
existing = {'user': {'name': 'John', 'age': 30}}
new = {'user': {'email': 'john@example.com'}}
result = merge_json_data(existing, new, overwrite=False)
# Result: {'user': {'name': 'John', 'age': 30, 'email': 'john@example.com'}}

# With overwrite (replaces existing values)
result = merge_json_data(existing, new, overwrite=True)
```

---

## Usage Examples

### Example 1: Load and Validate User Data
```python
from data_handler import load_json_file, validate_data_structure

# Load users from file
users = load_json_file('data/users.json')

# Validate structure
if validate_data_structure(users, 'users'):
    print(f"Loaded {len(users)} valid users")
    for username in users:
        print(f"  - {username}")
else:
    print("Invalid user data structure")
```

### Example 2: Save and Backup Data
```python
from data_handler import load_json_file, save_json_file

# Load existing data
forum_posts = load_json_file('data/forum.json')

# Add new post
new_post = {
    'id': len(forum_posts) + 1,
    'username': 'user1234',
    'title': 'New Discussion',
    'content': 'Let us discuss this topic',
    'city': 'Paris',
    'created_at': '2024-01-01 12:00:00',
    'replies': []
}
forum_posts.append(new_post)

# Save updated data
if save_json_file('data/forum.json', forum_posts):
    print("Forum updated successfully")
    # Optionally save backup
    save_json_file('data/forum_backup.json', forum_posts)
```

### Example 3: Safe Loading with Fallback
```python
from data_handler import load_json_file_safe

# Load city data with fallback to empty dict
cities = load_json_file_safe(
    'data/city_data.json',
    data_type='city',
    default={}
)

print(f"Loaded {len(cities)} cities")
# If file doesn't exist or is invalid, cities will be {}
```

### Example 4: Merge User Trips
```python
from data_handler import load_json_file, save_json_file, merge_json_data

# Load existing user
users = load_json_file('data/users.json')
user_data = users.get('john1234', {})

# Create new user data with additional trips
new_user_data = {
    'trips': [
        {
            'trip_name': 'Summer 2024',
            'days': {...}
        }
    ]
}

# Merge (keeps existing password, adds new trips)
merged = merge_json_data(user_data, new_user_data, overwrite=False)
users['john1234'] = merged

# Save updated users
save_json_file('data/users.json', users)
```

---

## Error Handling

All functions include comprehensive error handling and logging:

- **Missing files**: Returns None or default value
- **Invalid JSON**: Logs error and returns None
- **Permission errors**: Raises IOError with descriptive message
- **Validation errors**: Logs specific validation failures

Enable logging to see detailed error messages:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## Testing

Run the comprehensive test suite:
```bash
python3 test_data_handler.py
```

Tests include:
- ✓ Loading valid/invalid JSON files
- ✓ Saving data with directory creation
- ✓ Data structure validation for all types
- ✓ Error handling and edge cases
- ✓ Safe loading with fallbacks
- ✓ Data merging functionality
- ✓ Integration workflows

---

## Performance Notes

- Files are read entirely into memory
- Suitable for moderately sized JSON files (< 10MB)
- For very large files (> 100MB), consider streaming approaches
- Logging overhead is minimal in production

---

## Future Enhancements

- [ ] Add CSV export/import functionality
- [ ] Implement file locking for concurrent access
- [ ] Add data encryption for sensitive fields
- [ ] Support for database backends (SQLite, MongoDB)
- [ ] Automatic data backups and versioning
