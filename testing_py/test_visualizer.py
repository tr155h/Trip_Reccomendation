"""
Test suite for visualizer.py module
Tests visualization functions for budget charts and cost breakdown
"""

import unittest
from visualizer import (
    generate_budget_chart
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


if __name__ == '__main__':
    unittest.main(verbosity=2)
