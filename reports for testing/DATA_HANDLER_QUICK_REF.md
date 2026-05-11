# data_handler.py - Quick Reference

## 🎯 What Was Implemented

✅ **load_json_file()** - Load JSON files safely  
✅ **save_json_file()** - Save data to JSON files  
✅ **validate_data_structure()** - Validate data format  
✅ **load_json_file_safe()** - Load with fallback  
✅ **merge_json_data()** - Deep merge dictionaries  

## 📊 Test Results

```
34 tests → ALL PASSED ✅
0 failures
0 errors
```

## 🚀 Quick Start

```python
from data_handler import load_json_file, save_json_file, validate_data_structure

# Load data
data = load_json_file('data/users.json')

# Validate structure
if validate_data_structure(data, 'users'):
    print("Valid data!")

# Save data
save_json_file('data/users.json', data)
```

## 📋 Validation Types

| Type | Purpose | Returns dict/list? |
|------|---------|-------------------|
| users | User accounts | dict |
| forum | Forum posts | list |
| city | City data | dict |
| trips | Trip info | list |
| unknown | Generic check | dict or list |

## ⚡ Common Patterns

### Safe Load with Fallback
```python
users = load_json_file_safe('users.json', 'users', default={})
```

### Save with Backup
```python
data = load_json_file('file.json')
# ... modify data ...
save_json_file('file.json', data)
save_json_file('file_backup.json', data)
```

### Merge Data
```python
existing = {'user': {'name': 'John'}}
new = {'user': {'age': 30}}
merged = merge_json_data(existing, new)
```

## 🔍 Validation Examples

### Valid Users Structure ✅
```python
{
    'john1234': {
        'password': 'hash_value',
        'trips': []
    }
}
```

### Valid Forum Structure ✅
```python
[
    {
        'id': 1,
        'username': 'john1234',
        'title': 'Title',
        'content': 'Content',
        'city': 'Paris',
        'created_at': '2024-01-01',
        'replies': []
    }
]
```

## 📁 Files Created

| File | Purpose |
|------|---------|
| data_handler.py | Main implementation (330 lines) |
| test_data_handler.py | 34 tests (500+ lines) |
| DATA_HANDLER_DOCS.md | Complete documentation |
| DATA_HANDLER_IMPLEMENTATION.md | Implementation summary |

## ✨ Features

- ✅ Automatic error handling
- ✅ Logging for debugging
- ✅ Type hints throughout
- ✅ Directory auto-creation
- ✅ Unicode support
- ✅ Defensive programming
- ✅ Production-ready

## 🧪 Run Tests

```bash
python3 test_data_handler.py
```

Expected output:
```
Ran 34 tests in 0.004s
OK
```

## 🔗 Integration with app.py

```python
# Replace this:
def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.loads(f.read().strip())
    return {}

# With this:
def load_users():
    from data_handler import load_json_file_safe
    return load_json_file_safe(USERS_FILE, 'users', default={})
```

## 📌 Next Steps

1. Use data_handler functions in app.py
2. Implement recommender.py
3. Implement visualizer.py
4. Fix security issues (CSRF, input sanitization)

## ❓ FAQ

**Q: What if file doesn't exist?**  
A: Returns None (or default if using load_json_file_safe)

**Q: What if JSON is invalid?**  
A: Logs error, returns None (or default value)

**Q: Can I use with large files?**  
A: Yes, up to ~10MB. Larger files need streaming.

**Q: Is it thread-safe?**  
A: No. For concurrent access, use file locking.

---

**Status**: ✅ Ready for production  
**Tests**: 34/34 passing  
**Documentation**: Complete
