#!/usr/bin/env python3
"""
File operations for saving and loading transcript data.
"""
import json
import logging
import os
from pathlib import Path

logger = logging.getLogger("file_operations")

def save_transcript(model, file_path):
    """
    Save transcript data to the specified file.
    
    Args:
        model: The transcript model to save
        file_path: Path to save the file
        
    Returns:
        True if save was successful, False otherwise
    """
    try:
        # Prepare data
        data = model.to_dict()
        
        # Write to file
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=2)
        
        logger.info(f"Saved transcript to {file_path}")
        return True
    
    except Exception as e:
        logger.error(f"Failed to save file: {e}")
        return False

def load_transcript(model, file_path):
    """
    Load transcript data from the specified file.
    
    Args:
        model: The transcript model to update
        file_path: Path to the file to load
        
    Returns:
        True if load was successful, False otherwise
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        # Validate basic structure
        if not isinstance(data, dict) or "student_info" not in data or "semesters" not in data:
            logger.error(f"Invalid transcript data format: {file_path}")
            return False
        
        # Update model
        model.from_dict(data)
        model.set_changed(False)
        
        logger.info(f"Loaded transcript from {file_path}")
        return True
    
    except Exception as e:
        logger.error(f"Failed to load file: {e}")
        return False

def load_course_data(course_data_path):
    """
    Load course data from JSON file.
    
    Args:
        course_data_path: Path to course data JSON file
        
    Returns:
        Dictionary containing course data or empty dict on failure
    """
    try:
        if os.path.exists(course_data_path):
            with open(course_data_path, 'r', encoding='utf-8') as file:
                course_data = json.load(file)
                
            # Create a flattened dictionary of all courses for easy lookup
            all_courses = {}
            for course in course_data.get("industrial_engineering_courses", []):
                all_courses[course["code"]] = course
            
            logger.info(f"Loaded {len(all_courses)} courses from {course_data_path}")
            
            return {
                "raw_data": course_data, 
                "all_courses": all_courses
            }
        else:
            logger.warning(f"Course data file not found: {course_data_path}")
            return {}
    
    except Exception as e:
        logger.error(f"Error loading course data: {e}")
        return {}
