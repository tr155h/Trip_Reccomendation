"""
Test suite for data_handler.py module
"""

import unittest
import json
import os
import tempfile
import shutil
from data_handler import (
    load_json_file, 
    save_json_file, 
    validate_data_structure,
    load_json_file_safe,
    merge_json_data
)


class TestLoadJsonFile(unittest.TestCase):
    """Test load_json_file function"""
    
    def setUp(self):
        """Create temporary directory for test files"""
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up temporary directory"""
        shutil.rmtree(self.test_dir)
    
    def test_load_valid_json_dict(self):
        """Test loading valid JSON dictionary"""
        test_file = os.path.join(self.test_dir, 'test.json')
        test_data = {'key': 'value', 'number': 42}
        
        with open(test_file, 'w') as f:
            json.dump(test_data, f)
        
        result = load_json_file(test_file)
        self.assertEqual(result, test_data)
    
    def test_load_valid_json_list(self):
        """Test loading valid JSON list"""
        test_file = os.path.join(self.test_dir, 'test.json')
        test_data = [1, 2, 3, 'item']
        
        with open(test_file, 'w') as f:
            json.dump(test_data, f)
        
        result = load_json_file(test_file)
        self.assertEqual(result, test_data)
    
    def test_load_nonexistent_file(self):
        """Test loading non-existent file returns None"""
        result = load_json_file('/nonexistent/path/file.json')
        self.assertIsNone(result)
    
    def test_load_empty_file(self):
        """Test loading empty file"""
        test_file = os.path.join(self.test_dir, 'empty.json')
        open(test_file, 'w').close()  # Create empty file
        
        result = load_json_file(test_file)
        # Empty file should return {} or []
        self.assertIn(result, ({}, []))
    
    def test_load_malformed_json(self):
        """Test loading malformed JSON returns None"""
        test_file = os.path.join(self.test_dir, 'bad.json')
        with open(test_file, 'w') as f:
            f.write('{invalid json}')
        
        result = load_json_file(test_file)
        self.assertIsNone(result)
    
    def test_load_empty_filename(self):
        """Test loading with empty filename"""
        result = load_json_file('')
        self.assertIsNone(result)
    
    def test_load_none_filename(self):
        """Test loading with None filename"""
        result = load_json_file(None)
        self.assertIsNone(result)


class TestSaveJsonFile(unittest.TestCase):
    """Test save_json_file function"""
    
    def setUp(self):
        """Create temporary directory for test files"""
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up temporary directory"""
        shutil.rmtree(self.test_dir)
    
    def test_save_dict_data(self):
        """Test saving dictionary data"""
        test_file = os.path.join(self.test_dir, 'test.json')
        test_data = {'key': 'value', 'nested': {'inner': 'data'}}
        
        result = save_json_file(test_file, test_data)
        self.assertTrue(result)
        
        # Verify file was created and contains correct data
        with open(test_file, 'r') as f:
            saved_data = json.load(f)
        
        self.assertEqual(saved_data, test_data)
    
    def test_save_list_data(self):
        """Test saving list data"""
        test_file = os.path.join(self.test_dir, 'test.json')
        test_data = [1, 2, {'nested': 'item'}]
        
        result = save_json_file(test_file, test_data)
        self.assertTrue(result)
        
        with open(test_file, 'r') as f:
            saved_data = json.load(f)
        
        self.assertEqual(saved_data, test_data)
    
    def test_save_creates_directory(self):
        """Test that save creates parent directory if needed"""
        test_file = os.path.join(self.test_dir, 'subdir', 'file.json')
        test_data = {'test': 'data'}
        
        result = save_json_file(test_file, test_data)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(test_file))
    
    def test_save_none_data(self):
        """Test saving None data returns False"""
        test_file = os.path.join(self.test_dir, 'test.json')
        result = save_json_file(test_file, None)
        self.assertFalse(result)
    
    def test_save_empty_filename(self):
        """Test saving with empty filename"""
        result = save_json_file('', {'data': 'value'})
        self.assertFalse(result)
    
    def test_save_overwrites_existing(self):
        """Test that save overwrites existing file"""
        test_file = os.path.join(self.test_dir, 'test.json')
        
        # Save first data
        save_json_file(test_file, {'first': 'data'})
        
        # Save new data
        new_data = {'second': 'data'}
        save_json_file(test_file, new_data)
        
        # Verify new data is in file
        with open(test_file, 'r') as f:
            saved_data = json.load(f)
        
        self.assertEqual(saved_data, new_data)


