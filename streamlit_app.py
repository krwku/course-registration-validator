import streamlit as st
import json
import sys
from pathlib import Path
import tempfile
import os
import io
import PyPDF2  # Add this import

# Add your existing modules to path
sys.path.append(str(Path(__file__).parent))

# Import ONLY the non-GUI parts of your code
from utils.pdf_extractor import PDFExtractor
from utils.validation_adapter import ValidationAdapter
from validator import CourseRegistrationValidator

@st.cache_data
def load_available_course_data():
    """Load all available course data files from the repository"""
    course_data_dir = Path(__file__).parent / "course_data"
    available_files = {}
    
    if course_data_dir.exists():
        for json_file in course_data_dir.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Create a friendly name for the dropdown
                file_name = json_file.stem
                if "2560" in file_name:
                    display_name = "Industrial Engineering 2560 (2017-2021)"
                elif "2565" in file_name:
                    display_name = "Industrial Engineering 2565 (2022-2026)"
                else:
                    display_name = file_name
                
                available_files[display_name] = {
                    'data': data,
                    'filename': json_file.name,
                    'path': str(json_file)
                }
            except Exception as e:
                st.error(f"Error loading {json_file.name}: {e}")
    
    return available_files

def extract_text_from_pdf_bytes(pdf_bytes):
    """Extract text from PDF bytes using PyPDF2"""
    try:
        # Create a BytesIO object from the uploaded file
        pdf_file = io.BytesIO(pdf_bytes)
        
        # Create PDF reader
        reader = PyPDF2.PdfReader(pdf_file)
        
        all_text = []
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text and page_text.strip():
                all_text.append(page_text)
        
        return "\n".join(all_text)
    
    except Exception as e:
        st.error(f"Error extracting text from PDF: {e}")
        return ""

