import streamlit as st
from pathlib import Path
from typing import Dict, List, Optional
import json
from datetime import datetime

class ComprehensiveReportGenerator:
    """Generates comprehensive academic progress reports in HTML format."""
    
    def __init__(self):
        self.course_categories = None
        self.template = None
    
    def generate_comprehensive_report(self, student_info: Dict, semesters: List[Dict], 
                                    validation_results: List[Dict], selected_course_data: Dict) -> str:
        """Generate a comprehensive HTML report with analysis and recommendations."""
        
        # Load necessary data
        from components.flow_chart_generator import FlowChartGenerator
        flow_generator = FlowChartGenerator()
        
        curriculum_name = selected_course_data.get('curriculum_folder', 'B-IE-2565')
        self.template = flow_generator.load_curriculum_template_for_flow(curriculum_name)
        self.course_categories = flow_generator.load_course_categories_for_flow()
        
        if not self.template:
            return "Error: Could not load curriculum template"
        
        # Analyze student progress
        analysis = flow_generator.analyze_student_progress_enhanced(semesters, self.template, self.course_categories)
        
        # Generate report sections
        html_content = self._generate_html_structure()
        html_content += self._generate_header_section(student_info, curriculum_name)
        html_content += self._generate_executive_summary(student_info, semesters, analysis)
        html_content += self._generate_academic_progress_section(analysis, semesters)
        html_content += self._generate_course_completion_analysis(analysis, semesters)
        html_content += self._generate_validation_issues_section(validation_results)
        html_content += self._generate_graduation_requirements_section(analysis)
        html_content += self._generate_recommendations_section(analysis, semesters)
        html_content += self._generate_semester_planning_section(analysis, semesters)
        html_content += self._generate_footer()
        
        return html_content
    
    def _generate_html_structure(self) -> str:
        """Generate the HTML structure and CSS."""
        return """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Academic Progress Report</title>
            <style>
                * {
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }
                
                body {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                    min-height: 100vh;
                }
                
                .container {
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                }
                
                .report-header {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 40px;
                    border-radius: 15px;
                    margin-bottom: 30px;
                    text-align: center;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                }
                
                .report-header h1 {
                    font-size: 2.5em;
                    margin-bottom: 10px;
                    font-weight: 300;
                }
                
                .report-header .subtitle {
                    font-size: 1.2em;
                    opacity: 0.9;
                }
                
                .section {
                    background: white;
                    margin-bottom: 30px;
                    border-radius: 15px;
                    overflow: hidden;
                    box-shadow: 0 5px 20px rgba(0,0,0,0.1);
                }
                
                .section-header {
                    background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
                    color: white;
                    padding: 20px 30px;
                    font-size: 1.4em;
                    font-weight: 600;
                }
                
                .section-content {
                    padding: 30px;
                }
                
                .summary-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: 20px;
                    margin-bottom: 30px;
                }
                
                .summary-card {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 25px;
                    border-radius: 12px;
                    text-align: center;
                    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
                }
                
                .summary-card h3 {
                    font-size: 2.2em;
                    margin-bottom: 5px;
                    font-weight: 700;
                }
                
                .summary-card p {
                    font-size: 1.1em;
                    opacity: 0.9;
                }
                
                .progress-bar {
                    background: #e0e0e0;
                    border-radius: 25px;
                    height: 25px;
                    margin: 15px 0;
                    overflow: hidden;
                    position: relative;
                }
                
                .progress-fill {
                    background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
                    height: 100%;
                    border-radius: 25px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: white;
                    font-weight: bold;
                    transition: width 0.3s ease;
                }
                
                .status-good { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }
                .status-warning { background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); }
                .status-critical { background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%); }
                
                .course-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
                    gap: 15px;
                    margin: 20px 0;
                }
                
                .course-item {
                    background: #f8f9fa;
                    padding: 15px;
                    border-radius: 8px;
                    border-left: 4px solid #4facfe;
                }
                
                .course-item.completed { border-left-color: #00d4aa; }
                .course-item.failed { border-left-color: #ff6b6b; }
                .course-item.current { border-left-color: #4facfe; }
                
                .recommendation {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 20px;
                    border-radius: 12px;
                    margin: 15px 0;
                }
                
                .recommendation h4 {
                    margin-bottom: 10px;
                    font-size: 1.2em;
                }
                
                .action-item {
                    background: #e8f4fd;
                    border-left: 4px solid #4facfe;
                    padding: 15px;
                    margin: 10px 0;
                    border-radius: 0 8px 8px 0;
                }
                
                .semester-plan {
                    background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
                    padding: 20px;
                    border-radius: 12px;
                    margin: 15px 0;
                }
                
                .alert {
                    padding: 15px;
                    border-radius: 8px;
                    margin: 15px 0;
                }
                
                .alert-info { background: #e3f2fd; border-left: 4px solid #2196f3; }
                .alert-warning { background: #fff3e0; border-left: 4px solid #ff9800; }
                .alert-success { background: #e8f5e9; border-left: 4px solid #4caf50; }
                .alert-danger { background: #ffebee; border-left: 4px solid #f44336; }
                
                .footer {
                    text-align: center;
                    padding: 30px;
                    color: #666;
                    font-style: italic;
                }
                
                @media print {
                    body { background: white; }
                    .section { box-shadow: none; border: 1px solid #ddd; }
                }
            </style>
        </head>
        <body>
            <div class="container">
        """
    
    def _generate_header_section(self, student_info: Dict, curriculum_name: str) -> str:
        """Generate the report header."""
        current_date = datetime.now().strftime("%B %d, %Y")
        
        return f"""
        <div class="report-header">
            <h1>Academic Progress Report</h1>
            <div class="subtitle">
                <strong>{student_info.get('name', 'Student Name')}</strong> • 
                ID: {student_info.get('id', 'N/A')} • 
                {curriculum_name} • 
                Generated: {current_date}
            </div>
        </div>
        """
    
    def _generate_executive_summary(self, student_info: Dict, semesters: List[Dict], analysis: Dict) -> str:
        """Generate executive summary with key metrics."""
        
        # Calculate key metrics
        total_courses = sum(len(sem.get('courses', [])) for sem in semesters)
        total_credits = sum(sem.get('total_credits', 0) for sem in semesters)
        completed_courses = len(analysis['completed_courses'])
        failed_courses = len(analysis['failed_courses'])
        
        # Calculate GPA (simplified)
        grade_points = {'A': 4.0, 'B+': 3.5, 'B': 3.0, 'C+': 2.5, 'C': 2.0, 'D+': 1.5, 'D': 1.0, 'F': 0.0}
        total_points = 0
        total_credit_hours = 0
        
        for course_data in analysis['completed_courses'].values():
            grade = course_data.get('grade', 'F')
            if grade in grade_points:
                # Assume 3 credits per course for GPA calculation
                credits = 3
                total_points += grade_points[grade] * credits
                total_credit_hours += credits
        
        gpa = total_points / total_credit_hours if total_credit_hours > 0 else 0.0
        
        # Determine academic standing
        if gpa >= 3.5:
            standing = "Excellent"
            standing_class = "status-good"
        elif gpa >= 3.0:
            standing = "Good"
            standing_class = "status-good"
        elif gpa >= 2.5:
            standing = "Satisfactory"
            standing_class = "status-warning"
        else:
            standing = "Needs Improvement"
            standing_class = "status-critical"
        
        return f"""
        <div class="section">
            <div class="section-header">📊 Executive Summary</div>
            <div class="section-content">
                <div class="summary-grid">
                    <div class="summary-card">
                        <h3>{total_courses}</h3>
                        <p>Total Courses Taken</p>
                    </div>
                    <div class="summary-card">
                        <h3>{total_credits}</h3>
                        <p>Total Credits Earned</p>
                    </div>
                    <div class="summary-card">
                        <h3>{gpa:.2f}</h3>
                        <p>Estimated GPA</p>
                    </div>
                    <div class="summary-card {standing_class}">
                        <h3>{standing}</h3>
                        <p>Academic Standing</p>
                    </div>
                </div>
                
                <div class="alert alert-info">
                    <strong>Quick Overview:</strong> You have completed {completed_courses} courses successfully, 
                    with {failed_courses} courses that need attention. Your academic journey shows 
                    {"strong progress" if gpa >= 3.0 else "areas for improvement"} toward graduation.
                </div>
            </div>
        </div>
        """
    
    def _generate_academic_progress_section(self, analysis: Dict, semesters: List[Dict]) -> str:
        """Generate detailed academic progress analysis."""
        
        # Calculate progress by year
        year_progress = {}
        for semester in semesters:
            year = semester.get('year_int', 0)
            if year and year > 1900:
                if year not in year_progress:
                    year_progress[year] = {'courses': 0, 'credits': 0}
                year_progress[year]['courses'] += len(semester.get('courses', []))
                year_progress[year]['credits'] += semester.get('total_credits', 0)
        
        progress_html = """
        <div class="section">
            <div class="section-header">📈 Academic Progress Timeline</div>
            <div class="section-content">
        """
        
        for year in sorted(year_progress.keys()):
            data = year_progress[year]
            progress_html += f"""
            <div class="course-item">
                <h4>Academic Year {year}</h4>
                <p><strong>{data['courses']} courses</strong> • <strong>{data['credits']} credits</strong></p>
            </div>
            """
        
        # Add deviation analysis
        if analysis['deviations']:
            progress_html += f"""
            <div class="alert alert-warning">
                <strong>Schedule Variations:</strong> {len(analysis['deviations'])} courses were taken 
                outside the standard timeline. This is common and usually due to course availability 
                or personal planning preferences.
            </div>
            """
        
        progress_html += """
            </div>
        </div>
        """
        
        return progress_html
    
    def _generate_course_completion_analysis(self, analysis: Dict, semesters: List[Dict]) -> str:
        """Generate course completion analysis by category."""
        
        # Analyze elective progress
        elective_html = """
        <div class="section">
            <div class="section-header">📚 Course Completion by Category</div>
            <div class="section-content">
        """
        
        for category, data in analysis['elective_analysis'].items():
            required = data['required']
            completed = data['completed']
            progress_percent = min((completed / required) * 100, 100) if required > 0 else 0
            
            status_class = "status-good" if progress_percent >= 100 else "status-warning" if progress_percent >= 50 else "status-critical"
            
            category_name = category.replace('_', ' ').title()
            
            elective_html += f"""
            <div class="course-item">
                <h4>{category_name}</h4>
                <div class="progress-bar">
                    <div class="progress-fill {status_class}" style="width: {progress_percent}%">
                        {completed}/{required} credits ({progress_percent:.0f}%)
                    </div>
                </div>
            </div>
            """
        
        elective_html += """
            </div>
        </div>
        """
        
        return elective_html
    
    def _generate_validation_issues_section(self, validation_results: List[Dict]) -> str:
        """Generate validation issues section."""
        
        issues = [r for r in validation_results if not r.get("is_valid", True) and r.get("course_code") != "CREDIT_LIMIT"]
        
        if not issues:
            return """
            <div class="section">
                <div class="section-header">✅ Course Validation</div>
                <div class="section-content">
                    <div class="alert alert-success">
                        <strong>Excellent!</strong> All course registrations are valid with no prerequisite violations detected.
                    </div>
                </div>
            </div>
            """
        
        issues_html = f"""
        <div class="section">
            <div class="section-header">⚠️ Course Validation Issues</div>
            <div class="section-content">
                <div class="alert alert-warning">
                    <strong>Attention Required:</strong> {len(issues)} course registration issues were found that need review.
                </div>
        """
        
        for issue in issues:
            issues_html += f"""
            <div class="course-item failed">
                <h4>{issue.get('course_code', 'Unknown')} - {issue.get('course_name', 'Unknown Course')}</h4>
                <p><strong>Issue:</strong> {issue.get('reason', 'Unknown issue')}</p>
                <p><strong>Semester:</strong> {issue.get('semester', 'Unknown')}</p>
            </div>
            """
        
        issues_html += """
            </div>
        </div>
        """
        
        return issues_html
    
    def _generate_graduation_requirements_section(self, analysis: Dict) -> str:
        """Generate graduation requirements analysis."""
        
        # Calculate overall progress toward graduation
        total_required = sum(data['required'] for data in analysis['elective_analysis'].values())
        total_completed = sum(data['completed'] for data in analysis['elective_analysis'].values())
        
        overall_progress = (total_completed / total_required) * 100 if total_required > 0 else 0
        
        return f"""
        <div class="section">
            <div class="section-header">🎓 Graduation Requirements</div>
            <div class="section-content">
                <div class="summary-card">
                    <h3>{overall_progress:.1f}%</h3>
                    <p>Overall Progress to Graduation</p>
                </div>
                
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {overall_progress}%">
                        {total_completed}/{total_required} credits ({overall_progress:.0f}%)
                    </div>
                </div>
                
                <div class="alert alert-info">
                    <strong>Graduation Status:</strong> 
                    {"You are on track for graduation!" if overall_progress >= 80 else 
                     "Good progress toward graduation requirements." if overall_progress >= 50 else
                     "Focus needed on completing remaining requirements."}
                </div>
            </div>
        </div>
        """
    
    def _generate_recommendations_section(self, analysis: Dict, semesters: List[Dict]) -> str:
        """Generate personalized recommendations."""
        
        recommendations = []
        
        # Check for failed courses
        if analysis['failed_courses']:
            recommendations.append({
                'title': 'Address Failed Courses',
                'content': f'You have {len(analysis["failed_courses"])} failed courses that may need to be retaken. Consider retaking these courses to improve your GPA and meet graduation requirements.',
                'priority': 'high'
            })
        
        # Check elective progress
        for category, data in analysis['elective_analysis'].items():
            if data['completed'] < data['required']:
                remaining = data['required'] - data['completed']
                category_name = category.replace('_', ' ').title()
                recommendations.append({
                    'title': f'Complete {category_name} Requirements',
                    'content': f'You need {remaining} more credits in {category_name} to meet graduation requirements.',
                    'priority': 'medium'
                })
        
        # Check for schedule deviations
        if len(analysis['deviations']) > 5:
            recommendations.append({
                'title': 'Review Course Sequencing',
                'content': 'Consider meeting with an academic advisor to optimize your course sequence and ensure timely graduation.',
                'priority': 'low'
            })
        
        if not recommendations:
            recommendations.append({
                'title': 'Excellent Progress!',
                'content': 'You are making excellent progress toward graduation. Continue with your current academic plan.',
                'priority': 'good'
            })
        
        rec_html = """
        <div class="section">
            <div class="section-header">💡 Personalized Recommendations</div>
            <div class="section-content">
        """
        
        for rec in recommendations:
            priority_class = {
                'high': 'status-critical',
                'medium': 'status-warning', 
                'low': 'status-good',
                'good': 'status-good'
            }.get(rec['priority'], 'status-good')
            
            rec_html += f"""
            <div class="recommendation {priority_class}">
                <h4>{rec['title']}</h4>
                <p>{rec['content']}</p>
            </div>
            """
        
        rec_html += """
            </div>
        </div>
        """
        
        return rec_html
    
    def _generate_semester_planning_section(self, analysis: Dict, semesters: List[Dict]) -> str:
        """Generate next semester planning suggestions."""
        
        # Find missing requirements
        missing_requirements = []
        for category, data in analysis['elective_analysis'].items():
            if data['completed'] < data['required']:
                remaining = data['required'] - data['completed']
                category_name = category.replace('_', ' ').title()
                missing_requirements.append({
                    'category': category_name,
                    'credits_needed': remaining
                })
        
        planning_html = """
        <div class="section">
            <div class="section-header">📅 Next Semester Planning</div>
            <div class="section-content">
        """
        
        if missing_requirements:
            planning_html += """
            <div class="semester-plan">
                <h4>Suggested Focus Areas for Next Semester:</h4>
            """
            
            for req in missing_requirements[:3]:  # Show top 3 priorities
                planning_html += f"""
                <div class="action-item">
                    <strong>{req['category']}:</strong> Plan to take {req['credits_needed']} credits
                </div>
                """
            
            planning_html += """
            </div>
            """
        
        # Add general planning advice
        planning_html += """
        <div class="alert alert-info">
            <strong>Planning Tips:</strong>
            <ul style="margin-top: 10px; padding-left: 20px;">
                <li>Meet with your academic advisor to discuss course selection</li>
                <li>Check course prerequisites before registering</li>
                <li>Consider your workload and balance difficult courses with easier ones</li>
                <li>Plan for courses that are only offered in specific semesters</li>
            </ul>
        </div>
        
        </div>
        </div>
        """
        
        return planning_html
    
    def _generate_footer(self) -> str:
        """Generate report footer."""
        return """
        <div class="footer">
            <p>This report was generated by the KU Industrial Engineering Course Validator</p>
            <p>For questions about your academic progress, please consult with your academic advisor</p>
        </div>
        
        </div>
        </body>
        </html>
        """