"""
Data analysis logic for curriculum flow charts.
Handles course progress analysis and classification.
"""

from typing import Dict, List, Tuple
from pathlib import Path
import json
import re


class FlowChartDataAnalyzer:
    """Handles data analysis for curriculum flow charts."""
    
    def __init__(self):
        self.course_categories = None
    
    def load_course_categories(self) -> Dict:
        """Load course categories from data files."""
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
        
        # Load IE courses from folders
        ie_files = []
        if course_data_dir.exists():
            for folder in course_data_dir.glob("B-IE-*"):
                if folder.is_dir():
                    courses_file = folder / "courses.json"
                    if courses_file.exists():
                        year_match = re.search(r'B-IE-(\d{4})', folder.name)
                        if year_match:
                            year = int(year_match.group(1))
                            ie_files.append((year, courses_file))
        
        # Sort by year and process
        ie_files.sort(key=lambda x: x[0], reverse=True)
        
        for year, ie_file in ie_files:
            try:
                with open(ie_file, 'r', encoding='utf-8') as f:
                    ie_data = json.load(f)
                    
                    for course in ie_data.get("industrial_engineering_courses", []):
                        if course["code"] not in categories["all_courses"]:
                            if course.get("technical_electives", False):
                                categories["technical_electives"][course["code"]] = course
                            else:
                                categories["ie_core"][course["code"]] = course
                            categories["all_courses"][course["code"]] = course
                    
                    for course in ie_data.get("other_related_courses", []):
                        if course["code"] not in categories["all_courses"]:
                            categories["ie_core"][course["code"]] = course  
                            categories["all_courses"][course["code"]] = course
                            
            except Exception as e:
                print(f"Error loading {ie_file}: {e}")
                continue
        
        # Load Gen-Ed courses
        gen_ed_file = course_data_dir / "gen_ed_courses.json"
        if gen_ed_file.exists():
            try:
                with open(gen_ed_file, 'r', encoding='utf-8') as f:
                    gen_ed_data = json.load(f)
                    gen_ed_courses = gen_ed_data.get("gen_ed_courses", {})
                    
                    for subcategory, courses_list in gen_ed_courses.items():
                        if subcategory in categories["gen_ed"]:
                            for course in courses_list:
                                categories["gen_ed"][subcategory][course["code"]] = course
                                categories["all_courses"][course["code"]] = course
            except Exception as e:
                print(f"Error loading gen_ed_courses.json: {e}")
        
        self.course_categories = categories
        return categories
    
    def load_curriculum_template(self, catalog_name: str) -> Dict:
        """Load curriculum template from folder structure."""
        course_data_dir = Path(__file__).parent.parent / "course_data"
        
        curriculum_name = catalog_name.replace('.json', '') if catalog_name.endswith('.json') else catalog_name
        
        if '/' in curriculum_name:
            curriculum_name = curriculum_name.split('/')[0]
        
        curriculum_dir = course_data_dir / curriculum_name
        template_file = curriculum_dir / "template.json"
        
        if template_file.exists():
            try:
                with open(template_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading template {template_file}: {e}")
        
        return None
    
    def classify_course(self, course_code: str, course_name: str = "") -> Tuple[str, str, bool]:
        """Classify course into appropriate category."""
        if self.course_categories is None:
            self.course_categories = self.load_course_categories()
        
        code = course_code.upper()
        
        # Check Gen-Ed courses first
        for subcategory, courses in self.course_categories["gen_ed"].items():
            if code in courses:
                return ("gen_ed", subcategory, True)
        
        # Check Technical Electives
        if code in self.course_categories["technical_electives"]:
            return ("technical_electives", "technical", True)
        
        # Check IE Core courses
        if code in self.course_categories["ie_core"]:
            return ("ie_core", "core", True)
        
        # Check by prefix for technical electives
        if code.startswith("01206"):
            return ("technical_electives", "technical", False)
        
        # Default to free electives
        return ("free_electives", "free", False)
    
    def analyze_student_progress(self, semesters: List[Dict], template: Dict) -> Dict:
        """Analyze student's progress against curriculum template."""
        if self.course_categories is None:
            self.course_categories = self.load_course_categories()
        
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
            if year and year > 1900:
                semester_years.append(year)
                if earliest_year is None or year < earliest_year:
                    earliest_year = year
        
        # Calculate academic years for each semester
        for semester in semesters:
            calendar_year = semester.get("year_int", 0)
            semester_type = semester.get("semester_type", "")
            
            # Calculate academic year
            academic_year = 1
            if earliest_year and calendar_year and calendar_year > 1900:
                academic_year = calendar_year - earliest_year + 1
            
            for course in semester.get("courses", []):
                code = course.get("code", "")
                grade = course.get("grade", "")
                
                # Normalize semester type for comparison
                normalized_semester_type = semester_type
                if normalized_semester_type not in ["First", "Second", "Summer"]:
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
                        "semester_type": normalized_semester_type
                    }
                elif grade == "F":
                    failed_courses[code] = {"grade": grade, "semester": semester.get("semester", "")}
                elif grade == "W":
                    withdrawn_courses[code] = {"grade": grade, "semester": semester.get("semester", "")}
                elif grade in ["N", ""]:
                    current_courses[code] = {"grade": grade, "semester": semester.get("semester", "")}
        
        # Analyze deviations
        deviations = []
        for year_key, year_data in template.get("core_curriculum", {}).items():
            expected_year = int(year_key.split("_")[1])
            
            for semester_key, course_codes in year_data.items():
                expected_semester = "First" if "first" in semester_key else "Second"
                
                for course_code in course_codes:
                    if course_code in completed_courses:
                        actual_academic_year = completed_courses[course_code]["academic_year"]
                        actual_semester = completed_courses[course_code]["semester_type"]
                        
                        year_diff = abs(actual_academic_year - expected_year)
                        semester_different = actual_semester != expected_semester
                        
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
                        
                        if should_flag:
                            deviations.append({
                                "course_code": course_code,
                                "expected": f"Year {expected_year} {expected_semester}",
                                "actual": f"Year {actual_academic_year} {actual_semester}",
                                "severity": severity,
                                "year_diff": year_diff
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
                    category, subcategory, is_identified = self.classify_course(code, course.get("name", ""))
                    
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