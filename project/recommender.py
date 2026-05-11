#Budget logic and filtering recommendations based on user input
import json
import logging
from typing import Dict, List, Any, Optional

# Configure logging
logger = logging.getLogger(__name__)


def filter_by_budget(places: List[Dict], budget: float, reserve: float = 25.0) -> List[Dict]:
    """
    Filter places by budget constraint.
    
    Args:
        places (List[Dict]): List of places with 'cost' field
        budget (float): Total budget available
        reserve (float): Amount to reserve (default $25)
        
    Returns:
        List[Dict]: Places within budget (after reserve)
        
    Example:
        places = [
            {'name': 'Cheap', 'cost': 10},
            {'name': 'Expensive', 'cost': 100}
        ]
        filtered = filter_by_budget(places, 50)  # budget=50, reserve=25
        # Returns places with cost <= 25
    """
    if not places or not isinstance(places, list):
        logger.warning("filter_by_budget: Invalid places input")
        return []
    
    if budget <= 0:
        logger.warning(f"filter_by_budget: Invalid budget {budget}")
        return []
    
    max_spend = budget - reserve
    if max_spend <= 0:
        logger.warning(f"filter_by_budget: Budget ${budget} after reserve ${reserve} is not positive")
        return []
    
    filtered = [p for p in places if isinstance(p, dict) and p.get('cost', float('inf')) <= max_spend]
    logger.debug(f"filter_by_budget: Filtered {len(places)} places to {len(filtered)} within ${max_spend}")
    
    return filtered


def filter_by_category(places: List[Dict], categories: List[str]) -> List[Dict]:
    """
    Filter places by selected categories.
    
    Args:
        places (List[Dict]): List of places with 'category' field
        categories (List[str]): List of categories to include
        
    Returns:
        List[Dict]: Places matching selected categories
        
    Example:
        places = [
            {'name': 'Museum', 'category': 'Culture/History'},
            {'name': 'Restaurant', 'category': 'Food'}
        ]
        filtered = filter_by_category(places, ['Food'])
        # Returns only the Restaurant
    """
    if not places or not isinstance(places, list):
        logger.warning("filter_by_category: Invalid places input")
        return []
    
    if not categories or not isinstance(categories, list):
        logger.warning("filter_by_category: Invalid categories input")
        return []
    
    filtered = [
        p for p in places 
        if isinstance(p, dict) and p.get('category', '') in categories
    ]
    logger.debug(f"filter_by_category: Filtered {len(places)} places to {len(filtered)} in categories {categories}")
    
    return filtered


def rank_recommendations(places: List[Dict], sort_by: str = 'cost', limit: int = 10) -> List[Dict]:
    """
    Rank and limit recommendations.
    
    Args:
        places (List[Dict]): List of places to rank
        sort_by (str): Field to sort by ('cost', 'duration', 'name'). Default: 'cost'
        limit (int): Maximum number of recommendations to return. Default: 10
        
    Returns:
        List[Dict]: Ranked places, limited to specified count
        
    Example:
        places = [
            {'name': 'Expensive', 'cost': 50},
            {'name': 'Cheap', 'cost': 10},
            {'name': 'Free', 'cost': 0}
        ]
        ranked = rank_recommendations(places, sort_by='cost', limit=2)
        # Returns [Free, Cheap] (sorted by cost, max 2)
    """
    if not places or not isinstance(places, list):
        logger.warning("rank_recommendations: Invalid places input")
        return []
    
    if limit <= 0:
        logger.warning(f"rank_recommendations: Invalid limit {limit}")
        return []
    
    # Validate sort_by field
    valid_sorts = ['cost', 'duration', 'name', 'category']
    if sort_by not in valid_sorts:
        logger.warning(f"rank_recommendations: Invalid sort_by '{sort_by}', using 'cost'")
        sort_by = 'cost'
    
    try:
        # Sort by the specified field
        if sort_by == 'cost':
            # Sort by cost (numeric)
            sorted_places = sorted(places, key=lambda x: x.get(sort_by, float('inf')))
        else:
            # Sort alphabetically for other fields
            sorted_places = sorted(places, key=lambda x: str(x.get(sort_by, '')))
        
        # Limit to specified number
        result = sorted_places[:limit]
        logger.debug(f"rank_recommendations: Ranked {len(places)} places, returning top {len(result)} sorted by {sort_by}")
        
        return result
    except Exception as e:
        logger.error(f"rank_recommendations: Error ranking places: {str(e)}")
        return places[:limit]  # Fallback to just limiting


def get_recommendations(city: str, budget: float, categories: List[str], places: List[Dict]) -> List[Dict]:
    """
    Generate recommendations based on city, budget, and categories.
    Combines filtering and ranking into single function.
    
    Args:
        city (str): City name
        budget (float): Total budget
        categories (List[str]): Selected categories
        places (List[Dict]): Available places in city from city_data.json
        
    Returns:
        List[Dict]: Top 10 recommendations from city data
    """
    if not places:
        logger.warning(f"get_recommendations: No places available for {city}")
        return []
    
    # Filter by category first
    by_category = filter_by_category(places, categories)
    if not by_category:
        logger.warning(f"get_recommendations: No places match categories {categories}")
        return []
    
    # Filter by budget
    by_budget = filter_by_budget(by_category, budget)
    if not by_budget:
        logger.warning(f"get_recommendations: No places within budget ${budget}")
        return []
    
    # Rank and return top 10
    recommendations = rank_recommendations(by_budget, sort_by='cost', limit=10)
    logger.info(f"get_recommendations: Generated {len(recommendations)} recommendations for {city}")
    
    return recommendations
