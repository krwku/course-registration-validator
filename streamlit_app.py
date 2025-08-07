import streamlit as st
import json
import sys
from pathlib import Path
import tempfile
import os
import traceback
import importlib
import sys

# Force reload the course data loader module
if 'utils.course_data_loader' in sys.modules:
    importlib.reload(sys.modules['utils.course_data_loader'])
    
# Add modules to path
sys.path.append(str(Path(__file__).parent))

# Import our modules
from utils.pdf_processor import extract_text_from_pdf_bytes
from utils.course_data_loader import load_comprehensive_course_data
from utils.pdf_extractor import PDFExtractor
from utils.validation_adapter import ValidationAdapter
from validator import CourseRegistrationValidator

# Import the fixed generators
from utils.excel_generator import create_smart_registration_excel, classify_course, load_course_categories

def safe_course_classification():
    """Safely load course categories with error handling."""
    try:
        return load_course_categories()
    except Exception as e:
        st.error(f"Error loading course categories: {e}")
        return {
            "ie_core": {},
            "technical_electives": {},
            "gen_ed": {
                "wellness": {},
                "entrepreneurship": {},
                "language_communication": {},
                "thai_citizen_global": {},
                "aesthetics": {}
            },
            "all_courses": {}
        }

def analyze_unidentified_courses(semesters, course_categories):
    """Analyze transcript for unidentified courses."""
    unidentified_courses = []
    
    try:
        for semester in semesters:
            for course in semester.get("courses", []):
                course_code = course.get("code", "")
                course_name = course.get("name", "")
                
                if course_code:
                    category, subcategory, is_identified = classify_course(
                        course_code, 
                        course_name,
                        course_categories
                    )
                    
                    if not is_identified:
                        unidentified_courses.append({
                            "code": course_code,
                            "name": course_name,
                            "semester": semester.get("semester", ""),
                            "credits": course.get("credits", 0),
                            "grade": course.get("grade", "")
                        })
    except Exception as e:
        st.error(f"Error analyzing courses: {e}")
    
    return unidentified_courses

def calculate_credit_summary(semesters, course_categories):
    """Calculate credit summary by category."""
    try:
        summary = {
            "ie_core": 0,
            "wellness": 0,
            "entrepreneurship": 0,
            "language_communication": 0,
            "thai_citizen_global": 0,
            "aesthetics": 0,
            "technical_electives": 0,
            "free_electives": 0,
            "unidentified": 0
        }
        
        for semester in semesters:
            for course in semester.get("courses", []):
                course_code = course.get("code", "")
                course_name = course.get("name", "")
                grade = course.get("grade", "")
                credits = course.get("credits", 0)
                
                # Only count completed courses
                if grade in ["A", "B+", "B", "C+", "C", "D+", "D", "P"]:
                    category, subcategory, is_identified = classify_course(
                        course_code, course_name, course_categories
                    )
                    
                    if category == "ie_core":
                        summary["ie_core"] += credits
                    elif category == "gen_ed":
                        summary[subcategory] += credits
                    elif category == "technical_electives":
                        summary["technical_electives"] += credits
                    elif category == "unidentified":
                        summary["unidentified"] += credits
                    else:
                        summary["free_electives"] += credits
        
        return summary
    except Exception as e:
        st.error(f"Error calculating credit summary: {e}")
        return {}

def load_course_categories_for_flow():
    """Load course categories for the flow generator."""
    course_data_dir = Path(__file__).parent / "course_data"
    
    categories = {
        "ie_core": {},
        "technical_electives": {},
        "gen_ed": {
            "wellness": {},
            "entrepreneurship": {},
            "language_communication": {},
            "thai_citizen_global": {},
            "aesthetics": {}
        },
        "all_courses": {}
    }
    
    # Load IE Core courses
    for ie_file in ["B-IE-2560.json", "B-IE-2565.json"]:
        ie_path = course_data_dir / ie_file
        if ie_path.exists():
            with open(ie_path, 'r', encoding='utf-8') as f:
                ie_data = json.load(f)
                for course in ie_data.get("industrial_engineering_courses", []):
                    categories["ie_core"][course["code"]] = course
                    categories["all_courses"][course["code"]] = course
                for course in ie_data.get("other_related_courses", []):
                    categories["ie_core"][course["code"]] = course  
                    categories["all_courses"][course["code"]] = course
    
    # Load Technical Electives
    tech_file = course_data_dir / "technical_electives.json"
    if tech_file.exists():
        with open(tech_file, 'r', encoding='utf-8') as f:
            tech_data = json.load(f)
            for course in tech_data.get("technical_electives", []):
                categories["technical_electives"][course["code"]] = course
                categories["all_courses"][course["code"]] = course
    
    # Load Gen-Ed courses
    gen_ed_file = course_data_dir / "gen_ed_courses.json"
    if gen_ed_file.exists():
        with open(gen_ed_file, 'r', encoding='utf-8') as f:
            gen_ed_data = json.load(f)
            gen_ed_courses = gen_ed_data.get("gen_ed_courses", {})
            for subcategory in ["wellness", "entrepreneurship", "language_communication", "thai_citizen_global", "aesthetics"]:
                for course in gen_ed_courses.get(subcategory, []):
                    categories["gen_ed"][subcategory][course["code"]] = course
                    categories["all_courses"][course["code"]] = course
    
    return categories

def load_curriculum_template_for_flow(catalog_name):
    """Load curriculum template based on catalog name."""
    course_data_dir = Path(__file__).parent / "course_data"
    templates_dir = course_data_dir / "templates"
    
    # Determine which template to load
    if "2560" in catalog_name:
        template_file = templates_dir / "curriculum_template_2560.json"
    elif "2565" in catalog_name:
        template_file = templates_dir / "curriculum_template_2565.json"
    else:
        template_file = templates_dir / "curriculum_template_2565.json"  # Default
    
    if template_file.exists():
        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            st.error(f"Error loading template: {e}")
    
    return None

