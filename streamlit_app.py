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

def analyze_pdf_line_by_line(pdf_file):
    """Analyze PDF extraction line by line to find missing courses"""
    import streamlit as st
    import re
    from utils.pdf_processor import extract_text_from_pdf_bytes
    
    st.subheader("🔬 Line-by-Line PDF Analysis")
    
    # Extract text
    pdf_bytes = pdf_file.getvalue()
    text = extract_text_from_pdf_bytes(pdf_bytes)
    
    lines = text.split('\n')
    
    # Find semester boundaries
    semester_pattern = r'(First|Second|Summer).*(Semester|Session).*(\d{4})'
    semester_lines = []
    
    for i, line in enumerate(lines):
        if re.search(semester_pattern, line, re.IGNORECASE):
            semester_lines.append(i)
            st.success(f"**Line {i}:** SEMESTER FOUND - {line.strip()}")
    
    # Analyze lines between first two semesters
    if len(semester_lines) >= 2:
        start = semester_lines[0]
        end = semester_lines[1]
        
        st.write(f"### Analyzing lines {start} to {end} (First Semester)")
        
        course_pattern = r'\d{8}'
        matched_lines = []
        unmatched_lines = []
        
        for i in range(start + 1, end):
            line = lines[i].strip()
            if not line or len(line) < 10:
                continue
            
            if re.search(course_pattern, line):
                # This line has a course code - try to parse it
                patterns_to_try = [
                    r'(\d{8})\s+([^\d]+?)\s+([A-Z][\+\-]?|W|N|F|P)\s+(\d+)',
                    r'(\d{8})([A-Za-z][^\d]{10,80}?)([A-Z][\+\-]?|W|N|F|P)\s*(\d+)',
                    r'(\d{8})\s*(.+?)\s+([A-FWNP][\+\-]?)\s+(\d+)\s*$'
                ]
                
                matched = False
                for pattern_num, pattern in enumerate(patterns_to_try):
                    match = re.search(pattern, line)
                    if match:
                        matched_lines.append((i, line, match.groups(), pattern_num))
                        matched = True
                        break
                
                if not matched:
                    unmatched_lines.append((i, line))
        
        # Show matched
        st.write("#### ✅ Successfully Matched Course Lines:")
        for i, line, groups, pattern_num in matched_lines:
            with st.expander(f"Line {i} (Pattern {pattern_num + 1})"):
                st.code(line)
                st.write(f"- **Code:** {groups[0]}")
                st.write(f"- **Name:** {groups[1]}")
                st.write(f"- **Grade:** {groups[2]}")
                st.write(f"- **Credits:** {groups[3]}")
        
        st.metric("Matched Courses", len(matched_lines))
        
        # Show unmatched
        if unmatched_lines:
            st.write("#### ❌ Lines with Course Codes that FAILED to Match:")
            st.error(f"Found {len(unmatched_lines)} lines with course codes that couldn't be parsed!")
            
            for i, line in unmatched_lines:
                with st.expander(f"❌ Line {i} - UNMATCHED"):
                    st.code(line)
                    
                    # Show what we can detect
                    code_match = re.search(r'(\d{8})', line)
                    if code_match:
                        st.write(f"- **Course Code Found:** {code_match.group(1)}")
                    
                    # Try to find grade-like patterns
                    grade_match = re.search(r'\b([A-F][\+\-]?|W|N|P)\b', line)
                    if grade_match:
                        st.write(f"- **Possible Grade:** {grade_match.group(1)}")
                    
                    # Find numbers that could be credits
                    credit_match = re.findall(r'\b(\d)\b', line)
                    if credit_match:
                        st.write(f"- **Possible Credits:** {credit_match}")
                    
                    st.warning("💡 Copy this line and share it so we can fix the pattern!")
            
            st.metric("⚠️ Unmatched Course Lines", len(unmatched_lines))
        else:
            st.success("✅ All course lines successfully matched!")
    
    # Allow user to test custom patterns
    st.write("### 🧪 Test Custom Pattern")
    test_line = st.text_input("Paste a problematic line here:")
    custom_pattern = st.text_input(
        "Test your regex pattern:", 
        value=r'(\d{8})\s+(.+?)\s+([A-Z][\+\-]?|W|N|F|P)\s+(\d+)'
    )
    
    if test_line and custom_pattern:
        try:
            match = re.search(custom_pattern, test_line)
            if match:
                st.success("✅ Pattern matched!")
                st.write("**Groups:**")
                for i, group in enumerate(match.groups()):
                    st.write(f"{i+1}. {group}")
            else:
                st.error("❌ Pattern did not match")
        except Exception as e:
            st.error(f"Pattern error: {e}")

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

    if pdf_file is not None:
        if st.sidebar.button("🔬 Analyze Line-by-Line"):
            analyze_pdf_line_by_line(pdf_file)
    
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
            
if __name__ == "__main__":
    main()








