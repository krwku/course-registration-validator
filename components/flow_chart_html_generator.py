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
                           css_class: str, status_info: str) -> str:
        """Generate HTML for a single course box."""
        return f"""
        <div class="{css_class}">
            <div class="course-code">{course_code}</div>
            <div class="course-name">{course_name}</div>
            <div class="course-info">{credits} credits • {status_info}</div>
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