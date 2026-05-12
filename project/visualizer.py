"""
Visualization functions for budget and cost analysis
Generates chart data for trip recommendations and budget planning
"""

import json
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


def generate_budget_chart(budget: float, activities_cost: float) -> Dict:
   
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