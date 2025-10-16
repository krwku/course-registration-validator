import streamlit as st
import json
import sys
from pathlib import Path
import tempfile
import os
import traceback
import importlib

# Add modules to path
sys.path.append(str(Path(__file__).parent))

# Import our modules
from utils.pdf_processor import extract_text_from_pdf_bytes
from utils.course_data_loader import load_comprehensive_course_data
from utils.pdf_extractor import PDFExtractor
from validator import CourseRegistrationValidator

# Import refactored components
from components.course_analyzer import CourseAnalyzer
from components.flow_chart_generator import FlowChartGenerator
from components.report_generator import ReportGenerator
from components.ui_components import UIComponents
from components.session_manager import SessionManager


def main():
    """Main application entry point."""
    # Initialize page configuration
    st.set_page_config(
        page_title="KU IE Course Validator", 
        page_icon="🎓",
        layout="wide"
    )
    
    # Initialize session manager
    session_manager = SessionManager()
    session_manager.initialize_session_state()
    
    # Display header
    UIComponents.display_header()
    
    # Load course data
    try:
        available_course_data = load_comprehensive_course_data()
    except Exception as e:
        st.error(f"Error loading course data: {e}")
        available_course_data = {}
    
    # Handle sidebar configuration
    selected_course_data = UIComponents.handle_sidebar_configuration(available_course_data)
    
    if not selected_course_data:
        st.error("❌ No course data files found")
        st.stop()
    
    # Handle PDF upload and processing
    pdf_file = UIComponents.handle_pdf_upload()
    
    if pdf_file is not None and selected_course_data is not None:
        # Process PDF if not already done
        if not session_manager.is_processing_complete():
            _process_pdf_file(pdf_file, selected_course_data, session_manager)
        
        # Display results if processing is complete
        if session_manager.is_processing_complete():
            _display_results(session_manager, selected_course_data)
    else:
        # Display welcome screen
        UIComponents.display_welcome_screen()
    
    # Display status bar
    UIComponents.display_status_bar(session_manager)


def _process_pdf_file(pdf_file, selected_course_data, session_manager):
    """Process uploaded PDF file."""
    with st.spinner("🔄 Processing PDF and creating advanced course analysis..."):
        try:
            # Extract text from PDF
            pdf_bytes = pdf_file.getvalue()
            extracted_text = extract_text_from_pdf_bytes(pdf_bytes)
            
            if not extracted_text:
                st.error("❌ No text extracted from PDF. Please ensure the PDF contains readable text.")
                st.stop()
            
            # Process the extracted text
            extractor = PDFExtractor()
            student_info, semesters, _ = extractor.process_pdf(None, extracted_text)
            
            if not student_info or not semesters:
                st.error("❌ Failed to process transcript data. Please check if the PDF format is supported.")
                st.stop()
            
            # Validate courses
            validation_results = _validate_courses(semesters, selected_course_data)
            
            # Store results in session
            session_manager.store_processing_results(
                student_info, semesters, validation_results, pdf_file.name
            )
            
        except Exception as e:
            st.error(f"❌ Error during processing: {e}")
            with st.expander("Debug Information"):
                st.code(traceback.format_exc())
            st.stop()


