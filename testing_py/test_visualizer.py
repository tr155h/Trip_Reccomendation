"""
Test suite for visualizer.py module
Tests visualization functions for budget charts and cost breakdown
"""

import unittest
from visualizer import (
    generate_budget_chart,
    generate_cost_breakdown_chart
)


class TestGenerateBudgetChart(unittest.TestCase):
    """Test generate_budget_chart function"""
    
    def test_valid_budget_chart(self):
        """Test generating chart with valid inputs"""
        result = generate_budget_chart(budget=100, activities_cost=60)
        
        self.assertEqual(result['budget'], 100)
        self.assertEqual(result['activities_cost'], 60)
        self.assertEqual(result['total_planned'], 60)
        self.assertEqual(result['remaining'], 40)
        self.assertFalse(result['is_over_budget'])
        self.assertEqual(result['chart_type'], 'bar')
    
    def test_budget_chart_over_budget(self):
        """Test chart when planned cost exceeds budget"""
        result = generate_budget_chart(budget=100, activities_cost=120)
        
        self.assertEqual(result['total_planned'], 120)
        self.assertTrue(result['is_over_budget'])
        self.assertEqual(result['remaining'], -20)  # Shows negative overage
    
    def test_budget_chart_zero_budget(self):
        """Test chart with zero budget"""
        result = generate_budget_chart(budget=0, activities_cost=0)
        
        self.assertEqual(result['budget'], 0)
        self.assertEqual(result['total_planned'], 0)
        self.assertEqual(result['remaining'], 0)
    
    def test_budget_chart_only_activities(self):
        """Test chart with only activity costs"""
        result = generate_budget_chart(budget=50, activities_cost=40)
        
        self.assertEqual(result['total_planned'], 40)
        self.assertEqual(result['remaining'], 10)
        self.assertFalse(result['is_over_budget'])
    
    def test_budget_chart_exact_match(self):
        """Test chart when activities match budget exactly"""
        result = generate_budget_chart(budget=50, activities_cost=50)
        
        self.assertEqual(result['total_planned'], 50)
        self.assertEqual(result['remaining'], 0)
        self.assertFalse(result['is_over_budget'])
    
    def test_budget_chart_negative_budget(self):
        """Test chart with negative budget"""
        result = generate_budget_chart(budget=-100, activities_cost=50)
        
        self.assertIn('error', result)
        self.assertEqual(result['budget'], 0)
    
    def test_budget_chart_negative_activities(self):
        """Test chart with negative activity cost"""
        result = generate_budget_chart(budget=100, activities_cost=-50)
        
        self.assertIn('error', result)
    
    def test_budget_chart_large_activity(self):
        """Test chart with large activity cost"""
        result = generate_budget_chart(budget=100, activities_cost=150)
        
        self.assertEqual(result['total_planned'], 150)
        self.assertTrue(result['is_over_budget'])
        self.assertEqual(result['remaining'], -50)
    
    def test_budget_chart_decimal_values(self):
        """Test chart with decimal values"""
        result = generate_budget_chart(budget=99.99, activities_cost=45.50)
        
        self.assertEqual(result['budget'], 99.99)
        self.assertEqual(result['activities_cost'], 45.50)
        self.assertEqual(result['total_planned'], 45.50)
    
    def test_budget_chart_large_values(self):
        """Test chart with large budget values"""
        result = generate_budget_chart(budget=10000, activities_cost=5000)
        
        self.assertEqual(result['budget'], 10000)
        self.assertEqual(result['total_planned'], 5000)
        self.assertEqual(result['remaining'], 5000)
    
    def test_budget_chart_structure(self):
        """Test that all required keys are present"""
        result = generate_budget_chart(budget=100, activities_cost=60)
        
        required_keys = ['budget', 'activities_cost', 'total_planned',
                        'remaining', 'is_over_budget', 'chart_type', 'labels', 'data', 'colors']
        for key in required_keys:
            self.assertIn(key, result, f"Missing key: {key}")


