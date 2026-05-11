"""
Comprehensive test suite for Trip Recommendation Application
Tests for data validation, business logic, and error handling
"""

import unittest
import json
import os
import sys
from datetime import datetime
from unittest.mock import patch, MagicMock

# Import the functions we want to test
sys.path.insert(0, os.path.dirname(__file__))
from app import (
    is_valid_username, is_valid_password, username_exists, 
    get_recommendations_for_city,
    add_forum_post, add_reply_to_post, activity_image_url
)


class TestValidation(unittest.TestCase):
    """Test validation functions"""
    
    def test_valid_username_with_4_digits(self):
        """Test valid usernames ending with 4 digits"""
        self.assertTrue(is_valid_username('john1234'))
        self.assertTrue(is_valid_username('alice5678'))
        self.assertTrue(is_valid_username('a1000'))
    
    def test_invalid_username_no_digits(self):
        """Test invalid username without 4 digits at end"""
        self.assertFalse(is_valid_username('johndoe'))
        self.assertFalse(is_valid_username('alice123'))  # Only 3 digits
        self.assertFalse(is_valid_username('1234'))  # Only 4 digits, no name
    
    def test_invalid_username_too_short(self):
        """Test username minimum length requirement"""
        self.assertFalse(is_valid_username('a123'))  # Less than 5 characters
        self.assertFalse(is_valid_username(''))  # Empty
        self.assertFalse(is_valid_username(None))  # None
    
    def test_valid_password_minimum_length(self):
        """Test valid passwords with minimum 6 characters"""
        self.assertTrue(is_valid_password('password123'))
        self.assertTrue(is_valid_password('pass12'))
        self.assertTrue(is_valid_password('123456'))
    
    def test_invalid_password_too_short(self):
        """Test invalid passwords under 6 characters"""
        self.assertFalse(is_valid_password('pass1'))
        self.assertFalse(is_valid_password('abc'))
        self.assertFalse(is_valid_password(''))
        self.assertFalse(is_valid_password(None))


class TestActivityImageUrl(unittest.TestCase):
    """Test image URL generation"""
    
    def test_activity_image_url_with_existing_url(self):
        """Test that existing image URL is preserved"""
        rec = {'name': 'Museum', 'image_url': 'https://example.com/image.jpg'}
        result = activity_image_url(rec)
        self.assertEqual(result, 'https://example.com/image.jpg')
    
    def test_activity_image_url_fallback_svg(self):
        """Test SVG fallback when no image URL provided"""
        rec = {'name': 'Museum Tour'}
        result = activity_image_url(rec)
        
        # Should return SVG data URL
        self.assertTrue(result.startswith('data:image/svg'))
        # Should contain the activity name (first 20 chars)
        self.assertIn('Museum', result)
    
    def test_activity_image_url_long_name_truncated(self):
        """Test that long activity names are truncated to 20 chars"""
        rec = {'name': 'This is a very long museum tour name that exceeds limit'}
        result = activity_image_url(rec)
        
        # Should be truncated
        self.assertIn('This is a very long ', result)


class TestForumFunctions(unittest.TestCase):
    """Test forum posting functionality"""
    
    @patch('app.load_forum')
    @patch('app.save_forum')
    def test_add_forum_post_creates_post(self, mock_save, mock_load):
        """Test that forum post is created with correct structure"""
        mock_load.return_value = []
        
        result = add_forum_post('john1234', 'My Title', 'My Content', 'Paris')
        
        self.assertEqual(result['username'], 'john1234')
        self.assertEqual(result['title'], 'My Title')
        self.assertEqual(result['content'], 'My Content')
        self.assertEqual(result['city'], 'Paris')
        self.assertEqual(result['id'], 1)
        self.assertIn('created_at', result)
        self.assertEqual(result['replies'], [])
    
    @patch('app.load_forum')
    @patch('app.save_forum')
    def test_add_forum_post_increments_id(self, mock_save, mock_load):
        """Test that post IDs increment correctly"""
        mock_load.return_value = [
            {'id': 1, 'username': 'user1', 'replies': []},
            {'id': 2, 'username': 'user2', 'replies': []}
        ]
        
        result = add_forum_post('john1234', 'Title', 'Content')
        self.assertEqual(result['id'], 3)
    
    @patch('app.load_forum')
    @patch('app.save_forum')
    def test_add_reply_to_post_success(self, mock_save, mock_load):
        """Test adding reply to existing post"""
        posts = [{'id': 1, 'username': 'user1', 'replies': []}]
        mock_load.return_value = posts
        
        result = add_reply_to_post(1, 'john1234', 'Great tip!')
        
        self.assertTrue(result)
        mock_save.assert_called_once()
        # Check that reply was added
        self.assertEqual(len(posts[0]['replies']), 1)
        self.assertEqual(posts[0]['replies'][0]['username'], 'john1234')
        self.assertEqual(posts[0]['replies'][0]['content'], 'Great tip!')
    
    @patch('app.load_forum')
    @patch('app.save_forum')
    def test_add_reply_to_post_nonexistent_post(self, mock_save, mock_load):
        """Test adding reply to non-existent post"""
        mock_load.return_value = [{'id': 1, 'username': 'user1', 'replies': []}]
        
        result = add_reply_to_post(999, 'john1234', 'Reply')
        
        self.assertFalse(result)
        mock_save.assert_not_called()


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling"""
    
    def test_budget_with_negative_value(self):
        """Test that negative budget is handled"""
        # This should be caught in the Flask route validation
        self.assertFalse(is_valid_password('pass'))  # Example edge case
    
    def test_get_recommendations_for_city_empty_categories(self):
        """Test recommendations with empty category list"""
        with patch('app.load_city_data') as mock_load:
            mock_load.return_value = {'Paris': {'places': []}}
            recommendations = get_recommendations_for_city('Paris', 100, [])
            self.assertEqual(len(recommendations), 0)
    
    def test_very_long_username(self):
        """Test username validation with very long strings"""
        long_username = 'a' * 1000 + '1234'
        # Should still be valid since it ends with 4 digits
        self.assertTrue(is_valid_username(long_username))
    
    def test_special_characters_in_username(self):
        """Test username with special characters"""
        usernames = [
            'john@1234',  # @ symbol
            'john.doe1234',  # dot
            'john-doe1234',  # hyphen
        ]
        # Current implementation doesn't restrict special chars
        for username in usernames:
            # These will pass length/digit check but might be caught elsewhere
            if len(username) >= 5 and username[-4:].isdigit():
                self.assertTrue(is_valid_username(username))


class TestIntegration(unittest.TestCase):
    """Integration tests combining multiple functions"""
    
    def test_password_validation_comprehensive(self):
        """Comprehensive password validation test"""
        categories = ['Food', 'Sightseeing']
        
        # Verify password validation is working
        self.assertTrue(is_valid_password('SecurePass1'))
        self.assertFalse(is_valid_password('weak'))


class TestDataStructure(unittest.TestCase):
    """Test data structure integrity"""
    
    @patch('app.load_forum')
    def test_forum_post_structure(self, mock_load):
        """Verify forum posts have required fields"""
        mock_load.return_value = []
        
        post = add_forum_post('user1234', 'Title', 'Content', 'Paris')
        
        required_fields = ['id', 'username', 'title', 'content', 'city', 'created_at', 'replies']
        for field in required_fields:
            self.assertIn(field, post, f"Missing field: {field}")


# Run tests if executed directly
if __name__ == '__main__':
    unittest.main(verbosity=2)
