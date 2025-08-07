import json
from pathlib import Path

def load_course_categories():
    """Load course categories from existing JSON files."""
    course_data_dir = Path(__file__).parent.parent / "course_data"
    
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

def load_curriculum_template(catalog_name):
    """Load curriculum template based on catalog name."""
    course_data_dir = Path(__file__).parent.parent / "course_data"
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
            print(f"Error loading template: {e}")
    
    return None

def classify_course(course_code, course_name="", course_categories=None):
    """Classify course into appropriate category."""
    if course_categories is None:
        course_categories = load_course_categories()
    
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

def analyze_student_progress(semesters, template, course_categories):
    """Analyze student's actual progress against the curriculum template."""
    # Organize student courses by completion status
    completed_courses = {}
    failed_courses = {}
    withdrawn_courses = {}
    current_courses = {}
    
    for semester in semesters:
        for course in semester.get("courses", []):
            code = course.get("code", "")
            grade = course.get("grade", "")
            
            if grade in ["A", "B+", "B", "C+", "C", "D+", "D", "P"]:
                completed_courses[code] = {
                    "grade": grade,
                    "semester": semester.get("semester", ""),
                    "credits": course.get("credits", 0),
                    "year": semester.get("year_int", 0),
                    "semester_type": semester.get("semester_type", "")
                }
            elif grade == "F":
                failed_courses[code] = {"grade": grade, "semester": semester.get("semester", "")}
            elif grade == "W":
                withdrawn_courses[code] = {"grade": grade, "semester": semester.get("semester", "")}
            elif grade in ["N", ""]:
                current_courses[code] = {"grade": grade, "semester": semester.get("semester", "")}
    
    # Analyze deviations from template
    deviations = []
    
    for year_key, year_data in template.get("core_curriculum", {}).items():
        expected_year = int(year_key.split("_")[1])
        
        for semester_key, course_codes in year_data.items():
            expected_semester = "First" if "first" in semester_key else "Second"
            
            for course_code in course_codes:
                if course_code in completed_courses:
                    actual_year = completed_courses[course_code]["year"]
                    actual_semester = completed_courses[course_code]["semester_type"]
                    
                    if actual_year != expected_year or actual_semester != expected_semester:
                        deviations.append({
                            "course_code": course_code,
                            "expected": f"Year {expected_year} {expected_semester}",
                            "actual": f"Year {actual_year} {actual_semester}",
                            "severity": "moderate" if abs(actual_year - expected_year) <= 1 else "high"
                        })
    
    # Analyze elective courses
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
                category, subcategory, is_identified = classify_course(code, course.get("name", ""), course_categories)
                
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
    
    return {
        "completed_courses": completed_courses,
        "failed_courses": failed_courses,
        "withdrawn_courses": withdrawn_courses,
        "current_courses": current_courses,
        "deviations": deviations,
        "elective_analysis": elective_analysis
    }

def create_template_based_flow_html(student_info, semesters, validation_results, selected_course_data=None):
    """Create template-based HTML flow chart."""
    
    course_categories = load_course_categories()
    
    # Load curriculum template
    catalog_filename = selected_course_data.get('filename', 'B-IE-2565.json') if selected_course_data else 'B-IE-2565.json'
    template = load_curriculum_template(catalog_filename)
    
    if not template:
        return "Error: Could not load curriculum template", 1
    
    # Analyze student progress
    analysis = analyze_student_progress(semesters, template, course_categories)
    
    # CSS styles
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
            border: 1px solid #ffeaa7;
            padding: 15px;
            margin-bottom: 20px;
            border-radius: 5px;
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
            border: 3px solid #e74c3c !important;
        }
        
        .course-deviation::before {
            content: '⚠️';
            position: absolute;
            top: -5px;
            right: -5px;
            background: #e74c3c;
            color: white;
            border-radius: 50%;
            width: 18px;
            height: 18px;
            font-size: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .deviation-tooltip {
            display: none;
            position: absolute;
            top: -50px;
            left: 50%;
            transform: translateX(-50%);
            background: #e74c3c;
            color: white;
            padding: 5px 10px;
            border-radius: 4px;
            font-size: 10px;
            white-space: nowrap;
            z-index: 1000;
        }
        
        .course-deviation:hover .deviation-tooltip {
            display: block;
        }
        
        .course-code { font-size: 11px; font-weight: bold; margin-bottom: 4px; }
        .course-name { font-size: 10px; line-height: 1.2; margin-bottom: 4px; }
        .course-info { font-size: 9px; opacity: 0.8; }
        
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
    
    # Add deviation alerts
    if analysis['deviations']:
        html_content += f"""
        <div class="deviation-alert">
            <h4>⚠️ Schedule Deviations Detected ({len(analysis['deviations'])} courses)</h4>
            <p>Some courses were taken in different semesters than the recommended template. Hover over courses with ⚠️ for details.</p>
        </div>
        """
    
    # Add legend
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
            <span style="color: #e74c3c; font-weight: bold;">⚠️</span>
            <span>Schedule Deviation</span>
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
                
                # Check for deviations
                deviation = next((d for d in analysis['deviations'] if d['course_code'] == course_code), None)
                if deviation:
                    css_class += " course-deviation"
                    deviation_info = f'<div class="deviation-tooltip">Expected: {deviation["expected"]}<br>Actually taken: {deviation["actual"]}</div>'
                
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
    
    # Add electives section
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
    
    # Add progress summary
    total_template_courses = sum(len(courses) for year_data in template.get('core_curriculum', {}).values() 
                               for courses in year_data.values())
    completed_template_courses = len([c for c in analysis['completed_courses'] 
                                    if any(c in courses for year_data in template.get('core_curriculum', {}).values() 
                                          for courses in year_data.values())])
    
    html_content += f'''
    <div class="stats-summary">
        <h3 style="text-align: center; color: #2c3e50;">📊 Overall Progress Summary</h3>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-top: 15px;">
            <div style="text-align: center; background: #f8f9fa; padding: 15px; border-radius: 8px;">
                <div style="font-size: 24px; font-weight: bold; color: #2c3e50;">{completed_template_courses}/{total_template_courses}</div>
                <div style="font-size: 12px; color: #7f8c8d;">Core Courses Completed</div>
            </div>
            <div style="text-align: center; background: #f8f9fa; padding: 15px; border-radius: 8px;">
                <div style="font-size: 24px; font-weight: bold; color: #e74c3c;">{len(analysis['deviations'])}</div>
                <div style="font-size: 12px; color: #7f8c8d;">Schedule Deviations</div>
            </div>
            <div style="text-align: center; background: #f8f9fa; padding: 15px; border-radius: 8px;">
                <div style="font-size: 24px; font-weight: bold; color: #f39c12;">{unidentified_count}</div>
                <div style="font-size: 12px; color: #7f8c8d;">Unidentified Courses</div>
            </div>
        </div>
    </div>
    '''
    
    html_content += '''
        </div>
    </body>
    </html>
    '''
    
    return html_content, unidentified_count
