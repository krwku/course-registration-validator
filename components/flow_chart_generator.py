import streamlit as st
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import streamlit.components.v1 as components
import re

class FlowChartGenerator:
    """Handles generation and display of curriculum flow charts."""
    
    def __init__(self):
        self.course_categories = None
        self.curriculum_template = None
    
    def load_course_categories_for_flow(self):
        """FUTURE-PROOF VERSION: Load course categories for the flow generator."""
        course_data_dir = Path(__file__).parent.parent / "course_data"
        
        categories = {
            "ie_core": {},
            "technical_electives": {},
            "gen_ed": {
                "wellness": {},
                "wellness_PE": {},
                "entrepreneurship": {},
                "language_communication_thai": {},
                "language_communication_foreigner": {},
                "language_communication_computer": {},
                "thai_citizen_global": {},
                "aesthetics": {}
            },
            "all_courses": {}
        }
        
        # FUTURE-PROOF: Find all B-IE files dynamically
        ie_files = []
        if course_data_dir.exists():
            for json_file in course_data_dir.glob("B-IE-*.json"):
                year_match = re.search(r'B-IE-(\d{4})\.json', json_file.name)
                if year_match:
                    year = int(year_match.group(1))
                    ie_files.append((year, json_file))
        
        # Sort by year (newest first) and process
        ie_files.sort(key=lambda x: x[0], reverse=True)
        
        # Load IE Core courses from available B-IE files
        for year, ie_file in ie_files:
            try:
                with open(ie_file, 'r', encoding='utf-8') as f:
                    ie_data = json.load(f)
                    
                    # Process industrial_engineering_courses
                    for course in ie_data.get("industrial_engineering_courses", []):
                        if course["code"] not in categories["all_courses"]:
                            if course.get("technical_electives", False):
                                categories["technical_electives"][course["code"]] = course
                            else:
                                categories["ie_core"][course["code"]] = course
                            categories["all_courses"][course["code"]] = course
                    
                    # Process other_related_courses
                    for course in ie_data.get("other_related_courses", []):
                        if course["code"] not in categories["all_courses"]:
                            categories["ie_core"][course["code"]] = course  
                            categories["all_courses"][course["code"]] = course
                            
            except Exception as e:
                print(f"Error loading {ie_file}: {e}")
                continue
        
        # Load Gen-Ed courses (unchanged)
        gen_ed_file = course_data_dir / "gen_ed_courses.json"
        if gen_ed_file.exists():
            try:
                with open(gen_ed_file, 'r', encoding='utf-8') as f:
                    gen_ed_data = json.load(f)
                    gen_ed_courses = gen_ed_data.get("gen_ed_courses", {})
                    # Handle all gen_ed subcategories dynamically
                    for subcategory, courses_list in gen_ed_courses.items():
                        if subcategory in categories["gen_ed"]:
                            for course in courses_list:
                                categories["gen_ed"][subcategory][course["code"]] = course
                                categories["all_courses"][course["code"]] = course
            except Exception as e:
                print(f"Error loading gen_ed_courses.json: {e}")
        
        return categories

    def load_curriculum_template_for_flow(self, catalog_name):
        """Load curriculum template based on catalog name - FUTURE-PROOF VERSION."""
        course_data_dir = Path(__file__).parent.parent / "course_data"
        templates_dir = course_data_dir / "templates"
        
        # Extract year from catalog name (e.g., "B-IE-2565" -> "2565")
        year_match = re.search(r'(\d{4})', catalog_name)
        if year_match:
            year = year_match.group(1)
            template_file = templates_dir / f"curriculum_template_{year}.json"
            
            # If specific template exists, use it
            if template_file.exists():
                try:
                    with open(template_file, 'r', encoding='utf-8') as f:
                        return json.load(f)
                except Exception as e:
                    st.error(f"Error loading template {template_file}: {e}")
            else:
                st.warning(f"Template for {year} not found: {template_file}")
        
        # Fallback: Find the most recent available template
        available_templates = []
        if templates_dir.exists():
            for template_file in templates_dir.glob("curriculum_template_*.json"):
                template_year_match = re.search(r'curriculum_template_(\d{4})\.json', template_file.name)
                if template_year_match:
                    template_year = int(template_year_match.group(1))
                    available_templates.append((template_year, template_file))
        
        if available_templates:
            available_templates.sort(key=lambda x: x[0], reverse=True)
            newest_year, newest_template = available_templates[0]
            
            st.info(f"Using fallback template: {newest_template.name}")
            try:
                with open(newest_template, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                st.error(f"Error loading fallback template: {e}")
        
        st.error("No curriculum templates found!")
        return None

    def classify_course_for_flow(self, course_code, course_name="", course_categories=None):
        """
        Classify course into appropriate category.
        PRIORITY ORDER: Gen-Ed → Technical Electives → IE Core → Free Electives
        """
        if course_categories is None:
            course_categories = self.load_course_categories_for_flow()
        
        code = course_code.upper()
        
        # PRIORITY 1: Check Gen-Ed courses FIRST (highest priority)
        for subcategory, courses in course_categories["gen_ed"].items():
            if code in courses:
                return ("gen_ed", subcategory, True)
        
        # PRIORITY 2: Check Technical Electives
        if code in course_categories["technical_electives"]:
            return ("technical_electives", "technical", True)
        
        # PRIORITY 3: Check IE Core courses
        if code in course_categories["ie_core"]:
            return ("ie_core", "core", True)
        
        # PRIORITY 4: Everything else is free elective (not in our database)
        return ("free_electives", "free", False)  # False = not identified in database

    def analyze_student_progress_enhanced(self, semesters, template, course_categories):
        """
        Enhanced: Analyze student's actual progress against the curriculum template with much more lenient deviation detection.
        Updated to use proper technical electives classification.
        """
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

        # Analyze elective courses (FIXED: Now uses proper technical electives classification)
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
                    # FIXED: Use the updated classify function that properly handles technical electives
                    category, subcategory, is_identified = self.classify_course_for_flow(code, course.get("name", ""), course_categories)
                    
                    elective_key = None
                    if category == "technical_electives":  # FIXED: Now properly handled
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

    def create_enhanced_template_flow_html(self, student_info, semesters, validation_results, selected_course_data=None):
        """Create template-based HTML flow chart with enhanced deviation detection."""
        
        course_categories = self.load_course_categories_for_flow()
        
        # Load curriculum template
        catalog_filename = selected_course_data.get('filename', 'B-IE-2565.json') if selected_course_data else 'B-IE-2565.json'
        template = self.load_curriculum_template_for_flow(catalog_filename)
        
        if not template:
            return "Error: Could not load curriculum template", 1
        
        # Use the FIXED analysis function
        analysis = self.analyze_student_progress_enhanced(semesters, template, course_categories)
        
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
            .category-header.wellness_PE { background: linear-gradient(45deg, #e67e22, #d35400); }
            .category-header.entrepreneurship { background: linear-gradient(45deg, #f39c12, #e67e22); }
            .category-header.language_communication_thai { background: linear-gradient(45deg, #3498db, #2980b9); }
            .category-header.language_communication_foreigner { background: linear-gradient(45deg, #2980b9, #1f4e79); }
            .category-header.language_communication_computer { background: linear-gradient(45deg, #5dade2, #3498db); }
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
            <title>Template-Based IE Curriculum Flow Chart</title>
            <meta charset="utf-8">
            {css_styles}
        </head>
        <body>
            <div class="curriculum-container">
                <div class="header">
                    <h1>Industrial Engineering Curriculum Template Flow Chart</h1>
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
            category_display_map = {
                'wellness': 'Wellness',
                'wellness_PE': 'Wellness & PE',
                'entrepreneurship': 'Entrepreneurship',
                'language_communication_thai': 'Thai Language & Communication',
                'language_communication_foreigner': 'Foreign Language & Communication',
                'language_communication_computer': 'Computer & Digital Literacy',
                'thai_citizen_global': 'Thai Citizen & Global',
                'aesthetics': 'Aesthetics',
                'technical_electives': 'Technical Electives',
                'free_electives': 'Free Electives'
            }
            category_display = category_display_map.get(elective_key, elective_key.replace('_', ' ').title())
            
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
            <h3 style="text-align: center; color: #2c3e50;">📊 Enhanced Analysis - Overall Progress Summary</h3>
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
                <h4 style="margin: 0 0 10px 0; color: #27ae60;">📋 Schedule Analysis Summary</h4>
                <p style="margin: 0; font-size: 14px; color: #2c3e50;">
                    <strong>Enhanced Analysis:</strong> The deviation detection is now much more lenient and realistic. 
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
    
    
    def generate_and_display_flow_chart(self, student_info: Dict, semesters: List[Dict], 
                                       validation_results: List[Dict], selected_course_data: Dict):
        """Generate and display the flow chart in Streamlit."""
        st.divider()
        st.header("📊 Advanced Visualizations & Downloads - FIXED VERSION")
        
        try:
            with st.spinner("Generating FIXED template-based curriculum flow chart..."):
                flow_html, flow_unidentified = self.create_enhanced_template_flow_html(
                    student_info, semesters, validation_results, selected_course_data
                )
            
            st.subheader("🗂️ Template-Based Curriculum Flow Chart")
            st.markdown("*Shows ideal curriculum template with your actual progress and enhanced deviation analysis*")
            
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
                components.html(js_code, height=0)
                
                # Show success message and provide re-open option
                col_flow1, col_flow2 = st.columns([2, 1])
                
                with col_flow1:
                    st.success("✅ Flow chart automatically opened in new window!")
                    st.info("🔧 **Enhanced:** Schedule deviations are now more lenient and realistic")
                    if flow_unidentified > 0:
                        st.warning(f"⚠️ {flow_unidentified} unidentified courses in flow chart")
                
                with col_flow2:
                    # Re-open button for popup blocker cases
                    if st.button("🔄 Re-open Flow Chart", help="Click if popup was blocked"):
                        js_reopen = f"""
                        <script>
                        const flowHTML = `{escaped_flow_html}`;
                        const newWindow = window.open('', '_blank');
                        newWindow.document.write(flowHTML);
                        newWindow.document.close();
                        </script>
                        """
                        components.html(js_reopen, height=0)
                        st.success("✅ Flow chart re-opened!")
                
                st.info("💡 **Note:** If the window didn't open automatically, use the 'Re-open' button (popup might be blocked by browser).")
                
            else:
                st.error("❌ No HTML content generated for flow chart")
                
        except Exception as e:
            st.error(f"Error generating flow chart: {e}")
            with st.expander("Debug Information"):
                st.code(str(e))