def classify_course_for_flow(course_code, course_name="", course_categories=None):
    """Classify course into appropriate category."""
    if course_categories is None:
        course_categories = load_course_categories_for_flow()
    
    code = course_code.upper()
    
    if code in course_categories["ie_core"]:
        return ("ie_core", "core", True)
    elif code in course_categories["technical_electives"]:
        return ("technical_electives", "technical", True)
    else:
        for subcategory, courses in course_categories["gen_ed"].items():
            if code in courses:
                return ("gen_ed", subcategory, True)
    
    return ("unidentified", "unknown", False)

def analyze_student_progress_fixed(semesters, template, course_categories):
    """FIXED: Analyze student's actual progress against the curriculum template with much more lenient deviation detection."""
    # Organize student courses by completion status
    completed_courses = {}
    failed_courses = {}
    withdrawn_courses = {}
    current_courses = {}
    
    # Find the earliest academic year to establish baseline
    earliest_year = None
    semester_years = []
    
    for semester in semesters:
        year = semester.get("year_int", 0)
        if year and year > 1900:  # Valid calendar year
            semester_years.append(year)
            if earliest_year is None or year < earliest_year:
                earliest_year = year
    
    # Debug information
    print(f"Debug: Earliest year found: {earliest_year}")
    print(f"Debug: All semester years: {sorted(set(semester_years))}")
    
    # Calculate academic years for each semester
    for semester in semesters:
        calendar_year = semester.get("year_int", 0)
        semester_type = semester.get("semester_type", "")
        
        # Calculate academic year
        academic_year = 1  # Default to year 1
        if earliest_year and calendar_year and calendar_year > 1900:
            academic_year = calendar_year - earliest_year + 1
        
        # Debug information for each semester
        print(f"Debug: {semester.get('semester', 'Unknown')}: Calendar={calendar_year}, Academic={academic_year}, Type={semester_type}")
        
        for course in semester.get("courses", []):
            code = course.get("code", "")
            grade = course.get("grade", "")
            
            # Normalize semester type for comparison
            normalized_semester_type = semester_type
            if normalized_semester_type not in ["First", "Second", "Summer"]:
                # Try to extract from semester name
                semester_name = semester.get("semester", "").lower()
                if "first" in semester_name:
                    normalized_semester_type = "First"
                elif "second" in semester_name:
                    normalized_semester_type = "Second" 
                elif "summer" in semester_name:
                    normalized_semester_type = "Summer"
            
            if grade in ["A", "B+", "B", "C+", "C", "D+", "D", "P"]:
                completed_courses[code] = {
                    "grade": grade,
                    "semester": semester.get("semester", ""),
                    "credits": course.get("credits", 0),
                    "calendar_year": calendar_year,
                    "academic_year": academic_year,
                    "semester_type": normalized_semester_type,
                    "original_semester_type": semester_type  # Keep original for debugging
                }
            elif grade == "F":
                failed_courses[code] = {"grade": grade, "semester": semester.get("semester", "")}
            elif grade == "W":
                withdrawn_courses[code] = {"grade": grade, "semester": semester.get("semester", "")}
            elif grade in ["N", ""]:
                current_courses[code] = {"grade": grade, "semester": semester.get("semester", "")}
    
    # MUCH MORE LENIENT DEVIATION ANALYSIS
    deviations = []
    
    for year_key, year_data in template.get("core_curriculum", {}).items():
        expected_year = int(year_key.split("_")[1])
        
        for semester_key, course_codes in year_data.items():
            expected_semester = "First" if "first" in semester_key else "Second"
            
            for course_code in course_codes:
                if course_code in completed_courses:
                    actual_academic_year = completed_courses[course_code]["academic_year"]
                    actual_calendar_year = completed_courses[course_code]["calendar_year"]
                    actual_semester = completed_courses[course_code]["semester_type"]
                    
                    # MUCH MORE LENIENT deviation detection
                    year_diff = abs(actual_academic_year - expected_year)
                    semester_different = actual_semester != expected_semester
                    
                    # Only flag as significant deviation if:
                    # 1. Year is off by MORE than 2 years (very unusual)
                    # 2. OR it's taken in Summer when not expected (but only mark as low severity)
                    should_flag = False
                    severity = "low"
                    
                    if year_diff > 2:
                        should_flag = True
                        severity = "high"
                    elif year_diff == 2 and semester_different:
                        should_flag = True 
                        severity = "moderate"
                    elif year_diff <= 1 and actual_semester == "Summer" and expected_semester != "Summer":
                        should_flag = True
                        severity = "low"
                    
                    # Debug information for each course
                    print(f"Debug: {course_code} - Expected: Year {expected_year} {expected_semester}, Actual: Year {actual_academic_year} {actual_semester}, Diff: {year_diff}, Flag: {should_flag}")
                    
                    if should_flag:
                        deviations.append({
                            "course_code": course_code,
                            "expected": f"Year {expected_year} {expected_semester}",
                            "actual": f"Year {actual_academic_year} {actual_semester} ({actual_calendar_year})",
                            "severity": severity,
                            "year_diff": year_diff
                        })

    # Analyze elective courses (unchanged)
    elective_analysis = {}
    for category, required_credits in template.get("elective_requirements", {}).items():
        elective_analysis[category] = {"required": required_credits, "completed": 0, "courses": []}
    
    # Classify elective courses
    for semester in semesters:
        for course in semester.get("courses", []):
            code = course.get("code", "")
            grade = course.get("grade", "")
            
            if grade not in ["A", "B+", "B", "C+", "C", "D+", "D", "P"]:
                continue
            
            # Check if it's in the core curriculum
            is_core = False
            for year_data in template.get("core_curriculum", {}).values():
                for course_codes in year_data.values():
                    if code in course_codes:
                        is_core = True
                        break
                if is_core:
                    break
            
            if not is_core:
                category, subcategory, is_identified = classify_course_for_flow(code, course.get("name", ""), course_categories)
                
                elective_key = None
                if category == "technical_electives":
                    elective_key = "technical_electives"
                elif category == "gen_ed":
                    elective_key = subcategory
                else:
                    elective_key = "free_electives"
                
                if elective_key and elective_key in elective_analysis:
                    elective_analysis[elective_key]["completed"] += course.get("credits", 0)
                    elective_analysis[elective_key]["courses"].append({
                        "code": code,
                        "name": course.get("name", ""),
                        "credits": course.get("credits", 0),
                        "semester": semester.get("semester", ""),
                        "is_identified": is_identified
                    })
    
    # Debug summary
    print(f"Debug: Total deviations found: {len(deviations)}")
    for dev in deviations:
        print(f"Debug: Deviation - {dev['course_code']}: {dev['severity']} ({dev.get('year_diff', 0)} year diff)")
    
    return {
        "completed_courses": completed_courses,
        "failed_courses": failed_courses,
        "withdrawn_courses": withdrawn_courses,
        "current_courses": current_courses,
        "deviations": deviations,
        "elective_analysis": elective_analysis
    }

