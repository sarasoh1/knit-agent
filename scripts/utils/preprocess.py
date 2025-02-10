import re
import requests
from models.helpers.pattern_needle_size import PatternNeedleSize

def preprocess_pattern_needle_sizes(pattern_needle_sizes: dict) -> PatternNeedleSize:
    """
    Preprocess the pattern needle sizes to make them more usable for the model.
    """
    pattern_needle_size = PatternNeedleSize(
        id=pattern_needle_sizes["id"],
        us=pattern_needle_sizes["us"],
        metric=pattern_needle_sizes["metric"],
        is_knit=pattern_needle_sizes["knitting"],
        is_crochet=pattern_needle_sizes["crochet"],
        name=pattern_needle_sizes["name"],
        pretty_metric=pattern_needle_sizes["pretty_metric"],
        hook=pattern_needle_sizes["hook"],
    )
    return pattern_needle_size

def preprocess_pattern(pattern: dict) -> dict:
    """
    Preprocess a pattern to make it more usable for the model.
    """
    pattern_dict = {}

    # Add the pattern id
    pattern_dict["id"] = int(pattern["id"])

    # Add the pattern name
    pattern_dict["name"] = pattern["name"]  
    
    # Add the pattern permalink
    pattern_dict["permalink"] = pattern["permalink"]

    # Add the pattern craft
    pattern_dict["craft"] = pattern.get("craft", {}).get("permalink")
    
    # Add the pattern download location
    pattern_dict["download_location"] = pattern["download_location"]
    
    # Add the pattern ratings
    pattern_dict["ratings"] = {
        "rating_average": pattern.get("rating_average"),
        "rating_count": pattern.get("rating_count"),
        "difficulty_average": pattern.get("difficulty_average"),
        "difficulty_count": pattern.get("difficulty_count"),
        "favorites_count": pattern.get("favorites_count"),
        "projects_count": pattern.get("projects_count"),
    }
    
    # Add the pattern gauge
    pattern_dict["gauge"] ={
        "gauge": pattern.get("gauge"),
        "gauge_divisor": pattern.get("gauge_divisor"),
        "gauge_pattern": pattern.get("gauge_pattern"),
        "row_gauge": pattern.get("row_gauge"),
        "yardage": pattern.get("yardage"),
        "yardage_max": pattern.get("yardage_max"),
        "gauge_description": pattern.get("gauge_description"),
        "yarn_weight_description": pattern.get("yarn_weight_description"),
        "yardage_description": pattern.get("yardage_description"),
        "pattern_needle_sizes": [preprocess_pattern_needle_sizes(needle_size) for needle_size in pattern.get("pattern_needle_sizes", [])],
    }
    
    # Add the pattern attributes
    pattern_dict["pattern_attributes"] = pattern.get("pattern_attributes")
    
    # Add the pattern categories
    pattern_dict["pattern_categories"] = pattern.get("pattern_categories")
    
    return pattern_dict

def check_pattern_url_is_active(pattern_url: str) -> bool:
    """
    Check if the pattern url is active
    Args:
        pattern_url (str): The url of the pattern

    Returns:
        bool: True if the pattern url is active, False otherwise
    """
    response = requests.get(pattern_url, timeout=20)
    js_redirect_pattern = re.search(r'window\.location\.href\s*=\s*["\'](.*?)["\']', response.text)

    if js_redirect_pattern:
        redirect_path = js_redirect_pattern.group(1)
        print(f"Detected JavaScript redirect to: {redirect_path}")

        # If it's redirecting to a suspicious path like "/lander", consider it inactive
        if "/lander" in redirect_path or "godaddy.com" in redirect_path:
            return False
    
    return True

