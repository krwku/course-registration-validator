import json
from pathlib import Path
from .curriculum_selector import get_curriculum_for_student_id, get_available_curricula

def load_comprehensive_course_data():
    """
    Load all course data from new folder structure.
    """
    course_data_dir = Path(__file__).parent.parent / "course_data"
    available_files = {}
    
    if course_data_dir.exists():
        # Get available curricula from folder structure (newest first for UI)
        curricula = get_available_curricula()
        curricula.sort(reverse=True)  # Sort newest first for UI display
        
        # Process each curriculum folder
        for curriculum in curricula:
            curriculum_dir = course_data_dir / curriculum
            courses_file = curriculum_dir / "courses.json"
            
            if courses_file.exists():
                try:
                    with open(courses_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # Validate that the file contains course data
                    has_courses = (
                        'industrial_engineering_courses' in data or
                        'gen_ed_courses' in data or
                        'other_related_courses' in data
                    )
                    
                    if has_courses:
                        available_files[curriculum] = {
                            'data': data,
                            'filename': f"{curriculum}/courses.json",
                            'path': str(courses_file),
                            'curriculum_folder': curriculum
                        }
                except Exception as e:
                    print(f"Error loading {courses_file}: {e}")
                    continue
    
    return available_files

def load_curriculum_data(curriculum_name: str = None, student_id: str = None):
    """
    Load curriculum data with auto-selection based on student ID.
    
    Args:
        curriculum_name: Specific curriculum to load (e.g., "B-IE-2565")
        student_id: Student ID for auto-selection (e.g., "6512345678")
    
    Returns:
        Dictionary with curriculum data and template
    """
    course_data_dir = Path(__file__).parent.parent / "course_data"
    
    # Determine which curriculum to use
    if curriculum_name:
        selected_curriculum = curriculum_name
    elif student_id:
        selected_curriculum = get_curriculum_for_student_id(student_id)
    else:
        selected_curriculum = get_curriculum_for_student_id("")  # Gets newest
    
    curriculum_dir = course_data_dir / selected_curriculum
    courses_file = curriculum_dir / "courses.json"
    template_file = curriculum_dir / "template.json"
    
    result = {
        'curriculum_name': selected_curriculum,
        'courses': None,
        'template': None,
        'error': None
    }
    
    # Load courses
    if courses_file.exists():
        try:
            with open(courses_file, 'r', encoding='utf-8') as f:
                result['courses'] = json.load(f)
        except Exception as e:
            result['error'] = f"Error loading courses: {e}"
    else:
        result['error'] = f"Courses file not found: {courses_file}"
    
    # Load template
    if template_file.exists():
        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                result['template'] = json.load(f)
        except Exception as e:
            result['error'] = f"Error loading template: {e}"
    else:
        result['error'] = f"Template file not found: {template_file}"
    
    return result

def validate_course_data_structure(data):
    """
    Validate the structure of course data.
    FIXED: Updated validation for new technical electives structure.
    """
    required_fields = ['code', 'name', 'credits']
    
    # Check industrial engineering courses
    if 'industrial_engineering_courses' in data:
        for course in data['industrial_engineering_courses']:
            for field in required_fields:
                if field not in course:
                    return False, f"Missing field '{field}' in industrial engineering course"
            # ADDED: Check for technical_electives attribute validity
            if 'technical_electives' in course and not isinstance(course['technical_electives'], bool):
                return False, f"technical_electives attribute must be boolean in course {course.get('code', 'Unknown')}"
    
    # Check general education courses
    if 'gen_ed_courses' in data:
        for category, courses in data['gen_ed_courses'].items():
            for course in courses:
                for field in required_fields:
                    if field not in course:
                        return False, f"Missing field '{field}' in gen-ed course"
    
    # REMOVED: Check technical electives - no longer separate section
    
    return True, "Valid structure"

def get_course_statistics(data):
    """
    Get statistics about the course data.
    FIXED: Now properly counts technical electives from B-IE files.
    """
    stats = {
        'ie_courses': 0,
        'gen_ed_courses': 0,
        'technical_electives': 0,
        'other_courses': 0,
        'total_courses': 0
    }
    
    if 'industrial_engineering_courses' in data:
        ie_courses = data['industrial_engineering_courses']
        stats['ie_courses'] = len(ie_courses)
        
        # FIXED: Count technical electives from B-IE files
        tech_electives_count = sum(1 for course in ie_courses if course.get('technical_electives', False))
        stats['technical_electives'] = tech_electives_count
        # Adjust IE courses count to exclude technical electives
        stats['ie_courses'] = stats['ie_courses'] - tech_electives_count
    
    if 'gen_ed_courses' in data:
        for category, courses in data['gen_ed_courses'].items():
            stats['gen_ed_courses'] += len(courses)
    
    # REMOVED: No longer loading from separate technical_electives.json
    
    if 'other_related_courses' in data:
        stats['other_courses'] = len(data['other_related_courses'])
    
    stats['total_courses'] = sum([
        stats['ie_courses'],
        stats['gen_ed_courses'], 
        stats['technical_electives'],
        stats['other_courses']
    ])
    
    return stats

def analyze_course_distribution(data):
    """
    Analyze the distribution of courses across categories.
    FIXED: Now includes proper technical electives analysis.
    """
    distribution = {
        'ie_core': [],
        'technical_electives': [],
        'gen_ed': {
            'wellness': [],
            'wellness_PE': [],
            'entrepreneurship': [],
            'language_communication_thai': [],
            'language_communication_foreigner': [],
            'language_communication_computer': [],
            'thai_citizen_global': [],
            'aesthetics': []
        },
        'other_related': []
    }
    
    # Process IE courses
    if 'industrial_engineering_courses' in data:
        for course in data['industrial_engineering_courses']:
            # FIXED: Check technical_electives attribute
            if course.get('technical_electives', False):
                distribution['technical_electives'].append(course)
            else:
                distribution['ie_core'].append(course)
    
    # Process other related courses
    if 'other_related_courses' in data:
        distribution['other_related'] = data['other_related_courses']
    
    # Process Gen-Ed courses
    if 'gen_ed_courses' in data:
        for subcategory, courses in data['gen_ed_courses'].items():
            if subcategory in distribution['gen_ed']:
                distribution['gen_ed'][subcategory] = courses
    
    return distribution

def get_technical_electives_from_data(data):
    """
    Extract technical electives from B-IE course data.
    NEW: Helper function to get technical electives with their attributes.
    """
    technical_electives = []
    
    if 'industrial_engineering_courses' in data:
        for course in data['industrial_engineering_courses']:
            if course.get('technical_electives', False):
                technical_electives.append(course)
    
    return technical_electives
