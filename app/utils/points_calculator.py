def calculate_points(difficulty: str, priority: str) -> int:
    """Calculate points based on issue difficulty and priority"""
    difficulty_points = {
        "easy": 100,
        "medium": 200,
        "hard": 300
    }
    
    priority_multiplier = {
        "low": 1.0,
        "medium": 1.5,
        "high": 2.0
    }
    
    base_points = difficulty_points.get(difficulty, 100)
    multiplier = priority_multiplier.get(priority, 1.0)
    
    return int(base_points * multiplier)
