"""
Utility for automatic curriculum selection based on student ID
"""
from pathlib import Path
import os

def get_curriculum_for_student_id(student_id: str) -> str:
    """
    Auto-select curriculum based on student ID first 2 digits
    
    Args:
        student_id: 10-digit student ID (e.g., "6512345678")
    
    Returns:
        Curriculum folder name (e.g., "B-IE-2565")
    """
    if not student_id or len(student_id) < 2:
        return get_newest_curriculum()
    
    try:
        # Extract first 2 digits
        year_digits = int(student_id[:2])
        
        # Map year digits to curriculum
        if year_digits >= 65:
            return "B-IE-2565"
        elif year_digits >= 60:
            return "B-IE-2560"
        else:
            # For older students, use oldest available curriculum
            return get_oldest_curriculum()
            
    except (ValueError, IndexError):
        # If parsing fails, use newest
        return get_newest_curriculum()

def get_available_curricula() -> list:
    """Get list of available curriculum folders"""
    course_data_dir = Path(__file__).parent.parent / "course_data"
    curricula = []
    
    for item in course_data_dir.iterdir():
        if item.is_dir() and item.name.startswith("B-IE-"):
            curricula.append(item.name)
    
    return sorted(curricula)

def get_newest_curriculum() -> str:
    """Get the newest curriculum (highest version number)"""
    curricula = get_available_curricula()
    return curricula[-1] if curricula else "B-IE-2565"

def get_oldest_curriculum() -> str:
    """Get the oldest curriculum (lowest version number)"""
    curricula = get_available_curricula()
    return curricula[0] if curricula else "B-IE-2560"

def curriculum_exists(curriculum_name: str) -> bool:
    """Check if a curriculum folder exists"""
    course_data_dir = Path(__file__).parent.parent / "course_data"
    curriculum_path = course_data_dir / curriculum_name
    return curriculum_path.exists() and curriculum_path.is_dir()