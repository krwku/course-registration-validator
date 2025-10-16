import streamlit as st
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from components.session_manager import SessionManager
from components.ui_components import UIComponents
import re

class CourseAnalyzer:
    """Handles course analysis and classification."""
    
    def __init__(self):
        self.course_categories = None
    
    def load_course_categories(self) -> Dict:
        """FUTURE-PROOF VERSION: Load course categories from separate JSON files."""
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
        
        self.course_categories = categories
        return categories
    
    def classify_course(self, course_code: str, course_name: str = "", 
                       course_categories: Optional[Dict] = None) -> Tuple[str, str, bool]:
        """
        Classify course into appropriate category.
        PRIORITY ORDER: Gen-Ed → Technical Electives → IE Core → Free Electives
        """
        if course_categories is None:
            if self.course_categories is None:
                self.course_categories = self.load_course_categories()
            course_categories = self.course_categories
        
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
    
    def analyze_unidentified_courses(self, semesters: List[Dict]) -> List[Dict]:
        """Analyze transcript for unidentified courses."""
        if self.course_categories is None:
            self.course_categories = self.load_course_categories()
        
        unidentified_courses = []
        
        try:
            for semester in semesters:
                for course in semester.get("courses", []):
                    course_code = course.get("code", "")
                    course_name = course.get("name", "")
                    
                    if course_code:
                        category, subcategory, is_identified = self.classify_course(
                            course_code, course_name, self.course_categories
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
    
    def calculate_credit_summary(self, semesters: List[Dict]) -> Dict:
        """
        Calculate credit summary by category.
        FIXED: Now properly handles technical electives from B-IE files.
        """
        if self.course_categories is None:
            self.course_categories = self.load_course_categories()
        
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
                        category, subcategory, is_identified = self.classify_course(
                            course_code, course_name, self.course_categories
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
    
    def analyze_and_display_courses(self, semesters: List[Dict]):
        """Analyze courses and display results."""
        session_manager = SessionManager()
        
        # Load course categories if not already loaded
        if self.course_categories is None:
            self.course_categories = self.load_course_categories()
            session_manager.set_course_categories(self.course_categories)
        
        # Analyze unidentified courses
        unidentified_courses = self.analyze_unidentified_courses(semesters)
        session_manager.set_unidentified_count(len(unidentified_courses))
        
        # Display unidentified courses info
        UIComponents.display_unidentified_courses_info(unidentified_courses)
        
        # Calculate and display credit summary
        credit_summary = self.calculate_credit_summary(semesters)
        UIComponents.display_credit_summary(credit_summary)
    
    def get_course_statistics(self) -> Dict:
        """Get statistics about course categories."""
        if self.course_categories is None:
            self.course_categories = self.load_course_categories()
        
        stats = {
            'ie_core': len(self.course_categories["ie_core"]),
            'technical_electives': len(self.course_categories["technical_electives"]),
            'gen_ed': {
                category: len(courses) for category, courses in self.course_categories["gen_ed"].items()
            },
            'total': len(self.course_categories["all_courses"])
        }
        
        return stats
    
    def get_courses_by_category(self, category: str, subcategory: str = None) -> Dict:
        """Get courses by category and subcategory."""
        if self.course_categories is None:
            self.course_categories = self.load_course_categories()
        
        if category == "gen_ed" and subcategory:
            return self.course_categories["gen_ed"].get(subcategory, {})
        else:
            return self.course_categories.get(category, {})
    
    def is_course_technical_elective(self, course_code: str) -> bool:
        """Check if a course is a technical elective."""
        if self.course_categories is None:
            self.course_categories = self.load_course_categories()
        
        return course_code.upper() in self.course_categories["technical_electives"]
    
    def get_course_info(self, course_code: str) -> Optional[Dict]:
        """Get detailed information about a course."""
        if self.course_categories is None:
            self.course_categories = self.load_course_categories()
        
        return self.course_categories["all_courses"].get(course_code.upper())


class CourseClassificationHelper:
    """Helper class for course classification tasks."""
    
    @staticmethod
    def extract_credit_value(credits_str: str) -> int:
        """Extract numeric credit value from credit string like '3(3-0-6)'."""
        try:
            if isinstance(credits_str, int):
                return credits_str
            elif isinstance(credits_str, str):
                if "(" in credits_str:
                    return int(credits_str.split("(")[0])
                else:
                    return int(credits_str) if credits_str.isdigit() else 0
            else:
                return 0
        except (ValueError, AttributeError):
            return 0
    
    @staticmethod
    def is_passing_grade(grade: str) -> bool:
        """Check if a grade is a passing grade."""
        return grade in ["A", "B+", "B", "C+", "C", "D+", "D", "P"]
    
    @staticmethod
    def get_grade_points(grade: str) -> float:
        """Get grade points for GPA calculation."""
        grade_points = {
            "A": 4.0,
            "B+": 3.5,
            "B": 3.0,
            "C+": 2.5,
            "C": 2.0,
            "D+": 1.5,
            "D": 1.0,
            "F": 0.0
        }
        return grade_points.get(grade, 0.0)
    
    @staticmethod
    def categorize_by_department(course_code: str) -> str:
        """Categorize course by department code."""
        if not course_code:
            return "Unknown"
        
        dept_code = course_code[:5] if len(course_code) >= 5 else course_code
        
        dept_mapping = {
            "01206": "Industrial Engineering",
            "01204": "Computer Science", 
            "01205": "Electrical Engineering",
            "01208": "Mechanical Engineering",
            "01213": "Materials Engineering",
            "01417": "Mathematics",
            "01420": "Physics",
            "01403": "Chemistry",
            "01361": "Thai Language",
            "01355": "English Language",
            "01175": "Physical Education",
            "01999": "General Education",
            "01418": "Information Technology"
        }
        
        return dept_mapping.get(dept_code, f"Department {dept_code}")


class CourseValidationHelper:
    """Helper class for course validation related tasks."""
    
    @staticmethod
    def check_prerequisite_satisfaction(course_code: str, passed_courses: List[str], 
                                      course_analyzer: CourseAnalyzer) -> Tuple[bool, str]:
        """Check if prerequisites are satisfied for a course."""
        course_info = course_analyzer.get_course_info(course_code)
        
        if not course_info:
            return True, "Course not found in database"
        
        prerequisites = course_info.get("prerequisites", [])
        if not prerequisites:
            return True, "No prerequisites required"
        
        missing_prerequisites = []
        for prereq in prerequisites:
            if prereq not in passed_courses:
                missing_prerequisites.append(prereq)
        
        if missing_prerequisites:
            return False, f"Missing prerequisites: {', '.join(missing_prerequisites)}"
        
        return True, "All prerequisites satisfied"
    
    @staticmethod
    def validate_credit_load(semester_credits: int, semester_type: str) -> Tuple[bool, str]:
        """Validate credit load for a semester."""
        if semester_type.lower() == "summer":
            max_credits = 9
        else:
            max_credits = 22
        
        if semester_credits > max_credits:
            return False, f"Exceeds maximum {max_credits} credits for {semester_type} semester"
        
        return True, f"Credit load valid: {semester_credits} credits"
