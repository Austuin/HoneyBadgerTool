"""Key Crest Calculator - Pure calculation logic (no UI)"""
import math


def calculate_key_crest(shaft_diameter: float, key_width: float) -> dict:
    """
    Calculate the crest height within a keyway.
    
    Args:
        shaft_diameter: The diameter of the shaft (must be positive)
        key_width: The width of the key (must be positive and less than shaft_diameter)
    
    Returns:
        dict with 'success', 'crest' (if successful), or 'error' (if failed)
    """
    # Validation
    if shaft_diameter <= 0:
        return {'success': False, 'error': 'Shaft diameter must be positive.'}
    if key_width <= 0:
        return {'success': False, 'error': 'Key width must be positive.'}
    if key_width >= shaft_diameter:
        return {'success': False, 'error': 'Key width must be less than shaft diameter.'}
    
    # Calculation
    shaft_radius = shaft_diameter / 2
    half_key = key_width / 2
    pythag = math.sqrt(shaft_radius ** 2 - half_key ** 2)
    crest = shaft_radius - pythag
    
    return {
        'success': True,
        'crest': crest,
        'shaft_diameter': shaft_diameter,
        'key_width': key_width
    }