def _validate_courses(semesters, selected_course_data):
    """Validate courses using the validator."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
        json.dump(selected_course_data['data'], tmp_file)
        tmp_path = tmp_file.name
    
    try:
        validator = CourseRegistrationValidator(tmp_path)
        passed_courses_history = validator.build_passed_courses_history(semesters)
        
        all_results = []
        
        # Validate each semester
        for i, semester in enumerate(semesters):
            # Check credit limit
            credit_valid, credit_reason = validator.validate_credit_limit(semester)
            if not credit_valid:
                all_results.append({
                    "semester": semester.get("semester", ""),
                    "semester_index": i,
                    "course_code": "CREDIT_LIMIT", 
                    "course_name": "Credit Limit Check",
                    "grade": "N/A",
                    "is_valid": True,  # Credit limits are warnings, not errors
                    "reason": credit_reason,
                    "type": "credit_limit"
                })
            
            # Validate each course
            for course in semester.get("courses", []):
                is_valid, reason = validator.validate_course(
                    course, i, semesters, passed_courses_history, all_results
                )
                
                all_results.append({
                    "semester": semester.get("semester", ""),
                    "semester_index": i,
                    "course_code": course.get("code", ""),
                    "course_name": course.get("name", ""),
                    "grade": course.get("grade", ""),
                    "is_valid": is_valid,
                    "reason": reason,
                    "type": "prerequisite"
                })
        
        # Propagate invalidation
        validator.propagate_invalidation(semesters, all_results)
        return all_results
    
    finally:
        # Clean up temp file
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def _display_results(session_manager, selected_course_data):
    """Display processing results."""
    student_info = session_manager.get_student_info()
    semesters = session_manager.get_semesters()
    validation_results = session_manager.get_validation_results()
    
    # Display student info and validation results
    UIComponents.display_student_info_and_validation(
        student_info, semesters, validation_results
    )
    
    # Initialize course analyzer
    course_analyzer = CourseAnalyzer()
    
    # Analyze courses and display summary
    course_analyzer.analyze_and_display_courses(semesters)
    
    # Generate and display visualizations
    flow_generator = FlowChartGenerator()
    flow_generator.generate_and_display_flow_chart(
        student_info, semesters, validation_results, selected_course_data
    )
    
    # Handle downloads
    report_generator = ReportGenerator()
    report_generator.display_download_section(
        student_info, semesters, validation_results, selected_course_data
    )
    
    # Process another file option
    UIComponents.display_process_another_option()

def show_extraction_diagnostics(pdf_file):
    """Show detailed extraction diagnostics"""
    import streamlit as st
    from utils.pdf_processor import extract_text_from_pdf_bytes
    from utils.pdf_extractor import PDFExtractor
    
    st.subheader("🔍 PDF Extraction Diagnostics")
    
    # Extract text
    pdf_bytes = pdf_file.getvalue()
    extracted_text = extract_text_from_pdf_bytes(pdf_bytes)
    
    # Show raw text (first 2000 chars)
    with st.expander("📄 Raw Extracted Text (first 2000 chars)"):
        st.code(extracted_text[:2000])
    
    # Process with extractor
    extractor = PDFExtractor()
    student_info, semesters, _ = extractor.process_pdf(None, extracted_text)
    
    # Show extracted data
    st.write("### Extraction Summary")
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Semesters Found", len(semesters))
        total_courses = sum(len(sem.get("courses", [])) for sem in semesters)
        st.metric("Total Courses Found", total_courses)
    
    with col2:
        st.metric("Student ID", student_info.get("id", "Not Found"))
        st.metric("Student Name", student_info.get("name", "Not Found")[:20] + "...")
    
    # Detailed semester breakdown
    st.write("### Detailed Semester Breakdown")
    for i, sem in enumerate(semesters):
        with st.expander(f"{sem.get('semester', f'Semester {i+1}')} - {len(sem.get('courses', []))} courses"):
            st.write(f"**GPA:** Sem={sem.get('sem_gpa', 'N/A')}, Cum={sem.get('cum_gpa', 'N/A')}")
            st.write(f"**Total Credits:** {sem.get('total_credits', 0)}")
            st.write("**Courses:**")
            
            for course in sem.get("courses", []):
                st.write(f"- `{course.get('code')}` {course.get('name')} | Grade: {course.get('grade')} | Credits: {course.get('credits')}")
    
    # Show potential issues
    st.write("### ⚠️ Potential Issues")
    issues = []
    
    for sem in semesters:
        if not sem.get("courses"):
            issues.append(f"❌ {sem.get('semester')} has no courses extracted")
        
        if sem.get("sem_gpa") is None:
            issues.append(f"⚠️ {sem.get('semester')} missing semester GPA")
    
    if not issues:
        st.success("✅ No obvious issues detected")
    else:
        for issue in issues:
            st.warning(issue)
            
if __name__ == "__main__":
    main()



