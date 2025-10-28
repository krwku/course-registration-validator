"""
HTML generation for curriculum flow charts.
Separated from main flow chart logic for better maintainability.
"""

import json
from typing import Dict, List


class FlowChartHTMLGenerator:
    """Handles HTML generation for curriculum flow charts."""
    
    def __init__(self):
        pass
    
    def generate_css_styles(self) -> str:
        """Generate CSS styles for the flow chart."""
        return """
        <style>
            .curriculum-container {
                font-family: 'Segoe UI', sans-serif;
                max-width: 1400px;
                margin: 0 auto;
                padding: 20px;
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                position: relative;
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
                border-color: #3498db;
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
            
            .course-code { 
                font-size: 11px; 
                font-weight: bold; 
                margin-bottom: 4px; 
            }
            
            .course-name { 
                font-size: 10px; 
                line-height: 1.2; 
                margin-bottom: 4px; 
            }
            
            .course-info { 
                font-size: 9px; 
                opacity: 0.8; 
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
            
            .course-deviation {
                border: 3px solid #f39c12 !important;
            }
            
            .course-deviation.high {
                border-color: #e74c3c !important;
            }
            
            .course-deviation.low {
                border-color: #27ae60 !important;
            }
            
            .deviation-tooltip {
                display: none;
                position: absolute;
                bottom: -70px;
                left: 50%;
                transform: translateX(-50%);
                background: #e67e22;
                color: white;
                padding: 8px 12px;
                border-radius: 6px;
                font-size: 11px;
                z-index: 999;
                max-width: 300px;
                white-space: normal;
                text-align: center;
                box-shadow: 0 4px 12px rgba(230, 126, 34, 0.3);
            }
            
            .course-deviation:hover .deviation-tooltip {
                display: block;
            }
            
            .deviation-tooltip::after {
                content: '';
                position: absolute;
                bottom: 100%;
                left: 50%;
                margin-left: -5px;
                border-width: 5px;
                border-style: solid;
                border-color: transparent transparent #e67e22 transparent;
            }
            
            .course-tooltip {
                display: none;
                position: absolute;
                top: -80px;
                left: 50%;
                transform: translateX(-50%);
                background: linear-gradient(135deg, #2c3e50, #34495e);
                color: white;
                padding: 12px 16px;
                border-radius: 8px;
                font-size: 12px;
                z-index: 1001;
                max-width: 350px;
                white-space: nowrap;
                text-align: center;
                box-shadow: 0 6px 20px rgba(0,0,0,0.3);
                border: 2px solid #3498db;
            }
            
            .course-tooltip::after {
                content: '';
                position: absolute;
                top: 100%;
                left: 50%;
                margin-left: -5px;
                border-width: 5px;
                border-style: solid;
                border-color: #2c3e50 transparent transparent transparent;
            }
            
            .course-box:hover .course-tooltip {
                display: block;
            }
            
            .course-box.has-relationships::after {
                content: "i";
                position: absolute;
                top: 2px;
                right: 2px;
                font-size: 10px;
                opacity: 0.6;
                background: #3498db;
                color: white;
                border-radius: 50%;
                width: 12px;
                height: 12px;
                display: flex;
                align-items: center;
                justify-content: center;
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
        </style>
        """
    
    def generate_header_section(self, student_info: Dict, template: Dict) -> str:
        """Generate the header section of the flow chart."""
        return f"""
        <div class="header">
            <h1>Industrial Engineering Curriculum Template Flow Chart</h1>
            <div class="template-info">
                <strong>Template:</strong> {template.get('curriculum_name', 'Unknown')} | 
                <strong>Student:</strong> {student_info.get('name', 'N/A')} ({student_info.get('id', 'N/A')})
            </div>
        </div>
        """
    
    def generate_legend_section(self) -> str:
        """Generate the legend section."""
        return """
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
        </div>
        """
    
    def generate_course_box(self, course_code: str, course_name: str, credits: int, 
                           css_class: str, status_info: str, deviation_info: str = "", 
                           tooltip_content: str = "") -> str:
        """Generate HTML for a single course box."""
        return f"""
        <div class="{css_class}">
            {deviation_info}
            {tooltip_content}
            <div class="course-code">{course_code}</div>
            <div class="course-name">{course_name}</div>
            <div class="course-info">{credits} credits - {status_info}</div>
        </div>
        """
    
    def generate_year_section(self, year_num: str, semesters_html: str) -> str:
        """Generate HTML for a year section."""
        return f"""
        <div class="year-column">
            <div class="year-header">Year {year_num}</div>
            {semesters_html}
        </div>
        """
    
    def generate_semester_section(self, semester_name: str, courses_html: str) -> str:
        """Generate HTML for a semester section."""
        return f"""
        <div class="semester-section">
            <div class="semester-header">{semester_name}</div>
            {courses_html}
        </div>
        """
    
    def generate_complete_html(self, student_info: Dict, template: Dict, 
                              curriculum_grid_html: str) -> str:
        """Generate the complete HTML document."""
        css_styles = self.generate_css_styles()
        header_html = self.generate_header_section(student_info, template)
        legend_html = self.generate_legend_section()
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Template-Based IE Curriculum Flow Chart</title>
            <meta charset="utf-8">
            {css_styles}
        </head>
        <body>
            <div class="curriculum-container">
                {header_html}
                {legend_html}
                <div class="year-container">
                    {curriculum_grid_html}
                </div>
            </div>
        </body>
        </html>
        """
    
    def generate_electives_section(self, template: Dict, analysis: Dict) -> str:
        """Generate the electives requirements section."""
        html = """
        <div class="electives-section">
            <h2 style="text-align: center; color: #2c3e50; margin-bottom: 20px;">Elective Requirements Progress</h2>
            <div class="electives-grid">
        """
        
        for elective_key, required_credits in template.get('elective_requirements', {}).items():
            analysis_data = analysis['elective_analysis'].get(elective_key, {'required': required_credits, 'completed': 0, 'courses': []})
            completed_credits = analysis_data['completed']
            courses = analysis_data['courses']
            
            progress_percentage = min((completed_credits / required_credits) * 100, 100) if required_credits > 0 else 0
            
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
            
            html += f"""
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
            """
            
            if courses:
                for course in courses:
                    html += f"""
                    <div class="course-box course-completed" style="margin-bottom: 5px;">
                        <div class="course-code">{course["code"]}</div>
                        <div class="course-name">{course["name"]}</div>
                        <div class="course-info">{course["credits"]} credits - {course["semester"]}</div>
                    </div>
                    """
            else:
                html += '<div style="text-align: center; color: #7f8c8d; font-style: italic;">No courses completed yet</div>'
            
            html += '</div>'
        
        html += '</div></div>'
        return html