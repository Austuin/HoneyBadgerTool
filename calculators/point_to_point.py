"""Point to Point Interval Calculator - Pure calculation logic (no UI)"""


def calculate_point_to_point(point1y: float, point1z: float, 
                              point2y: float, point2z: float, 
                              steps: int) -> dict:
    """
    Calculate intermediate points between two coordinates.
    
    Args:
        point1y: Starting Y coordinate
        point1z: Starting Z coordinate
        point2y: Ending Y coordinate
        point2z: Ending Z coordinate
        steps: Number of steps to divide the path into (must be positive integer)
    
    Returns:
        dict with 'success', calculation results, or 'error' (if failed)
    """
    # Validation
    if not isinstance(steps, int) or steps <= 0:
        return {'success': False, 'error': 'Steps must be a positive integer.'}
    
    # Calculate rates of change
    y_change = point2y - point1y
    z_change = point2z - point1z
    rate_of_change_y = y_change / steps
    rate_of_change_z = z_change / steps
    
    # Generate all intermediate points
    points = []
    for i in range(steps):
        new_y = point1y + (i + 1) * rate_of_change_y
        new_z = point1z + (i + 1) * rate_of_change_z
        points.append({
            'step': i + 1,
            'y': new_y,
            'z': new_z
        })
    
    return {
        'success': True,
        'rate_of_change_y': rate_of_change_y,
        'rate_of_change_z': rate_of_change_z,
        'points': points,
        'point1': {'y': point1y, 'z': point1z},
        'point2': {'y': point2y, 'z': point2z},
        'steps': steps
    }