class TestValidateDataStructure(unittest.TestCase):
    """Test validate_data_structure function"""
    
    def test_validate_users_structure_valid(self):
        """Test valid users structure"""
        data = {
            'user1234': {'password': 'hash123', 'trips': []},
            'user5678': {'password': 'hash456', 'trips': [{'trip_name': 'Paris'}]}
        }
        result = validate_data_structure(data, 'users')
        self.assertTrue(result)
    
    def test_validate_users_structure_invalid_not_dict(self):
        """Test invalid users structure (not dict)"""
        result = validate_data_structure([], 'users')
        self.assertFalse(result)
    
    def test_validate_users_structure_missing_password(self):
        """Test users structure missing password field"""
        data = {
            'user1234': {'trips': []}  # Missing password
        }
        result = validate_data_structure(data, 'users')
        self.assertFalse(result)
    
    def test_validate_forum_structure_valid(self):
        """Test valid forum structure"""
        data = [
            {
                'id': 1,
                'username': 'user1234',
                'title': 'Title',
                'content': 'Content',
                'city': 'Paris',
                'created_at': '2024-01-01',
                'replies': []
            }
        ]
        result = validate_data_structure(data, 'forum')
        self.assertTrue(result)
    
    def test_validate_forum_structure_invalid_not_list(self):
        """Test invalid forum structure (not list)"""
        result = validate_data_structure({}, 'forum')
        self.assertFalse(result)
    
    def test_validate_forum_structure_missing_field(self):
        """Test forum structure missing required field"""
        data = [
            {
                'id': 1,
                'username': 'user1234',
                'title': 'Title',
                # Missing 'content'
                'created_at': '2024-01-01',
                'replies': []
            }
        ]
        result = validate_data_structure(data, 'forum')
        self.assertFalse(result)
    
    def test_validate_city_structure_valid(self):
        """Test valid city structure"""
        data = {
            'Paris': {
                'name': 'Paris',
                'places': [
                    {'name': 'Eiffel Tower', 'category': 'Sightseeing', 'cost': 10}
                ],
                'categories': ['Sightseeing', 'Food']
            }
        }
        result = validate_data_structure(data, 'city')
        self.assertTrue(result)
    
    def test_validate_city_structure_missing_places(self):
        """Test city structure missing places field"""
        data = {
            'Paris': {
                'name': 'Paris',
                'categories': ['Sightseeing']
                # Missing 'places'
            }
        }
        result = validate_data_structure(data, 'city')
        self.assertFalse(result)
    
    def test_validate_none_data(self):
        """Test validating None data"""
        result = validate_data_structure(None, 'users')
        self.assertFalse(result)
    
    def test_validate_unknown_type(self):
        """Test validation with unknown type"""
        result = validate_data_structure({'key': 'value'}, 'unknown')
        self.assertTrue(result)  # Should return True for dict


