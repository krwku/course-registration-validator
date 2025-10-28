"""
Clean, modular flow chart generator.
Split into smaller components for better maintainability and Streamlit Cloud compatibility.
"""

import streamlit as st
from typing import Dict, List
import streamlit.components.v1 as components
from components.flow_chart_data_analyzer import FlowChartDataAnalyzer
from components.flow_chart_html_generator import FlowChartHTMLGenerator


class FlowChartGenerator:
    """Main flow chart generator class - clean and modular."""
    
    def __init__(self):
        self.data_analyzer = FlowChartDataAnalyzer()
        self.html_generator = FlowChartHTMLGenerator()
    
    def load_course_categories_for_flow(self):
        """Load course categories for the flow generator."""
        return self.data_analyzer.load_course_categories()
    
    def load_curriculum_template_for_flow(self, catalog_name: str):
        """Load curriculum template."""
        return self.data_analyzer.load_curriculum_template(catalog_name)
    
    def classify_course_for_flow(self, course_code: str, course_name: str = "", course_categories=None):
        """Classify course for flow chart."""
        return self.data_analyzer.classify_course(course_code, course_name)
    
    def analyze_student_progress_enhanced(self, semesters: List[Dict], template: Dict, course_categories: Dict):
        """Analyze student progress."""
        return self.data_analyzer.analyze_student_progress(semesters, template)
    
    def create_enhanced_template_flow_html(self, student_info: Dict, semesters: List[Dict], 
                                         validation_results: List[Dict], selected_course_data=None) -> tuple:
        """Create template-based HTML flow chart."""
        
        # Load data
        course_categories = self.load_course_categories_for_flow()
        curriculum_name = selected_course_data.get('curriculum_folder', 'B-IE-2565') if selected_course_data else 'B-IE-2565'
        template = self.load_curriculum_template_for_flow(curriculum_name)
        
        if not template:
            return "Error: Could not load curriculum template", 1
        
        # Analyze progress
        analysis = self.analyze_student_progress_enhanced(semesters, template, course_categories)
        
        # Generate curriculum grid HTML
        curriculum_grid_html = ""
        
        for year_key in sorted(template.get('core_curriculum', {}).keys()):
            year_num = year_key.split('_')[1]
            year_data = template['core_curriculum'][year_key]
            
            semesters_html = ""
            
            for semester_key in ['first_semester', 'second_semester']:
                if semester_key not in year_data:
                    continue
                    
                semester_name = 'First Semester' if semester_key == 'first_semester' else 'Second Semester'
                course_codes = year_data[semester_key]
                
                courses_html = ""
                
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
                    
                    # Determine status
                    css_class = "course-box"
                    status_info = "Not taken"
                    
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
                    
                    courses_html += self.html_generator.generate_course_box(
                        course_code, course_name, credits, css_class, status_info
                    )
                
                semesters_html += self.html_generator.generate_semester_section(semester_name, courses_html)
            
            curriculum_grid_html += self.html_generator.generate_year_section(year_num, semesters_html)
        
        # Generate complete HTML
        complete_html = self.html_generator.generate_complete_html(
            student_info, template, curriculum_grid_html
        )
        
        return complete_html, 0
    
    def generate_and_display_flow_chart(self, student_info: Dict, semesters: List[Dict], 
                                       validation_results: List[Dict], selected_course_data: Dict):
        """Generate and display the flow chart in Streamlit."""
        st.divider()
        st.header("Visualizations & Downloads")
        
        try:
            with st.spinner("Generating curriculum flow chart..."):
                flow_html, flow_unidentified = self.create_enhanced_template_flow_html(
                    student_info, semesters, validation_results, selected_course_data
                )
            
            st.subheader("Curriculum Flow Chart")
            st.markdown("Interactive curriculum template with progress tracking")
            
            if flow_html and len(flow_html.strip()) > 0:
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    if flow_unidentified > 0:
                        st.info(f"Note: {flow_unidentified} courses require classification")
                
                with col2:
                    st.download_button(
                        label="Download Flow Chart",
                        data=flow_html.encode('utf-8'),
                        file_name=f"curriculum_flow_{student_info.get('id', 'student')}.html",
                        mime="text/html",
                        type="primary",
                        help="Download interactive flow chart"
                    )
                
                st.success("Flow chart ready for download")
                
            else:
                st.error("Unable to generate flow chart")
                
        except Exception as e:
            st.error(f"Error generating flow chart: {e}")
            with st.expander("Debug Information"):
                st.code(str(e))