def create_fixed_template_flow_html(student_info, semesters, validation_results, selected_course_data=None):
    """Create template-based HTML flow chart with FIXED deviation detection."""
    
    course_categories = load_course_categories_for_flow()
    
    # Load curriculum template
    catalog_filename = selected_course_data.get('filename', 'B-IE-2565.json') if selected_course_data else 'B-IE-2565.json'
    template = load_curriculum_template_for_flow(catalog_filename)
    
    if not template:
        return "Error: Could not load curriculum template", 1
    
    # Use the FIXED analysis function
    analysis = analyze_student_progress_fixed(semesters, template, course_categories)
    
    # CSS styles with improved deviation indicators
    css_styles = """
    <style>
        .curriculum-container {
            font-family: 'Segoe UI', sans-serif;
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        .template-info {
            background: #e8f5e8;
            padding: 15px;
            margin-bottom: 20px;
            border-radius: 5px;
            text-align: center;
        }
        
        .deviation-alert {
            background: #fff3cd;
            border: 1px solid #f39c12;
            padding: 15px;
            margin-bottom: 20px;
            border-radius: 5px;
            border-left: 4px solid #f39c12;
        }
        
        .deviation-alert.low {
            background: #e8f5e8;
            border-color: #27ae60;
            border-left-color: #27ae60;
        }
        
        .year-container {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .year-column {
            background: white;
            border-radius: 10px;
            padding: 15px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        .year-header {
            text-align: center;
            font-size: 18px;
            font-weight: bold;
            color: white;
            margin-bottom: 15px;
            padding: 10px;
            background: linear-gradient(45deg, #3498db, #2980b9);
            border-radius: 5px;
        }
        
        .semester-section {
            margin-bottom: 20px;
        }
        
        .semester-header {
            font-size: 14px;
            font-weight: bold;
            color: #34495e;
            text-align: center;
            margin-bottom: 10px;
            padding: 8px;
            background: #ecf0f1;
            border-radius: 5px;
        }
        
        .course-box {
            margin-bottom: 8px;
            padding: 8px;
            border-radius: 5px;
            border: 2px solid #bdc3c7;
            background: white;
            transition: all 0.3s ease;
            cursor: pointer;
            position: relative;
        }
        
        .course-box:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }
        
        .course-completed {
            background: linear-gradient(135deg, #2ecc71, #27ae60);
            color: white;
            border-color: #27ae60;
        }
        
        .course-failed {
            background: linear-gradient(135deg, #e74c3c, #c0392b);
            color: white;
            border-color: #c0392b;
        }
        
        .course-withdrawn {
            background: linear-gradient(135deg, #f39c12, #e67e22);
            color: white;
            border-color: #e67e22;
        }
        
        .course-current {
            background: linear-gradient(135deg, #3498db, #2980b9);
            color: white;
            border-color: #2980b9;
        }
        
        .course-deviation {
            border: 3px solid #f39c12 !important;
        }
        
        .course-deviation.high {
            border-color: #e74c3c !important;
        }
        
        .course-deviation.low {
            border-color: #27ae60 !important;
        }
        
        .course-deviation::before {
            content: '⚠️';
            position: absolute;
            top: -5px;
            right: -5px;
            border-radius: 50%;
            width: 18px;
            height: 18px;
            font-size: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
        }
        
        .course-deviation.high::before {
            background: #e74c3c;
            content: '❌';
        }
        
        .course-deviation.low::before {
            background: #27ae60;
            content: '✓';
        }
        
        .deviation-tooltip {
            display: none;
            position: absolute;
            top: -60px;
            left: 50%;
            transform: translateX(-50%);
            background: #2c3e50;
            color: white;
            padding: 8px 12px;
            border-radius: 6px;
            font-size: 11px;
            z-index: 1000;
            max-width: 300px;
            white-space: normal;
            text-align: center;
        }
        
        .course-deviation:hover .deviation-tooltip {
            display: block;
        }
        
        .deviation-tooltip::after {
            content: '';
            position: absolute;
            top: 100%;
            left: 50%;
            margin-left: -5px;
            border-width: 5px;
            border-style: solid;
            border-color: #2c3e50 transparent transparent transparent;
        }
        
        .course-code { font-size: 11px; font-weight: bold; margin-bottom: 4px; }
        .course-name { font-size: 10px; line-height: 1.2; margin-bottom: 4px; }
        .course-info { font-size: 9px; opacity: 0.8; }
        
        .legend {
            display: flex;
            justify-content: center;
            flex-wrap: wrap;
            gap: 15px;
            margin: 20px 0;
            padding: 15px;
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .legend-item {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 12px;
        }
        
        .legend-color {
            width: 16px;
            height: 16px;
            border-radius: 3px;
            border: 1px solid #bdc3c7;
        }
        
        .electives-section {
            margin-top: 30px;
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        .electives-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        
        .elective-category {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 15px;
        }
        
        .category-header {
            font-size: 14px;
            font-weight: bold;
            color: white;
            margin-bottom: 10px;
            text-align: center;
            padding: 8px;
            border-radius: 5px;
        }
        
        .category-header.wellness { background: linear-gradient(45deg, #e74c3c, #c0392b); }
        .category-header.entrepreneurship { background: linear-gradient(45deg, #f39c12, #e67e22); }
        .category-header.language_communication { background: linear-gradient(45deg, #3498db, #2980b9); }
        .category-header.thai_citizen_global { background: linear-gradient(45deg, #9b59b6, #8e44ad); }
        .category-header.aesthetics { background: linear-gradient(45deg, #1abc9c, #16a085); }
        .category-header.technical_electives { background: linear-gradient(45deg, #34495e, #2c3e50); }
        .category-header.free_electives { background: linear-gradient(45deg, #95a5a6, #7f8c8d); }
        
        .progress-bar {
            width: 100%;
            height: 20px;
            background: #ecf0f1;
            border-radius: 10px;
            overflow: hidden;
            margin: 10px 0;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(45deg, #2ecc71, #27ae60);
            transition: width 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 12px;
            font-weight: bold;
        }
        
        .stats-summary {
            background: white;
            border-radius: 10px;
            padding: 20px;
            margin-top: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
    </style>
    """
    
    # Generate HTML
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>FIXED Template-Based IE Curriculum Flow Chart</title>
        <meta charset="utf-8">
        {css_styles}
    </head>
    <body>
        <div class="curriculum-container">
            <div class="header">
                <h1>Industrial Engineering Curriculum Template Flow Chart (FIXED)</h1>
                <div class="template-info">
                    <strong>Template:</strong> {template.get('curriculum_name', 'Unknown')} | 
                    <strong>Student:</strong> {student_info.get('name', 'N/A')} ({student_info.get('id', 'N/A')})
                </div>
            </div>
    """
    
    # Improved deviation alerts with severity-based messaging
    significant_deviations = [d for d in analysis['deviations'] if d['severity'] in ['moderate', 'high']]
    minor_deviations = [d for d in analysis['deviations'] if d['severity'] == 'low']
    
    if significant_deviations:
        html_content += f"""
        <div class="deviation-alert">
            <h4>📅 Significant Schedule Variations ({len(significant_deviations)} courses)</h4>
            <p><strong>Note:</strong> Some courses were taken significantly earlier/later than the standard timeline (>2 year difference). This may indicate advanced placement, repeated courses, or alternative academic planning.</p>
        </div>
        """
    elif minor_deviations:
        html_content += f"""
        <div class="deviation-alert low">
            <h4>✅ Minor Schedule Variations ({len(minor_deviations)} courses)</h4>
            <p><strong>Note:</strong> Some courses were taken in different semesters but within normal timing (±1-2 years). This is very common and usually due to course availability or personal scheduling preferences.</p>
        </div>
        """
    else:
        html_content += """
        <div class="deviation-alert low">
            <h4>🎯 Perfect Schedule Alignment</h4>
            <p><strong>Excellent!</strong> All courses were taken within the expected timeline according to the curriculum template.</p>
        </div>
        """
    
    # Add legend with updated information
    html_content += """
    <div class="legend">
        <div class="legend-item">
            <div class="legend-color" style="background: linear-gradient(135deg, #2ecc71, #27ae60);"></div>
            <span>Completed</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background: linear-gradient(135deg, #e74c3c, #c0392b);"></div>
            <span>Failed</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background: linear-gradient(135deg, #f39c12, #e67e22);"></div>
            <span>Withdrawn</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background: linear-gradient(135deg, #3498db, #2980b9);"></div>
            <span>Current</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background: white;"></div>
            <span>Not Taken</span>
        </div>
        <div class="legend-item">
            <span style="color: #27ae60; font-weight: bold;">✓</span>
            <span>Minor Timing Variation (Normal)</span>
        </div>
        <div class="legend-item">
            <span style="color: #f39c12; font-weight: bold;">⚠️</span>
            <span>Moderate Variation</span>
        </div>
        <div class="legend-item">
            <span style="color: #e74c3c; font-weight: bold;">❌</span>
            <span>Significant Variation (>2 years)</span>
        </div>
    </div>
    """
    
    # Generate curriculum grid based on template
    html_content += '<div class="year-container">'
    
    for year_key in sorted(template.get('core_curriculum', {}).keys()):
        year_num = year_key.split('_')[1]
        year_data = template['core_curriculum'][year_key]
        
        html_content += f'''
        <div class="year-column">
            <div class="year-header">Year {year_num}</div>
        '''
        
        for semester_key in ['first_semester', 'second_semester']:
            if semester_key not in year_data:
                continue
                
            semester_name = 'First Semester' if semester_key == 'first_semester' else 'Second Semester'
            course_codes = year_data[semester_key]
            
            html_content += f'''
            <div class="semester-section">
                <div class="semester-header">{semester_name}</div>
            '''
            
            for course_code in course_codes:
                # Get course details
                course_name = "Unknown Course"
                credits = 0
                
                if course_code in course_categories["all_courses"]:
                    course_info = course_categories["all_courses"][course_code]
                    course_name = course_info.get("name", "Unknown Course")
                    credits_str = course_info.get("credits", "0")
                    if isinstance(credits_str, str) and "(" in credits_str:
                        credits = int(credits_str.split("(")[0])
                    else:
                        credits = int(credits_str) if str(credits_str).isdigit() else 0
                
                # Determine status and deviations
                css_class = "course-box"
                status_info = "Not taken"
                deviation_info = ""
                
                # Check for deviations with improved tooltip
                deviation = next((d for d in analysis['deviations'] if d['course_code'] == course_code), None)
                if deviation:
                    css_class += f" course-deviation {deviation['severity']}"
                    severity_text = {
                        'low': 'Minor timing variation (within ±1-2 years, very normal)',
                        'moderate': 'Moderate schedule variation (±2 years)', 
                        'high': 'Significant timing difference (>2 years from expected)'
                    }.get(deviation['severity'], 'Schedule variation')
                    
                    deviation_info = f'<div class="deviation-tooltip">{severity_text}<br>Expected: {deviation["expected"]}<br>Actually taken: {deviation["actual"]}</div>'
                
                if course_code in analysis['completed_courses']:
                    css_class += " course-completed"
                    grade = analysis['completed_courses'][course_code]['grade']
                    status_info = f"Grade: {grade}"
                elif course_code in analysis['failed_courses']:
                    css_class += " course-failed"
                    status_info = "Grade: F"
                elif course_code in analysis['withdrawn_courses']:
                    css_class += " course-withdrawn"
                    status_info = "Withdrawn"
                elif course_code in analysis['current_courses']:
                    css_class += " course-current"
                    grade = analysis['current_courses'][course_code]['grade']
                    status_info = f"Current: {grade if grade else 'In Progress'}"
                
                html_content += f'''
                <div class="{css_class}">
                    {deviation_info}
                    <div class="course-code">{course_code}</div>
                    <div class="course-name">{course_name}</div>
                    <div class="course-info">{credits} credits • {status_info}</div>
                </div>
                '''
            
            html_content += '</div>'  # End semester-section
        
        html_content += '</div>'  # End year-column
    
    html_content += '</div>'  # End year-container
    
    # Add electives section (condensed for brevity)
    html_content += '''
    <div class="electives-section">
        <h2 style="text-align: center; color: #2c3e50; margin-bottom: 20px;">Elective Requirements Progress</h2>
        <div class="electives-grid">
    '''
    
    unidentified_count = 0
    
    for elective_key, required_credits in template.get('elective_requirements', {}).items():
        analysis_data = analysis['elective_analysis'].get(elective_key, {'required': required_credits, 'completed': 0, 'courses': []})
        completed_credits = analysis_data['completed']
        courses = analysis_data['courses']
        
        # Calculate progress
        progress_percentage = min((completed_credits / required_credits) * 100, 100) if required_credits > 0 else 0
        
        # Format category name
        category_display = elective_key.replace('_', ' ').title()
        if elective_key == 'thai_citizen_global':
            category_display = 'Thai Citizen & Global'
        elif elective_key == 'language_communication':
            category_display = 'Language & Communication'
        
        html_content += f'''
        <div class="elective-category">
            <div class="category-header {elective_key}">{category_display}</div>
            <div style="text-align: center; margin-bottom: 10px;">
                <strong>Progress: {completed_credits}/{required_credits} credits</strong>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: {progress_percentage}%">
                    {progress_percentage:.0f}%
                </div>
            </div>
        '''
        
        if courses:
            for course in courses:
                if not course.get('is_identified', True):
                    unidentified_count += 1
                
                html_content += f'''
                <div class="course-box course-completed" style="margin-bottom: 5px;">
                    <div class="course-code">{course["code"]}</div>
                    <div class="course-name">{course["name"]}</div>
                    <div class="course-info">{course["credits"]} credits • {course["semester"]}</div>
                </div>
                '''
        else:
            html_content += '<div style="text-align: center; color: #7f8c8d; font-style: italic;">No courses completed yet</div>'
        
        html_content += '</div>'  # End elective-category
    
    html_content += '</div></div>'  # End grids
    
    # Add progress summary with improved deviation information
    total_template_courses = sum(len(courses) for year_data in template.get('core_curriculum', {}).values() 
                               for courses in year_data.values())
    completed_template_courses = len([c for c in analysis['completed_courses'] 
                                    if any(c in courses for year_data in template.get('core_curriculum', {}).values() 
                                          for courses in year_data.values())])
    
    html_content += f'''
    <div class="stats-summary">
        <h3 style="text-align: center; color: #2c3e50;">📊 FIXED Analysis - Overall Progress Summary</h3>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-top: 15px;">
            <div style="text-align: center; background: #f8f9fa; padding: 15px; border-radius: 8px;">
                <div style="font-size: 24px; font-weight: bold; color: #2c3e50;">{completed_template_courses}/{total_template_courses}</div>
                <div style="font-size: 12px; color: #7f8c8d;">Core Courses Completed</div>
            </div>
            <div style="text-align: center; background: #f8f9fa; padding: 15px; border-radius: 8px;">
                <div style="font-size: 24px; font-weight: bold; color: #f39c12;">{len(significant_deviations)}</div>
                <div style="font-size: 12px; color: #7f8c8d;">Significant Variations (>2 years)</div>
            </div>
            <div style="text-align: center; background: #f8f9fa; padding: 15px; border-radius: 8px;">
                <div style="font-size: 24px; font-weight: bold; color: #27ae60;">{len(minor_deviations)}</div>
                <div style="font-size: 12px; color: #7f8c8d;">Minor Variations (Normal)</div>
            </div>
            <div style="text-align: center; background: #f8f9fa; padding: 15px; border-radius: 8px;">
                <div style="font-size: 24px; font-weight: bold; color: #9b59b6;">{unidentified_count}</div>
                <div style="font-size: 12px; color: #7f8c8d;">New Courses</div>
            </div>
        </div>
        
        <div style="margin-top: 20px; padding: 15px; background: #e8f5e8; border-radius: 8px; text-align: center;">
            <h4 style="margin: 0 0 10px 0; color: #27ae60;">📋 FIXED Schedule Analysis Summary</h4>
            <p style="margin: 0; font-size: 14px; color: #2c3e50;">
                <strong>ISSUE RESOLVED:</strong> The deviation detection is now much more lenient and realistic. 
                Minor timing variations (±1-2 years) are normal and expected due to course availability, prerequisites, or personal scheduling.
                <br><br><strong>Green ✓:</strong> Normal timing variations (±1-2 years) - Very common and not concerning
                <br><strong>Orange ⚠️:</strong> Moderate variations (±2 years exactly) - Still within reasonable range
                <br><strong>Red ❌:</strong> Significant variations (>2 years difference) - May warrant review but still valid
            </p>
        </div>
    </div>
    '''
    
    html_content += '''
        </div>
    </body>
    </html>
    '''
    
    return html_content, unidentified_count

def main():
    st.set_page_config(
        page_title="KU IE Course Validator", 
        page_icon="🎓",
        layout="wide"
    )
    
    st.title("🎓 KU Industrial Engineering Course Validator")
    st.markdown("*Smart Registration Planning with Advanced Course Detection*")
    st.markdown("*Created for Raphin P. - FIXED Schedule Deviation Detection*")
    
    # Initialize session state
    if 'student_info' not in st.session_state:
        st.session_state.student_info = {}
    if 'semesters' not in st.session_state:
        st.session_state.semesters = []
    if 'validation_results' not in st.session_state:
        st.session_state.validation_results = []
    if 'selected_course_data' not in st.session_state:
        st.session_state.selected_course_data = None
    if 'processing_complete' not in st.session_state:
        st.session_state.processing_complete = False
    if 'unidentified_count' not in st.session_state:
        st.session_state.unidentified_count = 0
    if 'course_categories' not in st.session_state:
        st.session_state.course_categories = None
    
    # Load course data
    try:
        available_course_data = load_comprehensive_course_data()
    except Exception as e:
        st.error(f"Error loading course data: {e}")
        available_course_data = {}
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        if available_course_data:
            selected_catalog = st.selectbox(
                "📚 Select Course Catalog",
                options=list(available_course_data.keys()),
                help="Choose the course catalog for validation"
            )
            
            if selected_catalog:
                st.session_state.selected_course_data = available_course_data[selected_catalog]
                st.success(f"✅ Using: {available_course_data[selected_catalog]['filename']}")
                
                # Load course categories for classification
                if st.session_state.course_categories is None:
                    with st.spinner("Loading course classification system..."):
                        st.session_state.course_categories = safe_course_classification()
        else:
            st.error("❌ No course data files found")
            st.stop()
        
        st.divider()
        
        st.header("📁 Upload Transcript")
        pdf_file = st.file_uploader(
            "Upload PDF Transcript", 
            type=['pdf'],
            help="Upload student transcript PDF"
        )
        
        if pdf_file is not None:
            st.info(f"📄 File: {pdf_file.name}")
            st.info(f"📊 Size: {len(pdf_file.getvalue()) / 1024:.1f} KB")
            
            # Reset processing when new file is uploaded
            if 'last_pdf_name' not in st.session_state or st.session_state.last_pdf_name != pdf_file.name:
                st.session_state.processing_complete = False
                st.session_state.student_info = {}
                st.session_state.semesters = []
                st.session_state.validation_results = []
                st.session_state.unidentified_count = 0
                st.session_state.last_pdf_name = pdf_file.name
    
    # Main processing
    if pdf_file is not None and st.session_state.selected_course_data is not None:
        
        if not st.session_state.processing_complete:
            with st.spinner("🔄 Processing PDF and creating advanced course analysis..."):
                
                try:
                    pdf_bytes = pdf_file.getvalue()
                    
                    # Extract text from PDF
                    extracted_text = extract_text_from_pdf_bytes(pdf_bytes)
                    
                    if not extracted_text:
                        st.error("❌ No text extracted from PDF. Please ensure the PDF contains readable text.")
                        st.stop()
                    
                    # Process the extracted text
                    extractor = PDFExtractor()
                    student_info, semesters, _ = extractor.process_pdf(None, extracted_text)
                    
                    if not student_info or not semesters:
                        st.error("❌ Failed to process transcript data. Please check if the PDF format is supported.")
                        st.stop()
                    
                    # Validate data
                    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
                        json.dump(st.session_state.selected_course_data['data'], tmp_file)
                        tmp_path = tmp_file.name
                    
                    try:
                        validator = CourseRegistrationValidator(tmp_path)
                        passed_courses_history = validator.build_passed_courses_history(semesters)
                        
                        all_results = []
                        
                        # Validate each semester
                        for i, semester in enumerate(semesters):
                            # Check credit limit
                            credit_valid, credit_reason = validator.validate_credit_limit(semester)
                            if not credit_valid:
                                all_results.append({
                                    "semester": semester.get("semester", ""),
                                    "semester_index": i,
                                    "course_code": "CREDIT_LIMIT", 
                                    "course_name": "Credit Limit Check",
                                    "grade": "N/A",
                                    "is_valid": True,  # Credit limits are warnings, not errors
                                    "reason": credit_reason,
                                    "type": "credit_limit"
                                })
                            
                            # Validate each course
                            for course in semester.get("courses", []):
                                is_valid, reason = validator.validate_course(
                                    course, i, semesters, passed_courses_history, all_results
                                )
                                
                                all_results.append({
                                    "semester": semester.get("semester", ""),
                                    "semester_index": i,
                                    "course_code": course.get("code", ""),
                                    "course_name": course.get("name", ""),
                                    "grade": course.get("grade", ""),
                                    "is_valid": is_valid,
                                    "reason": reason,
                                    "type": "prerequisite"
                                })
                        
                        # Propagate invalidation
                        validator.propagate_invalidation(semesters, all_results)
                    
                    finally:
                        # Clean up temp file
                        if os.path.exists(tmp_path):
                            os.unlink(tmp_path)
                    
                    # Store results
                    st.session_state.student_info = student_info
                    st.session_state.semesters = semesters
                    st.session_state.validation_results = all_results
                    st.session_state.processing_complete = True
                    
                    # Analyze unidentified courses
                    if st.session_state.course_categories:
                        unidentified_courses = analyze_unidentified_courses(
                            semesters, st.session_state.course_categories
                        )
                        st.session_state.unidentified_count = len(unidentified_courses)
                    
                except Exception as e:
                    st.error(f"❌ Error during processing: {e}")
                    with st.expander("Debug Information"):
                        st.code(traceback.format_exc())
                    st.stop()
        
        # Display results
        if st.session_state.processing_complete:
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.header("📋 Student Information")
                st.write(f"**Student ID:** {st.session_state.student_info.get('id', 'Unknown')}")
                st.write(f"**Name:** {st.session_state.student_info.get('name', 'Unknown')}")
                st.write(f"**Field of Study:** {st.session_state.student_info.get('field_of_study', 'Unknown')}")
                
                st.divider()
                st.subheader("📚 Semester Summary")
                for i, sem in enumerate(st.session_state.semesters):
                    semester_name = sem.get('semester', f'Semester {i+1}')
                    course_count = len(sem.get('courses', []))
                    total_credits = sem.get('total_credits', 0)
                    st.write(f"• **{semester_name}:** {course_count} courses, {total_credits} credits")
            
            with col2:
                st.header("✅ Validation Results")
                
                invalid_results = [r for r in st.session_state.validation_results 
                                 if not r.get("is_valid", True) and r.get("course_code") != "CREDIT_LIMIT"]
                total_courses = len([r for r in st.session_state.validation_results 
                                   if r.get("course_code") != "CREDIT_LIMIT"])
                
                if len(invalid_results) == 0:
                    st.success(f"🎉 **Excellent!** All {total_courses} registrations are valid!")
                else:
                    st.error(f"⚠️ **Issues Found:** {len(invalid_results)} invalid registrations")
                
                if invalid_results:
                    with st.expander("❌ Invalid Registrations", expanded=True):
                        for result in invalid_results:
                            st.error(f"**{result.get('semester')}:** {result.get('course_code')} - {result.get('course_name')}")
                            st.write(f"   *Issue:* {result.get('reason')}")
            
            # Check for unidentified courses
            if st.session_state.course_categories:
                unidentified_courses = analyze_unidentified_courses(
                    st.session_state.semesters, 
                    st.session_state.course_categories
                )
                st.session_state.unidentified_count = len(unidentified_courses)
                
                if unidentified_courses:
                    st.info(f"🔍 **Database Expansion Opportunity:** {len(unidentified_courses)} new courses found")
                    with st.expander("🔍 New Courses - Require Classification", expanded=True):
                        for course in unidentified_courses:
                            st.write(f"• **{course['code']}** - {course['name']} ({course['semester']}) - {course['credits']} credits")
                        st.info("💡 These courses are not yet in our classification system and would benefit from being added for more accurate analysis.")
                
                # Show credit summary
                credit_summary = calculate_credit_summary(
                    st.session_state.semesters, 
                    st.session_state.course_categories
                )
                
                if credit_summary:
                    st.divider()
                    st.subheader("📊 Credit Summary by Category")
                    
                    col_cr1, col_cr2, col_cr3 = st.columns(3)
                    
                    with col_cr1:
                        st.metric("IE Core", f"{credit_summary.get('ie_core', 0)}", help="Required: ~110 credits")
                        st.metric("Wellness", f"{credit_summary.get('wellness', 0)}", help="Required: 7 credits")
                        st.metric("Entrepreneurship", f"{credit_summary.get('entrepreneurship', 0)}", help="Required: 3 credits")
                    
                    with col_cr2:
                        st.metric("Language & Communication", f"{credit_summary.get('language_communication', 0)}", help="Required: 15 credits")
                        st.metric("Thai Citizen & Global", f"{credit_summary.get('thai_citizen_global', 0)}", help="Required: 2 credits")
                        st.metric("Aesthetics", f"{credit_summary.get('aesthetics', 0)}", help="Required: 3 credits")
                    
                    with col_cr3:
                        st.metric("Technical Electives", f"{credit_summary.get('technical_electives', 0)}", help="Variable requirement")
                        st.metric("Free Electives", f"{credit_summary.get('free_electives', 0)}", help="Variable requirement")
                        st.metric("Unidentified", f"{credit_summary.get('unidentified', 0)}", help="Courses needing classification", delta_color="off")
            
            # Visualization Options - FIXED SECTION
            st.divider()
            st.header("📊 Advanced Visualizations & Downloads - FIXED VERSION")
            
            # Generate flow chart with FIXED deviation detection
            try:
                with st.spinner("Generating FIXED template-based curriculum flow chart..."):
                    # Use the FIXED function
                    flow_html, flow_unidentified = create_fixed_template_flow_html(
                        st.session_state.student_info,
                        st.session_state.semesters,
                        st.session_state.validation_results,
                        st.session_state.selected_course_data
                    )
                
                st.subheader("🗂️ FIXED Template-Based Curriculum Flow Chart")
                st.markdown("*Shows ideal curriculum template with your actual progress and PROPERLY DETECTED deviations*")
                
                if flow_html and len(flow_html.strip()) > 0:
                    # Escape the backticks in the HTML content for the f-string
                    escaped_flow_html = flow_html.replace('`', '\\`')
                    
                    # Automatically open flow chart in new window
                    js_code = f"""
                    <script>
                    const flowHTML = `{escaped_flow_html}`;
                    const newWindow = window.open('', '_blank');
                    if (newWindow) {{
                        newWindow.document.write(flowHTML);
                        newWindow.document.close();
                    }}
                    </script>
                    """
                    st.components.v1.html(js_code, height=0)
                    
                    # Show success message and provide re-open option
                    col_flow1, col_flow2 = st.columns([2, 1])
                    
                    with col_flow1:
                        st.success("✅ FIXED flow chart automatically opened in new window!")
                        st.info("🔧 **FIXED:** Schedule deviations are now much more lenient and realistic")
                        if flow_unidentified > 0:
                            st.warning(f"⚠️ {flow_unidentified} unidentified courses in flow chart")
                    
                    with col_flow2:
                        # Re-open button for popup blocker cases
                        if st.button("🔄 Re-open FIXED Flow Chart", help="Click if popup was blocked"):
                            js_reopen = f"""
                            <script>
                            const flowHTML = `{escaped_flow_html}`;
                            const newWindow = window.open('', '_blank');
                            newWindow.document.write(flowHTML);
                            newWindow.document.close();
                            </script>
                            """
                            st.components.v1.html(js_reopen, height=0)
                            st.success("✅ FIXED flow chart re-opened!")
                    
                    st.info("💡 **Note:** If the window didn't open automatically, use the 'Re-open' button (popup might be blocked by browser).")
                    
                else:
                    st.error("❌ No HTML content generated for flow chart")
                
            except Exception as e:
                st.error(f"Error generating flow chart: {e}")
                with st.expander("Debug Information"):
                    st.code(traceback.format_exc())
            
            # Download section (rest of the code remains the same)
            st.divider()
            st.header("📥 Download Reports")
            
            col_dl1, col_dl2, col_dl3, col_dl4 = st.columns(4)
            
            with col_dl1:
                # Generate Smart Excel format
                try:
                    with st.spinner("Creating smart Excel analysis..."):
                        excel_bytes, excel_unidentified = create_smart_registration_excel(
                            st.session_state.student_info,
                            st.session_state.semesters,
                            st.session_state.validation_results
                        )
                    
                    if excel_bytes:
                        st.download_button(
                            label="📋 Smart Excel Analysis",
                            data=excel_bytes,
                            file_name=f"KU_IE_smart_analysis_{st.session_state.student_info.get('id', 'unknown')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            help="Comprehensive course analysis with alerts and recommendations",
                            use_container_width=True
                        )
                        
                        if excel_unidentified > 0:
                            st.warning(f"⚠️ {excel_unidentified} unidentified")
                    else:
                        st.error("❌ Excel generation failed")
                        
                except Exception as e:
                    st.error(f"❌ Excel error: {str(e)[:50]}...")
                    with st.expander("Debug"):
                        st.code(str(e))
            
            with col_dl2:
                # HTML Flow Chart download - FIXED VERSION
                try:
                    if 'flow_html' in locals():
                        st.download_button(
                            label="🗂️ FIXED Flow Chart (HTML)",
                            data=flow_html.encode('utf-8'),
                            file_name=f"FIXED_curriculum_flow_{st.session_state.student_info.get('id', 'unknown')}.html",
                            mime="text/html",
                            help="FIXED Interactive semester-based curriculum flow chart with proper deviation detection",
                            use_container_width=True
                        )
                        
                        if 'flow_unidentified' in locals() and flow_unidentified > 0:
                            st.warning(f"⚠️ {flow_unidentified} unidentified")
                    else:
                        # Generate flow chart for download if not already generated
                        flow_html, flow_unidentified = create_fixed_template_flow_html(
                            st.session_state.student_info,
                            st.session_state.semesters,
                            st.session_state.validation_results,
                            st.session_state.selected_course_data
                        )
                        
                        st.download_button(
                            label="🗂️ FIXED Flow Chart (HTML)",
                            data=flow_html.encode('utf-8'),
                            file_name=f"FIXED_curriculum_flow_{st.session_state.student_info.get('id', 'unknown')}.html",
                            mime="text/html",
                            help="FIXED Interactive semester-based curriculum flow chart with proper deviation detection",
                            use_container_width=True
                        )
                        
                        if flow_unidentified > 0:
                            st.warning(f"⚠️ {flow_unidentified} unidentified")
                        
                except Exception as e:
                    st.error(f"❌ Flow chart error: {str(e)[:50]}...")
            
            with col_dl3:
                # Text report
                try:
                    course_data_path = str(Path(__file__).parent / "course_data" / st.session_state.selected_course_data['filename'])
                    validator = CourseRegistrationValidator(course_data_path)
                    report_text = validator.generate_summary_report(
                        st.session_state.student_info, 
                        st.session_state.semesters, 
                        st.session_state.validation_results
                    )
                    
                    st.download_button(
                        label="📄 Validation Report",
                        data=report_text,
                        file_name=f"validation_report_{st.session_state.student_info.get('id', 'unknown')}.txt",
                        mime="text/plain",
                        help="Detailed prerequisite validation report",
                        use_container_width=True
                    )
                except Exception as e:
                    st.error(f"❌ Report error: {str(e)[:50]}...")
            
            with col_dl4:
                # JSON data
                try:
                    export_data = {
                        "student_info": st.session_state.student_info,
                        "semesters": st.session_state.semesters,
                        "validation_results": st.session_state.validation_results,
                        "unidentified_count": st.session_state.unidentified_count,
                        "metadata": {
                            "course_catalog": st.session_state.selected_course_data.get('filename', ''),
                            "generated_timestamp": str(st.session_state.get('processing_timestamp', 'unknown'))
                        }
                    }
                    
                    st.download_button(
                        label="💾 Raw Data (JSON)",
                        data=json.dumps(export_data, indent=2),
                        file_name=f"transcript_data_{st.session_state.student_info.get('id', 'unknown')}.json",
                        mime="application/json",
                        help="Raw extracted and validated data",
                        use_container_width=True
                    )
                except Exception as e:
                    st.error(f"❌ JSON error: {str(e)[:50]}...")
            
            # Process another file
            st.divider()
            if st.button("🔄 Process Another PDF", type="secondary"):
                # Reset all session state
                for key in ['processing_complete', 'student_info', 'semesters', 'validation_results', 
                           'unidentified_count', 'last_pdf_name']:
                    if key in st.session_state:
                        if key in ['student_info', 'semesters', 'validation_results']:
                            st.session_state[key] = [] if key != 'student_info' else {}
                        else:
                            del st.session_state[key]
                st.rerun()
    
    else:
        # Welcome screen
        st.info("📋 **Ready for advanced course validation and visualization with FIXED deviation detection!**")
        
        col_info1, col_info2 = st.columns([1, 1])
        
        with col_info1:
            st.markdown("### 🎯 How to use:")
            st.markdown("""
            1. **Select course catalog** (IE 2560 or 2565)
            2. **Upload PDF transcript** in the sidebar
            3. **Wait for processing** ⚡
            4. **View interactive visualizations** 🗂️
            5. **Download various report formats** 📋
            """)
        
        with col_info2:
            st.markdown("### 🚀 Key Features (FIXED):")
            st.markdown("• **Smart course detection** - Automatically categorizes courses")
            st.markdown("• **FIXED deviation detection** - Realistic timing analysis")
            st.markdown("• **Interactive flow chart** - Visual semester progression")
            st.markdown("• **Comprehensive Excel analysis** - Detailed credit breakdowns")
            st.markdown("• **Prerequisite validation** - Checks course requirements")
            st.markdown("• **Progress tracking** - Credit completion by category")
    
    # Status bar at bottom
    st.divider()
    col_status1, col_status2, col_status3 = st.columns([2, 2, 1])
    
    with col_status1:
        if st.session_state.unidentified_count > 0:
            st.info(f"🔍 Database expansion opportunity: {st.session_state.unidentified_count} new courses found")
        elif st.session_state.processing_complete:
            st.success("✅ All courses successfully classified")
    
    with col_status2:
        if st.session_state.processing_complete:
            invalid_count = len([r for r in st.session_state.validation_results 
                               if not r.get("is_valid", True) and r.get("course_code") != "CREDIT_LIMIT"])
            if invalid_count > 0:
                st.error(f"❌ {invalid_count} validation issues found")
            else:
                st.success("✅ All validations passed")
    
    with col_status3:
        st.markdown("*FIXED for Raphin P.*", 
                   help="Advanced course validation with FIXED deviation detection")

if __name__ == "__main__":
    main()

