"""
Test suite for recommender.py module
"""

import unittest
from recommender import (
    filter_by_budget,
    filter_by_category,
    rank_recommendations,
    get_recommendations
)


class TestFilterByBudget(unittest.TestCase):
    """Test filter_by_budget function"""
    
    def test_filter_within_budget(self):
        """Test filtering places within budget"""
        places = [
            {'name': 'Cheap', 'cost': 5},
            {'name': 'Medium', 'cost': 15},
            {'name': 'Expensive', 'cost': 50}
        ]
        result = filter_by_budget(places, budget=30)
        # Should include Cheap and Medium (both <= 30), exclude Expensive
        self.assertEqual(len(result), 2)
        self.assertTrue(any(p['name'] == 'Cheap' for p in result))
        self.assertTrue(any(p['name'] == 'Medium' for p in result))
    
    def test_filter_all_within_budget(self):
        """Test when all places are within budget"""
        places = [
            {'name': 'Item1', 'cost': 5},
            {'name': 'Item2', 'cost': 10}
        ]
        result = filter_by_budget(places, budget=50)
        self.assertEqual(len(result), 2)
    
    def test_filter_none_within_budget(self):
        """Test when no places are within budget"""
        places = [
            {'name': 'Expensive1', 'cost': 50},
            {'name': 'Expensive2', 'cost': 100}
        ]
        result = filter_by_budget(places, budget=30)
        # No items cost 30 or less
        self.assertEqual(len(result), 0)
    
    def test_filter_empty_places(self):
        """Test with empty places list"""
        result = filter_by_budget([], budget=50)
        self.assertEqual(len(result), 0)
    
    def test_filter_invalid_budget(self):
        """Test with invalid budget"""
        places = [{'name': 'Item', 'cost': 10}]
        result = filter_by_budget(places, budget=-10)
        self.assertEqual(len(result), 0)
    
    def test_filter_with_exact_budget_match(self):
        """Test filter when item cost exactly matches budget"""
        places = [
            {'name': 'Item1', 'cost': 5},
            {'name': 'Item2', 'cost': 50}
        ]
        result = filter_by_budget(places, budget=50)
        # Should include both Item1 and Item2 (both <= 50)
        self.assertEqual(len(result), 2)


class TestFilterByCategory(unittest.TestCase):
    """Test filter_by_category function"""
    
    def test_filter_single_category(self):
        """Test filtering by single category"""
        places = [
            {'name': 'Museum', 'category': 'Culture/History'},
            {'name': 'Restaurant', 'category': 'Food'},
            {'name': 'Park', 'category': 'Sightseeing'}
        ]
        result = filter_by_category(places, ['Food'])
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['name'], 'Restaurant')
    
    def test_filter_multiple_categories(self):
        """Test filtering by multiple categories"""
        places = [
            {'name': 'Museum', 'category': 'Culture/History'},
            {'name': 'Restaurant', 'category': 'Food'},
            {'name': 'Park', 'category': 'Sightseeing'}
        ]
        result = filter_by_category(places, ['Food', 'Sightseeing'])
        self.assertEqual(len(result), 2)
    
    def test_filter_no_matches(self):
        """Test when no categories match"""
        places = [
            {'name': 'Museum', 'category': 'Culture/History'}
        ]
        result = filter_by_category(places, ['Food'])
        self.assertEqual(len(result), 0)
    
    def test_filter_empty_categories(self):
        """Test with empty category list"""
        places = [{'name': 'Museum', 'category': 'Culture/History'}]
        result = filter_by_category(places, [])
        self.assertEqual(len(result), 0)
    
    def test_filter_empty_places(self):
        """Test with empty places list"""
        result = filter_by_category([], ['Food'])
        self.assertEqual(len(result), 0)


