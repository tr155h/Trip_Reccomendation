"""
Visualization functions for budget and cost analysis
Generates chart data for trip recommendations and budget planning
"""

import json
import logging
from io import BytesIO
import base64
from typing import Dict, List, Tuple

# Try to import matplotlib, fallback if not available
try:
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

logger = logging.getLogger(__name__)


def generate_budget_chart(budget: float, activities_cost: float, 
                         transport_cost: float = 0) -> Dict:
    """
    Generate budget comparison chart data.
    
    Shows the relationship between total budget and planned spending
    (activities + transport).
    
    Args:
        budget (float): Total budget allocated
        activities_cost (float): Total cost of planned activities
        transport_cost (float): Cost of transport (default: 0)
        
    Returns:
        Dict: Chart data with labels, values, and chart type for rendering
        
    Example:
        >>> chart = generate_budget_chart(100, 60, 10)
        >>> chart['total_planned']
        70
        >>> chart['remaining']
        30
    """
    if budget < 0 or activities_cost < 0 or transport_cost < 0:
        logger.warning(f"generate_budget_chart: Invalid values - "
                      f"budget={budget}, activities={activities_cost}, transport={transport_cost}")
        return {
            'error': 'Invalid budget values',
            'budget': 0,
            'total_planned': 0,
            'remaining': 0,
            'is_over_budget': False,
            'chart_type': 'bar'
        }
    
    total_planned = activities_cost + transport_cost
    remaining = budget - total_planned
    is_over_budget = remaining < 0
    
    chart_data = {
        'budget': round(budget, 2),
        'activities_cost': round(activities_cost, 2),
        'transport_cost': round(transport_cost, 2),
        'total_planned': round(total_planned, 2),
        'remaining': round(max(0, remaining), 2),
        'is_over_budget': is_over_budget,
        'chart_type': 'bar',
        'labels': ['Budget', 'Activities', 'Transport'],
        'data': [budget, activities_cost, transport_cost],
        'colors': [
            'rgba(76, 175, 80, 0.8)',  # Green for budget
            'rgba(255, 152, 0, 0.8)',  # Orange for activities
            'rgba(33, 150, 243, 0.8)'  # Blue for transport
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


def generate_chart_image(chart_type: str, labels: List[str], data: List[float],
                        title: str = '', colors: List[str] = None) -> str:
    """
    Generate a matplotlib chart image and return as base64 encoded string.
    
    Args:
        chart_type (str): Type of chart ('bar', 'pie', 'line')
        labels (List[str]): Chart labels
        data (List[float]): Data values
        title (str): Chart title
        colors (List[str]): Color list for bars/slices
        
    Returns:
        str: Base64 encoded image string, or empty string if matplotlib unavailable
    """
    if not MATPLOTLIB_AVAILABLE:
        logger.warning("generate_chart_image: Matplotlib not available")
        return ''
    
    if not labels or not data:
        logger.warning("generate_chart_image: No labels or data provided")
        return ''
    
    try:
        fig, ax = plt.subplots(figsize=(8, 5))
        
        if chart_type == 'bar':
            ax.bar(labels, data, color=colors or 'steelblue', edgecolor='black', linewidth=1.5)
            ax.set_ylabel('Cost ($)')
            ax.set_title(title or 'Budget Comparison')
        elif chart_type == 'pie':
            ax.pie(data, labels=labels, colors=colors, autopct='%1.1f%%',
                  startangle=90, textprops={'fontsize': 10})
            ax.set_title(title or 'Cost Breakdown')
        else:
            ax.plot(labels, data, marker='o', linewidth=2, markersize=8)
            ax.set_title(title or 'Cost Trend')
        
        # Save to BytesIO buffer
        buffer = BytesIO()
        plt.tight_layout()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        
        # Convert to base64
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        plt.close(fig)
        
        logger.info(f"generate_chart_image: Generated {chart_type} chart")
        return f"data:image/png;base64,{image_base64}"
        
    except Exception as e:
        logger.error(f"generate_chart_image: Failed to generate chart: {e}")
        return ''