class TestLoadJsonFileSafe(unittest.TestCase):
    """Test load_json_file_safe function"""
    
    def setUp(self):
        """Create temporary directory for test files"""
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up temporary directory"""
        shutil.rmtree(self.test_dir)
    
    def test_load_safe_valid_users_file(self):
        """Test loading valid users file with safe function"""
        test_file = os.path.join(self.test_dir, 'users.json')
        test_data = {
            'user1234': {'password': 'hash', 'trips': []}
        }
        save_json_file(test_file, test_data)
        
        result = load_json_file_safe(test_file, 'users')
        self.assertEqual(result, test_data)
    
    def test_load_safe_invalid_structure_returns_default(self):
        """Test that invalid structure returns default"""
        test_file = os.path.join(self.test_dir, 'bad.json')
        test_data = []  # Invalid for users type
        save_json_file(test_file, test_data)
        
        default_value = {'fallback': 'user'}
        result = load_json_file_safe(test_file, 'users', default_value)
        self.assertEqual(result, default_value)
    
    def test_load_safe_nonexistent_returns_default(self):
        """Test that nonexistent file returns default"""
        default_value = {'default': 'data'}
        result = load_json_file_safe('/nonexistent/file.json', default=default_value)
        self.assertEqual(result, default_value)
    
    def test_load_safe_no_default_returns_none(self):
        """Test that without default, returns None"""
        result = load_json_file_safe('/nonexistent/file.json')
        self.assertIsNone(result)


class TestMergeJsonData(unittest.TestCase):
    """Test merge_json_data function"""
    
    def test_merge_simple_dict(self):
        """Test merging simple dictionaries"""
        existing = {'a': 1, 'b': 2}
        new = {'c': 3}
        
        result = merge_json_data(existing, new)
        self.assertEqual(result, {'a': 1, 'b': 2, 'c': 3})
    
    def test_merge_nested_dict(self):
        """Test merging nested dictionaries"""
        existing = {'user': {'name': 'John', 'age': 30}}
        new = {'user': {'email': 'john@example.com'}}
        
        result = merge_json_data(existing, new, overwrite=False)
        expected = {'user': {'name': 'John', 'age': 30, 'email': 'john@example.com'}}
        self.assertEqual(result, expected)
    
    def test_merge_overwrite_true(self):
        """Test merge with overwrite=True"""
        existing = {'key': 'old_value'}
        new = {'key': 'new_value'}
        
        result = merge_json_data(existing, new, overwrite=True)
        self.assertEqual(result['key'], 'new_value')
    
    def test_merge_overwrite_false(self):
        """Test merge with overwrite=False keeps existing"""
        existing = {'key': 'old_value'}
        new = {'key': 'new_value'}
        
        result = merge_json_data(existing, new, overwrite=False)
        self.assertEqual(result['key'], 'old_value')
    
    def test_merge_invalid_input_not_dict(self):
        """Test merge with non-dict input returns original"""
        result = merge_json_data([], {})
        self.assertEqual(result, [])


class TestIntegration(unittest.TestCase):
    """Integration tests"""
    
    def setUp(self):
        """Create temporary directory for test files"""
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up temporary directory"""
        shutil.rmtree(self.test_dir)
    
    def test_full_workflow_users(self):
        """Test complete workflow: create, save, load, validate"""
        test_file = os.path.join(self.test_dir, 'users.json')
        
        # Create user data
        user_data = {
            'alice1234': {'password': 'hash_password', 'trips': []},
            'bob5678': {'password': 'hash_pass', 'trips': []}
        }
        
        # Save
        save_result = save_json_file(test_file, user_data)
        self.assertTrue(save_result)
        
        # Load
        loaded_data = load_json_file(test_file)
        self.assertEqual(loaded_data, user_data)
        
        # Validate
        validate_result = validate_data_structure(loaded_data, 'users')
        self.assertTrue(validate_result)
    
    def test_full_workflow_forum(self):
        """Test complete workflow for forum posts"""
        test_file = os.path.join(self.test_dir, 'forum.json')
        
        forum_data = [
            {
                'id': 1,
                'username': 'user1234',
                'title': 'Paris Tips',
                'content': 'Great place to visit',
                'city': 'Paris',
                'created_at': '2024-01-01 10:00:00',
                'replies': [
                    {'username': 'user5678', 'content': 'Agreed!', 'created_at': '2024-01-01 11:00:00'}
                ]
            }
        ]
        
        save_result = save_json_file(test_file, forum_data)
        self.assertTrue(save_result)
        
        loaded_data = load_json_file(test_file)
        self.assertEqual(loaded_data, forum_data)
        
        validate_result = validate_data_structure(loaded_data, 'forum')
        self.assertTrue(validate_result)


if __name__ == '__main__':
    unittest.main(verbosity=2)
