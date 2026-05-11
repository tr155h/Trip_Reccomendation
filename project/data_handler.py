#Save and load JSON files
import json
import os
import logging
from typing import Dict, Any, List, Optional, Union

# Configure logging
logger = logging.getLogger(__name__)


def load_json_file(filename: str) -> Union[Dict, List, None]:
    """
    Load data from a JSON file.
    
    Args:
        filename (str): Path to the JSON file to load
        
    Returns:
        Union[Dict, List, None]: Parsed JSON data, or None if file doesn't exist or is invalid
        
    Raises:
        IOError: If file cannot be read (permissions issue)
        json.JSONDecodeError: If JSON is malformed
    """
    if not filename:
        logger.error("load_json_file: filename is empty")
        return None
    
    if not os.path.exists(filename):
        logger.warning(f"load_json_file: File does not exist: {filename}")
        return None
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            
            # Return empty dict/list if file is empty
            if not content:
                logger.debug(f"load_json_file: File is empty: {filename}")
                return {} if filename.endswith('_dict.json') else []
            
            data = json.loads(content)
            logger.debug(f"load_json_file: Successfully loaded {filename}")
            return data
            
    except json.JSONDecodeError as e:
        logger.error(f"load_json_file: Invalid JSON in {filename}: {str(e)}")
        return None
    except IOError as e:
        logger.error(f"load_json_file: IO error reading {filename}: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"load_json_file: Unexpected error loading {filename}: {str(e)}")
        return None


def save_json_file(filename: str, data: Union[Dict, List]) -> bool:
    """
    Save data to a JSON file.
    
    Args:
        filename (str): Path to the JSON file to save to
        data (Union[Dict, List]): Data to save (must be JSON serializable)
        
    Returns:
        bool: True if successful, False otherwise
        
    Raises:
        IOError: If file cannot be written (permissions issue)
        TypeError: If data is not JSON serializable
    """
    if not filename:
        logger.error("save_json_file: filename is empty")
        return False
    
    if data is None:
        logger.warning("save_json_file: data is None, skipping save")
        return False
    
    try:
        # Create directory if it doesn't exist
        directory = os.path.dirname(filename)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            logger.debug(f"save_json_file: Created directory: {directory}")
        
        # Write to file
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.debug(f"save_json_file: Successfully saved {filename}")
        return True
        
    except IOError as e:
        logger.error(f"save_json_file: IO error writing {filename}: {str(e)}")
        raise
    except TypeError as e:
        logger.error(f"save_json_file: Data is not JSON serializable: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"save_json_file: Unexpected error saving {filename}: {str(e)}")
        return False


def validate_data_structure(data: Any, data_type: str = 'unknown') -> bool:
    """
    Validate that data has the correct structure.
    
    Args:
        data (Any): Data to validate
        data_type (str): Type of data ('users', 'trips', 'forum', 'city', or 'unknown')
        
    Returns:
        bool: True if data structure is valid, False otherwise
    """
    if data is None:
        logger.warning(f"validate_data_structure: data is None (type: {data_type})")
        return False
    
    try:
        if data_type == 'users':
            return _validate_users_structure(data)
        elif data_type == 'trips':
            return _validate_trips_structure(data)
        elif data_type == 'forum':
            return _validate_forum_structure(data)
        elif data_type == 'city':
            return _validate_city_structure(data)
        else:
            # Generic validation: check if it's a dict or list
            logger.debug(f"validate_data_structure: Generic validation for type: {data_type}")
            return isinstance(data, (dict, list))
    except Exception as e:
        logger.error(f"validate_data_structure: Validation error for type {data_type}: {str(e)}")
        return False


def _validate_users_structure(data: Any) -> bool:
    """
    Validate users.json structure.
    Expected: {username: {password: str, trips: [...]}, ...}
    """
    if not isinstance(data, dict):
        logger.warning("validate_data_structure: users data is not a dict")
        return False
    
    for username, user_data in data.items():
        if not isinstance(user_data, dict):
            logger.warning(f"validate_data_structure: user {username} is not a dict")
            return False
        
        if 'password' not in user_data:
            logger.warning(f"validate_data_structure: user {username} missing 'password'")
            return False
        
        if not isinstance(user_data.get('trips', []), list):
            logger.warning(f"validate_data_structure: user {username} 'trips' is not a list")
            return False
    
    return True


def _validate_trips_structure(data: Any) -> bool:
    """
    Validate trips structure.
    Expected: [{trip_name: str, days: {day_num: {...}}}, ...]
    """
    if not isinstance(data, list):
        logger.warning("validate_data_structure: trips data is not a list")
        return False
    
    for trip in data:
        if not isinstance(trip, dict):
            logger.warning("validate_data_structure: trip is not a dict")
            return False
        
        if 'trip_name' not in trip:
            logger.warning("validate_data_structure: trip missing 'trip_name'")
            return False
        
        if not isinstance(trip.get('days', {}), dict):
            logger.warning("validate_data_structure: trip 'days' is not a dict")
            return False
    
    return True


def _validate_forum_structure(data: Any) -> bool:
    """
    Validate forum posts structure.
    Expected: [{id: int, username: str, title: str, content: str, replies: [...]}, ...]
    """
    if not isinstance(data, list):
        logger.warning("validate_data_structure: forum data is not a list")
        return False
    
    for post in data:
        if not isinstance(post, dict):
            logger.warning("validate_data_structure: forum post is not a dict")
            return False
        
        required_fields = ['id', 'username', 'title', 'content', 'created_at', 'replies']
        for field in required_fields:
            if field not in post:
                logger.warning(f"validate_data_structure: forum post missing '{field}'")
                return False
        
        if not isinstance(post.get('replies', []), list):
            logger.warning("validate_data_structure: forum post 'replies' is not a list")
            return False
    
    return True


def _validate_city_structure(data: Any) -> bool:
    """
    Validate city_data.json structure.
    Expected: {city_name: {name: str, places: [...], categories: [...]}, ...}
    """
    if not isinstance(data, dict):
        logger.warning("validate_data_structure: city data is not a dict")
        return False
    
    for city_name, city_data in data.items():
        if not isinstance(city_data, dict):
            logger.warning(f"validate_data_structure: city {city_name} is not a dict")
            return False
        
        required_fields = ['name', 'places', 'categories']
        for field in required_fields:
            if field not in city_data:
                logger.warning(f"validate_data_structure: city {city_name} missing '{field}'")
                return False
        
        if not isinstance(city_data.get('places', []), list):
            logger.warning(f"validate_data_structure: city {city_name} 'places' is not a list")
            return False
        
        if not isinstance(city_data.get('categories', []), list):
            logger.warning(f"validate_data_structure: city {city_name} 'categories' is not a list")
            return False
    
    return True


def load_json_file_safe(filename: str, data_type: str = 'unknown', default: Any = None) -> Any:
    """
    Load and validate JSON file with fallback to default.
    
    Args:
        filename (str): Path to JSON file
        data_type (str): Type of data for validation
        default (Any): Default value if load/validation fails
        
    Returns:
        Any: Loaded data if valid, otherwise default value
    """
    try:
        data = load_json_file(filename)
        
        if data is None:
            logger.warning(f"load_json_file_safe: Could not load {filename}, using default")
            return default
        
        if not validate_data_structure(data, data_type):
            logger.warning(f"load_json_file_safe: Invalid structure in {filename}, using default")
            return default
        
        return data
    except Exception as e:
        logger.error(f"load_json_file_safe: Error loading {filename}: {str(e)}")
        return default


def merge_json_data(existing_data: Dict, new_data: Dict, overwrite: bool = False) -> Dict:
    """
    Merge new JSON data with existing data.
    
    Args:
        existing_data (Dict): Existing data to merge into
        new_data (Dict): New data to merge
        overwrite (bool): If True, new data overwrites existing; if False, keeps existing
        
    Returns:
        Dict: Merged data
    """
    if not isinstance(existing_data, dict) or not isinstance(new_data, dict):
        logger.warning("merge_json_data: One or both inputs are not dicts")
        return existing_data
    
    merged = existing_data.copy()
    
    for key, value in new_data.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = merge_json_data(merged[key], value, overwrite)
        elif overwrite or key not in merged:
            merged[key] = value
    
    return merged