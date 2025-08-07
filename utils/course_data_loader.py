import json
from pathlib import Path

def load_comprehensive_course_data():
    """
    Load all course data including Gen-Ed and Technical Electives with improved error handling.
    FIXED: Now properly handles technical_electives attribute from B-IE files.
    """
    course_data_dir = Path(__file__).parent.parent / "course_data"
    
    # Try to load from existing files
    available_files = {}
    
    if course_data_dir.exists():
        # Files to permanently exclude from the dropdown (support files)
        excluded_files = {
            "gen_ed_courses.json",
            "ie_core_courses.json", 
            # REMOVED: "technical_electives.json" - no longer used
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
                    # REMOVED: 'technical_electives' in data or
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
                    # REMOVED: 'technical_electives' in data or
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

def create_unified_course_lookup(data):
    """
    Create a unified lookup dictionary from course data.
    FIXED: Now properly handles technical_electives attribute from B-IE files.
    """
    lookup = {}
    
    # Add IE courses (FIXED: Separate technical electives from core)
    if 'industrial_engineering_courses' in data:
        for course in data['industrial_engineering_courses']:
            # FIXED: Check technical_electives attribute
            if course.get('technical_electives', False):
                lookup[course['code']] = {
                    **course,
                    'category': 'technical_electives',
                    'subcategory': 'technical'
                }
            else:
                lookup[course['code']] = {
                    **course,
                    'category': 'ie_core',
                    'subcategory': 'core'
                }
    
    # Add other related courses (always IE core)
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
    
    # REMOVED: No longer loading from separate technical electives file
    
    return lookup

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
            'entrepreneurship': [],
            'language_communication': [],
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

def generate_course_summary_report(data):
    """
    Generate a comprehensive summary report of course data.
    FIXED: Now includes proper technical electives information.
    """
    report_lines = []
    
    # Header
    report_lines.append("="*60)
    report_lines.append("COURSE DATA SUMMARY REPORT (FIXED)")
    report_lines.append("="*60)
    report_lines.append("")
    
    # Statistics
    stats = get_course_statistics(data)
    report_lines.append("COURSE STATISTICS:")
    report_lines.append("-"*30)
    report_lines.append(f"IE Core Courses:       {stats['ie_courses']}")
    report_lines.append(f"Technical Electives:   {stats['technical_electives']} (FIXED: from B-IE files)")
    report_lines.append(f"Gen-Ed Courses:        {stats['gen_ed_courses']}")
    report_lines.append(f"Other Related:         {stats['other_courses']}")
    report_lines.append(f"TOTAL COURSES:         {stats['total_courses']}")
    report_lines.append("")
    
    # Technical Electives Details
    tech_electives = get_technical_electives_from_data(data)
    if tech_electives:
        report_lines.append("TECHNICAL ELECTIVES (FIXED):")
        report_lines.append("-"*30)
        for course in tech_electives:
            report_lines.append(f"  {course['code']} - {course['name']}")
        report_lines.append("")
    
    # Distribution Analysis
    distribution = analyze_course_distribution(data)
    report_lines.append("COURSE DISTRIBUTION:")
    report_lines.append("-"*30)
    report_lines.append(f"IE Core:               {len(distribution['ie_core'])} courses")
    report_lines.append(f"Technical Electives:   {len(distribution['technical_electives'])} courses (FIXED)")
    report_lines.append(f"Other Related:         {len(distribution['other_related'])} courses")
    
    # Gen-Ed breakdown
    report_lines.append("\nGen-Ed Categories:")
    for category, courses in distribution['gen_ed'].items():
        category_display = category.replace('_', ' ').title()
        report_lines.append(f"  {category_display:<20} {len(courses)} courses")
    
    # Validation
    is_valid, validation_msg = validate_course_data_structure(data)
    report_lines.append("")
    report_lines.append("DATA VALIDATION:")
    report_lines.append("-"*30)
    if is_valid:
        report_lines.append("✅ Course data structure is valid")
    else:
        report_lines.append(f"❌ Validation error: {validation_msg}")
    
    report_lines.append("")
    report_lines.append("TECHNICAL ELECTIVES FIX STATUS:")
    report_lines.append("-"*30)
    report_lines.append("✅ Technical electives now loaded from B-IE files")
    report_lines.append("✅ Using technical_electives: true attribute")
    report_lines.append("✅ No longer dependent on separate technical_electives.json")
    
    return "\n".join(report_lines)
