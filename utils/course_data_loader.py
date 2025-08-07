import json
from pathlib import Path

def load_comprehensive_course_data():
    """Load all course data including Gen-Ed and Technical Electives with improved error handling."""
    course_data_dir = Path(__file__).parent.parent / "course_data"
    
    # Try to load from existing files
    available_files = {}
    
    if course_data_dir.exists():
        # Files to permanently exclude from the dropdown (support files)
        excluded_files = {
            "gen_ed_courses.json",
            "ie_core_courses.json", 
            "technical_electives.json"
        }
        
        # Scan for all JSON files and categorize them
        curriculum_files = []
        other_files = []
        
        for json_file in course_data_dir.glob("*.json"):
            # Skip excluded support files
            if json_file.name in excluded_files:
                continue
            
            # Check if it's a B-IE curriculum file
            if json_file.name.startswith("B-IE-") and json_file.name.endswith(".json"):
                curriculum_files.append(json_file)
            else:
                other_files.append(json_file)
        
        # Sort curriculum files by year (newest first)
        def extract_year(filename):
            """Extract year from B-IE-XXXX.json format"""
            try:
                # Extract the 4-digit year from B-IE-XXXX.json
                stem = filename.stem  # Gets "B-IE-XXXX"
                year_part = stem.split("-")[-1]  # Gets "XXXX"
                return int(year_part) if year_part.isdigit() else 0
            except:
                return 0
        
        curriculum_files.sort(key=extract_year, reverse=True)
        
        # Process curriculum files (B-IE-XXXX.json)
        for json_file in curriculum_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Validate that the file contains course data
                has_courses = (
                    'industrial_engineering_courses' in data or
                    'gen_ed_courses' in data or
                    'technical_electives' in data or
                    'other_related_courses' in data
                )
                
                if has_courses:
                    # Create clean display name: B-IE-2565.json -> B-IE-2565
                    display_name = json_file.stem
                    
                    available_files[display_name] = {
                        'data': data,
                        'filename': json_file.name,
                        'path': str(json_file)
                    }
            except Exception as e:
                print(f"Error loading {json_file.name}: {e}")
                continue
        
        # Process other valid JSON files (non-curriculum files)
        for json_file in other_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Validate that the file contains course data
                has_courses = (
                    'industrial_engineering_courses' in data or
                    'gen_ed_courses' in data or
                    'technical_electives' in data or
                    'other_related_courses' in data
                )
                
                if has_courses:
                    # Create a clean display name for other files
                    file_name = json_file.stem
                    display_name = file_name.replace("_", "-").replace("-courses", "").upper()
                    
                    # Limit length for readability
                    if len(display_name) > 20:
                        display_name = display_name[:17] + "..."
                    
                    # Ensure uniqueness
                    original_display_name = display_name
                    counter = 1
                    while display_name in available_files:
                        display_name = f"{original_display_name}-{counter}"
                        counter += 1
                    
                    available_files[display_name] = {
                        'data': data,
                        'filename': json_file.name,
                        'path': str(json_file)
                    }
            except Exception as e:
                print(f"Error loading {json_file.name}: {e}")
    
    return available_files

def validate_course_data_structure(data):
    """Validate the structure of course data."""
    required_fields = ['code', 'name', 'credits']
    
    # Check industrial engineering courses
    if 'industrial_engineering_courses' in data:
        for course in data['industrial_engineering_courses']:
            for field in required_fields:
                if field not in course:
                    return False, f"Missing field '{field}' in industrial engineering course"
    
    # Check general education courses
    if 'gen_ed_courses' in data:
        for category, courses in data['gen_ed_courses'].items():
            for course in courses:
                for field in required_fields:
                    if field not in course:
                        return False, f"Missing field '{field}' in gen-ed course"
    
    # Check technical electives
    if 'technical_electives' in data:
        for course in data['technical_electives']:
            for field in required_fields:
                if field not in course:
                    return False, f"Missing field '{field}' in technical elective"
    
    return True, "Valid structure"

def get_course_statistics(data):
    """Get statistics about the course data."""
    stats = {
        'ie_courses': 0,
        'gen_ed_courses': 0,
        'technical_electives': 0,
        'other_courses': 0,
        'total_courses': 0
    }
    
    if 'industrial_engineering_courses' in data:
        stats['ie_courses'] = len(data['industrial_engineering_courses'])
    
    if 'gen_ed_courses' in data:
        for category, courses in data['gen_ed_courses'].items():
            stats['gen_ed_courses'] += len(courses)
    
    if 'technical_electives' in data:
        stats['technical_electives'] = len(data['technical_electives'])
    
    if 'other_related_courses' in data:
        stats['other_courses'] = len(data['other_related_courses'])
    
    stats['total_courses'] = sum([
        stats['ie_courses'],
        stats['gen_ed_courses'], 
        stats['technical_electives'],
        stats['other_courses']
    ])
    
    return stats

def create_unified_course_lookup(data):
    """Create a unified lookup dictionary from course data."""
    lookup = {}
    
    # Add IE courses
    if 'industrial_engineering_courses' in data:
        for course in data['industrial_engineering_courses']:
            lookup[course['code']] = {
                **course,
                'category': 'ie_core',
                'subcategory': 'core'
            }
    
    # Add other related courses
    if 'other_related_courses' in data:
        for course in data['other_related_courses']:
            lookup[course['code']] = {
                **course,
                'category': 'ie_core',
                'subcategory': 'foundation'
            }
    
    # Add Gen-Ed courses
    if 'gen_ed_courses' in data:
        for subcategory, courses in data['gen_ed_courses'].items():
            for course in courses:
                lookup[course['code']] = {
                    **course,
                    'category': 'gen_ed',
                    'subcategory': subcategory
                }
    
    # Add Technical Electives
    if 'technical_electives' in data:
        for course in data['technical_electives']:
            lookup[course['code']] = {
                **course,
                'category': 'technical_electives',
                'subcategory': 'technical'
            }
    
    return lookup