class TestGenerateCostBreakdownChart(unittest.TestCase):
    """Test generate_cost_breakdown_chart function"""
    
    def test_valid_breakdown_chart(self):
        """Test generating breakdown with valid activities"""
        activities = [
            {'food': 'Food', 'price': 30},
            {'food': 'Sightseeing', 'price': 50},
            {'food': 'Food', 'price': 20}
        ]
        result = generate_cost_breakdown_chart(activities)
        
        self.assertNotIn('error', result)
        self.assertEqual(result['total_cost'], 100)
        self.assertEqual(len(result['labels']), 2)
        self.assertIn('Food', result['labels'])
        self.assertIn('Sightseeing', result['labels'])
    
    def test_breakdown_chart_single_category(self):
        """Test breakdown with single category"""
        activities = [
            {'food': 'Food', 'price': 50},
            {'food': 'Food', 'price': 50}
        ]
        result = generate_cost_breakdown_chart(activities)
        
        self.assertEqual(result['total_cost'], 100)
        self.assertEqual(len(result['labels']), 1)
        self.assertEqual(result['data'][0], 100)
    
    def test_breakdown_chart_all_categories(self):
        """Test breakdown with all category types"""
        activities = [
            {'food': 'Food', 'price': 40},
            {'food': 'Sightseeing', 'price': 30},
            {'food': 'Shopping', 'price': 20},
            {'food': 'Culture/History', 'price': 25},
            {'food': 'Entertainment', 'price': 15}
        ]
        result = generate_cost_breakdown_chart(activities)
        
        self.assertEqual(result['total_cost'], 130)
        self.assertEqual(len(result['labels']), 5)
    
    def test_breakdown_chart_empty_activities(self):
        """Test breakdown with empty activity list"""
        result = generate_cost_breakdown_chart([])
        
        self.assertIn('error', result)
        self.assertEqual(result['total_cost'], 0)
        self.assertEqual(len(result['labels']), 0)
    
    def test_breakdown_chart_invalid_price(self):
        """Test breakdown with invalid price values"""
        activities = [
            {'food': 'Food', 'price': 'invalid'},
            {'food': 'Sightseeing', 'price': 50}
        ]
        result = generate_cost_breakdown_chart(activities)
        
        self.assertEqual(result['total_cost'], 50)
        self.assertEqual(result['labels'], ['Sightseeing'])
    
    def test_breakdown_chart_negative_price(self):
        """Test breakdown with negative price (should be skipped)"""
        activities = [
            {'food': 'Food', 'price': -30},
            {'food': 'Sightseeing', 'price': 50}
        ]
        result = generate_cost_breakdown_chart(activities)
        
        self.assertEqual(result['total_cost'], 50)
        self.assertEqual(result['labels'], ['Sightseeing'])
    
    def test_breakdown_chart_missing_fields(self):
        """Test breakdown with missing 'food' or 'price' fields"""
        activities = [
            {'price': 30},  # Missing 'food'
            {'food': 'Food'},  # Missing 'price'
            {'food': 'Sightseeing', 'price': 50}
        ]
        result = generate_cost_breakdown_chart(activities)
        
        # Should handle missing fields gracefully
        self.assertIn('Sightseeing', result['labels'])
    
    def test_breakdown_chart_percentages(self):
        """Test that percentages are calculated correctly"""
        activities = [
            {'food': 'Food', 'price': 50},
            {'food': 'Sightseeing', 'price': 50}
        ]
        result = generate_cost_breakdown_chart(activities)
        
        self.assertEqual(sum(result['percentages']), 100)
        self.assertEqual(result['percentages'][0], 50.0)
        self.assertEqual(result['percentages'][1], 50.0)
    
    def test_breakdown_chart_decimal_costs(self):
        """Test breakdown with decimal costs"""
        activities = [
            {'food': 'Food', 'price': 15.50},
            {'food': 'Sightseeing', 'price': 24.75}
        ]
        result = generate_cost_breakdown_chart(activities)
        
        self.assertEqual(result['total_cost'], 40.25)
    
    def test_breakdown_chart_zero_cost(self):
        """Test breakdown with zero-cost items"""
        activities = [
            {'food': 'Sightseeing', 'price': 0},
            {'food': 'Food', 'price': 50}
        ]
        result = generate_cost_breakdown_chart(activities)
        
        self.assertEqual(result['total_cost'], 50)
        self.assertEqual(len(result['labels']), 2)
    
    def test_breakdown_chart_structure(self):
        """Test that all required keys are present"""
        activities = [
            {'food': 'Food', 'price': 30},
            {'food': 'Sightseeing', 'price': 50}
        ]
        result = generate_cost_breakdown_chart(activities)
        
        required_keys = ['labels', 'data', 'colors', 'total_cost', 'chart_type', 
                        'breakdown', 'percentages']
        for key in required_keys:
            self.assertIn(key, result, f"Missing key: {key}")
    
    def test_breakdown_chart_colors(self):
        """Test that colors are assigned correctly"""
        activities = [
            {'food': 'Food', 'price': 30},
            {'food': 'Sightseeing', 'price': 50}
        ]
        result = generate_cost_breakdown_chart(activities)
        
        self.assertEqual(len(result['colors']), len(result['labels']))
        # Check that colors are non-empty strings
        for color in result['colors']:
            self.assertIsInstance(color, str)
            self.assertGreater(len(color), 0)


class TestIntegration(unittest.TestCase):
    """Integration tests for visualization functions"""
    
    def test_complete_budget_workflow(self):
        """Test complete budget visualization workflow"""
        # Generate budget chart
        budget_chart = generate_budget_chart(100, 70)
        
        self.assertFalse(budget_chart['is_over_budget'])
        self.assertEqual(budget_chart['remaining'], 30)
        
        # Verify chart has valid structure
        self.assertGreater(len(budget_chart['data']), 0)
        self.assertEqual(len(budget_chart['labels']), len(budget_chart['data']))
    
    def test_complete_breakdown_workflow(self):
        """Test complete cost breakdown workflow"""
        activities = [
            {'title': 'Dinner', 'food': 'Food', 'price': 40},
            {'title': 'Museum', 'food': 'Culture/History', 'price': 30},
            {'title': 'Shopping', 'food': 'Shopping', 'price': 25}
        ]
        
        breakdown_chart = generate_cost_breakdown_chart(activities)
        
        self.assertEqual(breakdown_chart['total_cost'], 95)
        self.assertNotIn('error', breakdown_chart)
        
        # Verify all categories present
        self.assertEqual(len(breakdown_chart['labels']), 3)
    
    def test_combined_budget_and_breakdown(self):
        """Test using budget and breakdown together"""
        total_budget = 100
        activities = [
            {'food': 'Food', 'price': 40},
            {'food': 'Sightseeing', 'price': 30}
        ]
        
        # Calculate totals
        activities_total = sum(a['price'] for a in activities)
        
        # Generate charts
        budget_chart = generate_budget_chart(total_budget, activities_total)
        breakdown_chart = generate_cost_breakdown_chart(activities)
        
        # Verify consistency
        self.assertEqual(budget_chart['activities_cost'], activities_total)
        self.assertEqual(breakdown_chart['total_cost'], activities_total)


if __name__ == '__main__':
    unittest.main(verbosity=2)
