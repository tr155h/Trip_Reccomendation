"""
Visualization functions for budget and cost analysis
Generates chart data for trip recommendations and budget planning
"""

import json
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


def generate_budget_chart(budget: float, activities_cost: float) -> Dict:
    """
    Generate budget comparison chart data.
    
    Shows the relationship between total budget and planned spending on activities.
    
    Args:
        budget (float): Total budget allocated
        activities_cost (float): Total cost of planned activities
        
    Returns:
        Dict: Chart data with labels, values, and chart type for rendering
        
    Example:
        >>> chart = generate_budget_chart(100, 60)
        >>> chart['total_planned']
        60
        >>> chart['remaining']
        40
    """
    if budget < 0 or activities_cost < 0:
        logger.warning(f"generate_budget_chart: Invalid values - "
                      f"budget={budget}, activities={activities_cost}")
        return {
            'error': 'Invalid budget values',
            'budget': 0,
            'total_planned': 0,
            'remaining': 0,
            'is_over_budget': False,
            'chart_type': 'bar'
        }
    
    total_planned = activities_cost
    remaining = budget - total_planned
    is_over_budget = remaining < 0
    
    chart_data = {
        'budget': round(budget, 2),
        'activities_cost': round(activities_cost, 2),
        'total_planned': round(total_planned, 2),
        'remaining': round(remaining, 2),
        'is_over_budget': is_over_budget,
        'chart_type': 'bar',
        'labels': ['Budget', 'Activities'],
        'data': [budget, activities_cost],
        'colors': [
            'rgba(76, 175, 80, 0.8)',  # Green for budget
            'rgba(255, 152, 0, 0.8)'   # Orange for activities
        ]
    }
    
    logger.info(f"generate_budget_chart: Generated budget chart - "
               f"budget=${budget}, planned=${total_planned}, "
               f"over_budget={is_over_budget}")
    
    return chart_data


def generate_cost_breakdown_chart(activities: List[Dict]) -> Dict:
    """
    Generate cost breakdown chart by category.
    
    Analyzes activities and groups costs by category (Food, Sightseeing, etc.)
    to show spending distribution.
    
    Args:
        activities (List[Dict]): List of activity dictionaries with 'food' (category)
                                and 'price' (cost) keys
                                
    Returns:
        Dict: Chart data with category breakdown for rendering
        
    Example:
        >>> activities = [
        ...     {'food': 'Food', 'price': 30},
        ...     {'food': 'Sightseeing', 'price': 50},
        ...     {'food': 'Food', 'price': 20}
        ... ]
        >>> chart = generate_cost_breakdown_chart(activities)
        >>> chart['total_cost']
        100
        >>> len(chart['labels'])
        2
    """
    if not activities:
        logger.warning("generate_cost_breakdown_chart: No activities provided")
        return {
            'error': 'No activities to breakdown',
            'labels': [],
            'data': [],
            'colors': [],
            'total_cost': 0,
            'chart_type': 'pie'
        }
    
    # Group costs by category
    category_costs = {}
    for activity in activities:
        if not isinstance(activity, dict):
            continue
            
        category = activity.get('food', 'Other')
        price = activity.get('price', 0)
        
        if not isinstance(price, (int, float)) or price < 0:
            logger.warning(f"generate_cost_breakdown_chart: Invalid price {price}")
            continue
        
        if category not in category_costs:
            category_costs[category] = 0
        category_costs[category] += price
    
    if not category_costs:
        logger.warning("generate_cost_breakdown_chart: No valid costs found")
        return {
            'error': 'No valid costs found',
            'labels': [],
            'data': [],
            'colors': [],
            'total_cost': 0,
            'chart_type': 'pie'
        }
    
    # Define consistent colors for categories
    color_map = {
        'Food': 'rgba(255, 152, 0, 0.8)',           # Orange
        'Sightseeing': 'rgba(33, 150, 243, 0.8)',   # Blue
        'Shopping': 'rgba(156, 39, 176, 0.8)',      # Purple
        'Culture/History': 'rgba(244, 67, 54, 0.8)', # Red
        'Entertainment': 'rgba(76, 175, 80, 0.8)',   # Green
        'Other': 'rgba(158, 158, 158, 0.8)'         # Gray
    }
    
    # Generate chart data
    labels = sorted(category_costs.keys())
    data = [category_costs[label] for label in labels]
    colors = [color_map.get(label, 'rgba(158, 158, 158, 0.8)') for label in labels]
    total_cost = sum(data)
    
    # Calculate percentages
    percentages = [round((cost / total_cost * 100), 1) if total_cost > 0 else 0 
                  for cost in data]
    
    chart_data = {
        'labels': labels,
        'data': [round(cost, 2) for cost in data],
        'percentages': percentages,
        'colors': colors,
        'total_cost': round(total_cost, 2),
        'chart_type': 'pie',
        'breakdown': {label: round(category_costs[label], 2) for label in labels}
    }
    
    logger.info(f"generate_cost_breakdown_chart: Generated breakdown - "
               f"total=${total_cost}, categories={len(labels)}")
    
    return chart_data