import streamlit as st
import json
import tempfile
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from utils.excel_generator import create_smart_registration_excel
from validator import CourseRegistrationValidator


class ReportGenerator:
    """Handles generation and download of various report formats."""
    
    def __init__(self):
        pass
    
    def generate_excel_report(self, student_info: Dict, semesters: List[Dict], 
                             validation_results: List[Dict]) -> tuple[bytes, int]:
        """Generate Excel report with comprehensive analysis."""
        try:
            return create_smart_registration_excel(student_info, semesters, validation_results)
        except Exception as e:
            raise Exception(f"Error creating Excel report: {e}")
    
    def generate_text_report(self, student_info: Dict, semesters: List[Dict], 
                           validation_results: List[Dict], course_data_path: str) -> str:
        """Generate text-based validation report."""
        try:
            validator = CourseRegistrationValidator(course_data_path)
            return validator.generate_summary_report(student_info, semesters, validation_results)
        except Exception as e:
            raise Exception(f"Error creating text report: {e}")
    
    def generate_json_export(self, student_info: Dict, semesters: List[Dict], 
                           validation_results: List[Dict], selected_course_data: Dict, 
                           unidentified_count: int) -> str:
        """Generate JSON export with all data."""
        try:
            export_data = {
                "student_info": student_info,
                "semesters": semesters,
                "validation_results": validation_results,
                "unidentified_count": unidentified_count,
                "metadata": {
                    "course_catalog": selected_course_data.get('filename', ''),
                    "generated_timestamp": str(st.session_state.get('processing_timestamp', 'unknown'))
                }
            }
            
            return json.dumps(export_data, indent=2)
        except Exception as e:
            raise Exception(f"Error creating JSON export: {e}")
    
    def generate_flow_chart_html(self, student_info: Dict, semesters: List[Dict], 
                               validation_results: List[Dict], selected_course_data: Dict) -> tuple[str, int]:
        """Generate HTML flow chart for download."""
        try:
            from components.flow_chart_generator import FlowChartGenerator
            flow_generator = FlowChartGenerator()
            return flow_generator.create_enhanced_template_flow_html(
                student_info, semesters, validation_results, selected_course_data
            )
        except Exception as e:
            raise Exception(f"Error creating HTML flow chart: {e}")
    
    def display_download_section(self, student_info: Dict, semesters: List[Dict], 
                               validation_results: List[Dict], selected_course_data: Dict):
        """Display the download section with all available report formats."""
        st.divider()
        st.header("📥 Download Reports")
        
        col_dl1, col_dl2, col_dl3, col_dl4 = st.columns(4)
        
        # Excel Report
        with col_dl1:
            self._handle_excel_download(student_info, semesters, validation_results)
        
        # HTML Flow Chart
        with col_dl2:
            self._handle_flow_chart_download(student_info, semesters, validation_results, selected_course_data)
        
        # Text Report
        with col_dl3:
            self._handle_text_report_download(student_info, semesters, validation_results, selected_course_data)
        
        # JSON Export
        with col_dl4:
            self._handle_json_export_download(student_info, semesters, validation_results, selected_course_data)
    
    def _handle_excel_download(self, student_info: Dict, semesters: List[Dict], 
                              validation_results: List[Dict]):
        """Handle Excel report download."""
        try:
            with st.spinner("Creating smart Excel analysis..."):
                excel_bytes, excel_unidentified = self.generate_excel_report(
                    student_info, semesters, validation_results
                )
            
            if excel_bytes:
                st.download_button(
                    label="📋 Smart Excel Analysis",
                    data=excel_bytes,
                    file_name=f"KU_IE_smart_analysis_{student_info.get('id', 'unknown')}.xlsx",
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
    
    def _handle_flow_chart_download(self, student_info: Dict, semesters: List[Dict], 
                                   validation_results: List[Dict], selected_course_data: Dict):
        """Handle HTML flow chart download."""
        try:
            flow_html, flow_unidentified = self.generate_flow_chart_html(
                student_info, semesters, validation_results, selected_course_data
            )
            
            st.download_button(
                label="🗂️ Flow Chart (HTML)",
                data=flow_html.encode('utf-8'),
                file_name=f"curriculum_flow_{student_info.get('id', 'unknown')}.html",
                mime="text/html",
                help="Interactive semester-based curriculum flow chart with enhanced deviation detection",
                use_container_width=True
            )
            
            if flow_unidentified > 0:
                st.warning(f"⚠️ {flow_unidentified} unidentified")
                
        except Exception as e:
            st.error(f"❌ Flow chart error: {str(e)[:50]}...")
    
    def _handle_text_report_download(self, student_info: Dict, semesters: List[Dict], 
                                    validation_results: List[Dict], selected_course_data: Dict):
        """Handle text report download."""
        try:
            course_data_path = str(Path(__file__).parent.parent / "course_data" / selected_course_data['filename'])
            report_text = self.generate_text_report(
                student_info, semesters, validation_results, course_data_path
            )
            
            st.download_button(
                label="📄 Validation Report",
                data=report_text,
                file_name=f"validation_report_{student_info.get('id', 'unknown')}.txt",
                mime="text/plain",
                help="Detailed prerequisite validation report",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"❌ Report error: {str(e)[:50]}...")
    
    def _handle_json_export_download(self, student_info: Dict, semesters: List[Dict], 
                                    validation_results: List[Dict], selected_course_data: Dict):
        """Handle JSON export download."""
        try:
            unidentified_count = st.session_state.get('unidentified_count', 0)
            json_data = self.generate_json_export(
                student_info, semesters, validation_results, selected_course_data, unidentified_count
            )
            
            st.download_button(
                label="💾 Raw Data (JSON)",
                data=json_data,
                file_name=f"transcript_data_{student_info.get('id', 'unknown')}.json",
                mime="application/json",
                help="Raw extracted and validated data",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"❌ JSON error: {str(e)[:50]}...")


class ReportFormatter:
    """Helper class for formatting various report elements."""
    
    @staticmethod
    def format_student_summary(student_info: Dict) -> str:
        """Format student summary for reports."""
        return f"""
        Student ID: {student_info.get('id', 'Unknown')}
        Name: {student_info.get('name', 'Unknown')}
        Field of Study: {student_info.get('field_of_study', 'Unknown')}
        Date of Admission: {student_info.get('date_admission', 'Unknown')}
        """
    
    @staticmethod
    def format_semester_summary(semesters: List[Dict]) -> str:
        """Format semester summary for reports."""
        summary_lines = []
        
        for i, semester in enumerate(semesters):
            semester_name = semester.get('semester', f'Semester {i+1}')
            course_count = len(semester.get('courses', []))
            total_credits = semester.get('total_credits', 0)
            gpa = semester.get('cum_gpa', 'N/A')
            
            summary_lines.append(f"{semester_name}: {course_count} courses, {total_credits} credits, GPA: {gpa}")
        
        return "\n".join(summary_lines)
    
    @staticmethod
    def format_validation_summary(validation_results: List[Dict]) -> str:
        """Format validation summary for reports."""
        total_validations = len([r for r in validation_results if r.get("course_code") != "CREDIT_LIMIT"])
        invalid_count = len([r for r in validation_results 
                           if not r.get("is_valid", True) and r.get("course_code") != "CREDIT_LIMIT"])
        
        return f"""
        Total Validations: {total_validations}
        Invalid Registrations: {invalid_count}
        Success Rate: {((total_validations - invalid_count) / total_validations * 100):.1f}%
        """
    
    @staticmethod
    def format_course_list(courses: List[Dict], include_grades: bool = True) -> str:
        """Format a list of courses for display."""
        course_lines = []
        
        for course in courses:
            line = f"{course.get('code', 'Unknown')}: {course.get('name', 'Unknown Course')}"
            if include_grades and course.get('grade'):
                line += f" (Grade: {course['grade']})"
            if course.get('credits'):
                line += f" - {course['credits']} credits"
            
            course_lines.append(line)
        
        return "\n".join(course_lines)


class ReportMetrics:
    """Helper class for calculating report metrics."""
    
    @staticmethod
    def calculate_completion_metrics(semesters: List[Dict]) -> Dict:
        """Calculate various completion metrics."""
        total_courses = 0
        completed_courses = 0
        failed_courses = 0
        withdrawn_courses = 0
        current_courses = 0
        total_credits = 0
        completed_credits = 0
        
        for semester in semesters:
            for course in semester.get('courses', []):
                total_courses += 1
                credits = course.get('credits', 0)
                total_credits += credits
                grade = course.get('grade', '')
                
                if grade in ["A", "B+", "B", "C+", "C", "D+", "D", "P"]:
                    completed_courses += 1
                    completed_credits += credits
                elif grade == "F":
                    failed_courses += 1
                elif grade == "W":
                    withdrawn_courses += 1
                elif grade in ["N", ""]:
                    current_courses += 1
        
        return {
            "total_courses": total_courses,
            "completed_courses": completed_courses,
            "failed_courses": failed_courses,
            "withdrawn_courses": withdrawn_courses,
            "current_courses": current_courses,
            "total_credits": total_credits,
            "completed_credits": completed_credits,
            "completion_rate": (completed_courses / total_courses * 100) if total_courses > 0 else 0
        }
    
    @staticmethod
    def calculate_gpa_trend(semesters: List[Dict]) -> List[float]:
        """Calculate GPA trend over semesters."""
        gpa_trend = []
        
        for semester in semesters:
            gpa = semester.get('cum_gpa')
            if isinstance(gpa, (int, float)):
                gpa_trend.append(float(gpa))
            elif isinstance(gpa, str) and gpa != "N/A":
                try:
                    gpa_trend.append(float(gpa))
                except ValueError:
                    gpa_trend.append(0.0)
            else:
                gpa_trend.append(0.0)
        
        return gpa_trend
    
    @staticmethod
    def identify_problem_areas(validation_results: List[Dict]) -> Dict:
        """Identify common problem areas in validation."""
        problem_types = {}
        
        for result in validation_results:
            if not result.get("is_valid", True):
                problem_type = result.get("type", "unknown")
                reason = result.get("reason", "Unknown issue")
                
                if problem_type not in problem_types:
                    problem_types[problem_type] = []
                
                problem_types[problem_type].append({
                    "course": result.get("course_code", "Unknown"),
                    "semester": result.get("semester", "Unknown"),
                    "reason": reason
                })
        
        return problem_types
    
