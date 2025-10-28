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
        
        for semester in semesters:
            for course in semester.get("courses", []):
                code = course.get("code", "")
                grade = course.get("grade", "")
                
                if grade in ["A", "B+", "B", "C+", "C", "D+", "D", "P"]:
                    completed_courses[code] = {
                        "grade": grade,
                        "semester": semester.get("semester", ""),
                        "credits": course.get("credits", 0)
                    }
                elif grade == "F":
                    failed_courses[code] = {"grade": grade, "semester": semester.get("semester", "")}
                elif grade == "W":
                    withdrawn_courses[code] = {"grade": grade, "semester": semester.get("semester", "")}
                elif grade in ["N", ""]:
                    current_courses[code] = {"grade": grade, "semester": semester.get("semester", "")}
        
        return {
            "completed_courses": completed_courses,
            "failed_courses": failed_courses,
            "withdrawn_courses": withdrawn_courses,
            "current_courses": current_courses,
            "deviations": [],  # Simplified for now
            "elective_analysis": {}  # Simplified for now
        }