class TestRankRecommendations(unittest.TestCase):
    """Test rank_recommendations function"""
    
    def test_rank_by_cost(self):
        """Test ranking by cost"""
        places = [
            {'name': 'Expensive', 'cost': 50},
            {'name': 'Cheap', 'cost': 10},
            {'name': 'Free', 'cost': 0}
        ]
        result = rank_recommendations(places, sort_by='cost', limit=10)
        # Should be sorted by cost (ascending)
        self.assertEqual(result[0]['name'], 'Free')
        self.assertEqual(result[1]['name'], 'Cheap')
        self.assertEqual(result[2]['name'], 'Expensive')
    
    def test_rank_by_name(self):
        """Test ranking by name (alphabetical)"""
        places = [
            {'name': 'Zoo', 'cost': 10},
            {'name': 'Museum', 'cost': 15},
            {'name': 'Park', 'cost': 0}
        ]
        result = rank_recommendations(places, sort_by='name', limit=10)
        self.assertEqual(result[0]['name'], 'Museum')
        self.assertEqual(result[1]['name'], 'Park')
        self.assertEqual(result[2]['name'], 'Zoo')
    
    def test_rank_limit(self):
        """Test that limit is respected"""
        places = [
            {'name': f'Item{i}', 'cost': i} for i in range(20)
        ]
        result = rank_recommendations(places, sort_by='cost', limit=5)
        self.assertEqual(len(result), 5)
    
    def test_rank_empty_places(self):
        """Test with empty places"""
        result = rank_recommendations([], sort_by='cost', limit=10)
        self.assertEqual(len(result), 0)
    
    def test_rank_invalid_sort_by(self):
        """Test with invalid sort_by field (should default to cost)"""
        places = [
            {'name': 'Expensive', 'cost': 50},
            {'name': 'Cheap', 'cost': 10}
        ]
        result = rank_recommendations(places, sort_by='invalid', limit=10)
        # Should still work, defaulting to cost
        self.assertEqual(result[0]['name'], 'Cheap')


class TestGetRecommendations(unittest.TestCase):
    """Test get_recommendations function"""
    
    def test_get_recommendations_valid(self):
        """Test getting recommendations with valid data"""
        places = [
            {'name': 'Cheap Food', 'category': 'Food', 'cost': 5},
            {'name': 'Expensive Food', 'category': 'Food', 'cost': 100},
            {'name': 'Museum', 'category': 'Culture/History', 'cost': 10}
        ]
        result = get_recommendations('Paris', budget=50, categories=['Food'], places=places)
        # Should include Cheap Food (5 <= 25), not Expensive Food (100 > 25)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['name'], 'Cheap Food')
    
    def test_get_recommendations_multiple_categories(self):
        """Test with multiple categories"""
        places = [
            {'name': 'Restaurant', 'category': 'Food', 'cost': 15},
            {'name': 'Museum', 'category': 'Culture/History', 'cost': 10},
            {'name': 'Park', 'category': 'Sightseeing', 'cost': 0}
        ]
        result = get_recommendations('Rome', budget=50, categories=['Food', 'Culture/History'], places=places)
        # Should include Restaurant and Museum, not Park
        self.assertEqual(len(result), 2)
    
    def test_get_recommendations_empty_places(self):
        """Test with no places available"""
        result = get_recommendations('NoCity', budget=50, categories=['Food'], places=[])
        self.assertEqual(len(result), 0)
    
    def test_get_recommendations_no_matching_category(self):
        """Test when no places match the selected categories"""
        places = [
            {'name': 'Museum', 'category': 'Culture/History', 'cost': 10}
        ]
        result = get_recommendations('London', budget=50, categories=['Food'], places=places)
        self.assertEqual(len(result), 0)


class TestIntegration(unittest.TestCase):
    """Integration tests for recommendation workflow"""
    
    def test_full_recommendation_workflow(self):
        """Test complete recommendation workflow"""
        places = [
            {'name': 'Street Food', 'category': 'Food', 'cost': 8, 'duration': '1h', 'description': 'Local food'},
            {'name': 'Market', 'category': 'Shopping', 'cost': 20, 'duration': '2h', 'description': 'Shopping tour'},
            {'name': 'Museum', 'category': 'Culture/History', 'cost': 12, 'duration': '2h', 'description': 'History museum'},
            {'name': 'Park', 'category': 'Sightseeing', 'cost': 0, 'duration': '1h', 'description': 'Nature park'},
            {'name': 'Fancy Restaurant', 'category': 'Food', 'cost': 50, 'duration': '2h', 'description': 'Fine dining'}
        ]
        
        budget = 60
        categories = ['Food', 'Culture/History']
        
        # Get recommendations
        result = get_recommendations('TestCity', budget=budget, categories=categories, places=places)
        
        # Verify results
        self.assertGreater(len(result), 0)
        self.assertLessEqual(len(result), 10)
        
        # All should be in selected categories
        for r in result:
            self.assertIn(r['category'], categories)
        
        # All should be within budget (no reserve)
        for r in result:
            self.assertLessEqual(r['cost'], budget)


if __name__ == '__main__':
    unittest.main(verbosity=2)