def main():
    st.set_page_config(
        page_title="Course Registration Validator", 
        page_icon="🎓",
        layout="wide"
    )
    
    st.title("🎓 Course Registration Validation System")
    st.markdown("*Created for Raphin P.*")
    
    # Initialize session state
    if 'student_info' not in st.session_state:
        st.session_state.student_info = {}
    if 'semesters' not in st.session_state:
        st.session_state.semesters = []
    if 'selected_course_data' not in st.session_state:
        st.session_state.selected_course_data = None
    if 'extracted_text' not in st.session_state:
        st.session_state.extracted_text = ""
    
    # Load available course data
    available_course_data = load_available_course_data()
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Course data selection (no upload needed!)
        if available_course_data:
            selected_catalog = st.selectbox(
                "📚 Select Course Catalog",
                options=list(available_course_data.keys()),
                help="Choose the course catalog for validation"
            )
            
            if selected_catalog:
                st.session_state.selected_course_data = available_course_data[selected_catalog]
                st.success(f"✅ Using: {available_course_data[selected_catalog]['filename']}")
        else:
            st.error("❌ No course data files found in repository")
            st.stop()
        
        st.divider()
        
        # PDF upload
        st.header("📁 Upload Transcript")
        pdf_file = st.file_uploader(
            "Upload PDF Transcript", 
            type=['pdf'],
            help="Upload student transcript PDF for validation"
        )
        
        # Show PDF info if uploaded
        if pdf_file is not None:
            st.info(f"📄 File: {pdf_file.name}")
            st.info(f"📊 Size: {len(pdf_file.getvalue()) / 1024:.1f} KB")
    
    # Main content area
    if pdf_file is not None and st.session_state.selected_course_data is not None:
        
        # Two-column layout
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.header("📄 PDF Processing")
            
            # Step 1: Extract raw text
            if st.button("🔍 Step 1: Extract Text from PDF", type="primary"):
                with st.spinner("Extracting text from PDF..."):
                    pdf_bytes = pdf_file.getvalue()
                    extracted_text = extract_text_from_pdf_bytes(pdf_bytes)
                    
                    if extracted_text:
                        st.session_state.extracted_text = extracted_text
                        st.success(f"✅ Extracted {len(extracted_text)} characters from PDF")
                        
                        # Show first 500 characters as preview
                        with st.expander("📖 Text Preview (First 500 characters)"):
                            st.text(extracted_text[:500] + "..." if len(extracted_text) > 500 else extracted_text)
                    else:
                        st.error("❌ No text extracted from PDF")
                        st.warning("This might be a scanned/image PDF. Try using a text-based PDF.")
            
            # Step 2: Process extracted text
            if st.session_state.extracted_text:
                st.divider()
                
                if st.button("🔄 Step 2: Process Extracted Text", type="secondary"):
                    with st.spinner("Processing extracted text..."):
                        try:
                            # Use your existing PDF extractor with the extracted text
                            extractor = PDFExtractor()
                            
                            # Process the extracted text
                            student_info, semesters, _ = extractor.process_pdf(None, st.session_state.extracted_text)
                            
                            if student_info and semesters:
                                st.session_state.student_info = student_info
                                st.session_state.semesters = semesters
                                st.success("✅ Data processed successfully!")
                                
                                # Show extracted info
                                with st.expander("📋 Extracted Student Information", expanded=True):
                                    col_a, col_b = st.columns(2)
                                    with col_a:
                                        st.write(f"**Student ID:** {student_info.get('id', 'Unknown')}")
                                        st.write(f"**Name:** {student_info.get('name', 'Unknown')}")
                                    with col_b:
                                        st.write(f"**Field of Study:** {student_info.get('field_of_study', 'Unknown')}")
                                        st.write(f"**Date of Admission:** {student_info.get('date_admission', 'Unknown')}")
                                
                                with st.expander("📚 Extracted Semesters Summary"):
                                    st.write(f"**Total Semesters Found:** {len(semesters)}")
                                    for i, sem in enumerate(semesters):
                                        semester_name = sem.get('semester', f'Semester {i+1}')
                                        course_count = len(sem.get('courses', []))
                                        total_credits = sem.get('total_credits', 0)
                                        st.write(f"• **{semester_name}:** {course_count} courses, {total_credits} credits")
                            else:
                                st.error("❌ Failed to process extracted text")
                                st.info("💡 The text might not be in the expected transcript format")
                                
                                # Show debugging info
                                with st.expander("🔍 Debug: Show Raw Extracted Text"):
                                    st.text_area("Raw Text", st.session_state.extracted_text, height=200)
                                
                        except Exception as e:
                            st.error(f"❌ Error processing text: {e}")
                            with st.expander("🔍 Debug Information"):
                                st.exception(e)
                                st.text_area("Raw Text", st.session_state.extracted_text, height=200)
        
        with col2:
            st.header("✅ Validation")
            
            if st.session_state.student_info and st.session_state.semesters:
                
                # Show validation button
                if st.button("🔍 Validate Transcript", type="primary"):
                    with st.spinner("Validating transcript against course requirements..."):
                        try:
                            # Create temporary course data file for validator
                            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
                                json.dump(st.session_state.selected_course_data['data'], tmp_file)
                                tmp_path = tmp_file.name
                            
                            # Use your existing validation logic
                            validator = CourseRegistrationValidator(tmp_path)
                            
                            # Build passed courses history
                            passed_courses_history = validator.build_passed_courses_history(st.session_state.semesters)
                            
                            # Validate each semester
                            all_results = []
                            for i, semester in enumerate(st.session_state.semesters):
                                # Check credit limits
                                credit_valid, credit_reason = validator.validate_credit_limit(semester)
                                if not credit_valid:
                                    all_results.append({
                                        "semester": semester.get("semester", ""),
                                        "semester_index": i,
                                        "course_code": "CREDIT_LIMIT",
                                        "course_name": "Credit Limit Check",
                                        "grade": "N/A",
                                        "is_valid": True,  # Just a warning
                                        "reason": credit_reason,
                                        "type": "credit_limit"
                                    })
                                
                                # Validate each course
                                for course in semester.get("courses", []):
                                    is_valid, reason = validator.validate_course(
                                        course, i, st.session_state.semesters, passed_courses_history, all_results
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
                            validator.propagate_invalidation(st.session_state.semesters, all_results)
                            
                            # Clean up temp file
                            os.unlink(tmp_path)
                            
                            # Display results
                            invalid_results = [r for r in all_results if not r.get("is_valid", True) and r.get("course_code") != "CREDIT_LIMIT"]
                            credit_warnings = [r for r in all_results if r.get("course_code") == "CREDIT_LIMIT"]
                            
                            # Summary
                            total_courses = len([r for r in all_results if r.get("course_code") != "CREDIT_LIMIT"])
                            
                            if len(invalid_results) == 0:
                                st.success(f"🎉 **Excellent!** All {total_courses} course registrations are valid!")
                            else:
                                st.error(f"⚠️ **Issues Found:** {len(invalid_results)} invalid registrations out of {total_courses} total")
                            
                            # Show credit warnings if any
                            if credit_warnings:
                                with st.expander("⚠️ Credit Load Warnings"):
                                    for warning in credit_warnings:
                                        st.warning(f"📊 {warning.get('semester')}: {warning.get('reason')}")
                            
                            # Show invalid courses if any
                            if invalid_results:
                                with st.expander("❌ Invalid Course Registrations", expanded=True):
                                    for result in invalid_results:
                                        st.error(f"**{result.get('semester')}:** {result.get('course_code')} - {result.get('course_name')}")
                                        st.write(f"   *Issue:* {result.get('reason')}")
                            
                            # Generate downloadable report
                            st.divider()
                            st.subheader("📥 Download Reports")
                            
                            col_download1, col_download2 = st.columns(2)
                            
                            with col_download1:
                                # Text report
                                report_text = validator.generate_summary_report(
                                    st.session_state.student_info, 
                                    st.session_state.semesters, 
                                    all_results
                                )
                                
                                st.download_button(
                                    label="📄 Download Text Report",
                                    data=report_text,
                                    file_name=f"validation_report_{st.session_state.student_info.get('id', 'unknown')}.txt",
                                    mime="text/plain",
                                    help="Detailed validation report in text format"
                                )
                            
                            with col_download2:
                                # JSON data export
                                export_data = {
                                    "student_info": st.session_state.student_info,
                                    "semesters": st.session_state.semesters,
                                    "validation_results": all_results,
                                    "course_catalog_used": st.session_state.selected_course_data['filename']
                                }
                                
                                st.download_button(
                                    label="💾 Download JSON Data",
                                    data=json.dumps(export_data, indent=2),
                                    file_name=f"transcript_data_{st.session_state.student_info.get('id', 'unknown')}.json",
                                    mime="application/json",
                                    help="Complete transcript and validation data"
                                )
                                
                        except Exception as e:
                            st.error(f"❌ Validation error: {e}")
                            with st.expander("🔍 Error Details"):
                                st.exception(e)
            else:
                st.info("👆 Extract and process PDF data first to enable validation")
    
    else:
        # Welcome message and instructions
        st.info("📋 **Ready to validate transcripts!**")
        
        col_info1, col_info2 = st.columns([1, 1])
        
        with col_info1:
            st.markdown("### 🎯 How to use:")
            st.markdown("""
            1. **Select course catalog** (already loaded!)
            2. **Upload PDF transcript** in the sidebar
            3. **Extract text** from the PDF
            4. **Process extracted text** into transcript data
            5. **Validate** against course requirements
            6. **Download** validation report
            """)
        
        with col_info2:
            st.markdown("### 📚 Available Catalogs:")
            if available_course_data:
                for catalog_name, info in available_course_data.items():
                    st.markdown(f"• {catalog_name}")
            
            st.markdown("### 📄 Supported PDF Format:")
            st.markdown("• Academic transcripts with student info and course grades")
            st.markdown("• Text-based PDFs (not scanned images)")

if __name__ == "__main__":
    main()
