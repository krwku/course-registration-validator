import streamlit as st
from typing import Dict, List, Optional, Any
from pathlib import Path


class UIComponents:
    """Handles all UI-related components and displays."""
    
    @staticmethod
    def display_header():
        """Display the main application header."""
        st.title("🎓 KU Industrial Engineering Course Validator")
        st.markdown("*Smart Registration Planning with Advanced Course Detection*")
        st.markdown("*Created for Raphin P. - Enhanced Schedule Analysis*")
    
    @staticmethod
    def handle_sidebar_configuration(available_course_data: Dict) -> Optional[Dict]:
        """Handle sidebar configuration and return selected course data."""
        with st.sidebar:
            st.header("⚙️ Configuration")
            
            if available_course_data:
                selected_catalog = st.selectbox(
                    "📚 Select Course Catalog",
                    options=list(available_course_data.keys()),
                    help="Choose the course catalog for validation"
                )
                
                if selected_catalog:
                    selected_course_data = available_course_data[selected_catalog]
                    st.session_state.selected_course_data = selected_course_data
                    st.success(f"✅ Using: {selected_course_data['filename']}")
                    
                    # Load course categories for classification
                    if st.session_state.course_categories is None:
                        with st.spinner("Loading course classification system..."):
                            from components.course_analyzer import CourseAnalyzer
                            analyzer = CourseAnalyzer()
                            st.session_state.course_categories = analyzer.load_course_categories()
                    
                    return selected_course_data
            
            return None
    
    @staticmethod
    def handle_pdf_upload() -> Optional[Any]:
        """Handle PDF file upload in sidebar."""
        with st.sidebar:
            st.divider()
            st.header("📁 Upload Transcript")
            
            pdf_file = st.file_uploader(
                "Upload PDF Transcript", 
                type=['pdf'],
                help="Upload student transcript PDF"
            )
            
            if pdf_file is not None:
                st.info(f"📄 File: {pdf_file.name}")
                st.info(f"📊 Size: {len(pdf_file.getvalue()) / 1024:.1f} KB")
                
                # Reset processing when new file is uploaded
                from components.session_manager import SessionManager
                if SessionManager.should_reset_for_new_file(pdf_file.name):
                    SessionManager.reset_processing_state()
            
            return pdf_file
    
    @staticmethod
    def display_student_info_and_validation(student_info: Dict, semesters: List[Dict], 
                                          validation_results: List[Dict]):
        """Display student information and validation results."""
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.header("📋 Student Information")
            st.write(f"**Student ID:** {student_info.get('id', 'Unknown')}")
            st.write(f"**Name:** {student_info.get('name', 'Unknown')}")
            st.write(f"**Field of Study:** {student_info.get('field_of_study', 'Unknown')}")
            
            st.divider()
            st.subheader("📚 Semester Summary")
            for i, sem in enumerate(semesters):
                semester_name = sem.get('semester', f'Semester {i+1}')
                course_count = len(sem.get('courses', []))
                total_credits = sem.get('total_credits', 0)
                st.write(f"• **{semester_name}:** {course_count} courses, {total_credits} credits")
        
        with col2:
            st.header("✅ Validation Results")
            
            invalid_results = [r for r in validation_results 
                             if not r.get("is_valid", True) and r.get("course_code") != "CREDIT_LIMIT"]
            total_courses = len([r for r in validation_results 
                               if r.get("course_code") != "CREDIT_LIMIT"])
            
            if len(invalid_results) == 0:
                st.success(f"🎉 **Excellent!** All {total_courses} registrations are valid!")
            else:
                st.error(f"⚠️ **Issues Found:** {len(invalid_results)} invalid registrations")
            
            if invalid_results:
                with st.expander("❌ Invalid Registrations", expanded=True):
                    for result in invalid_results:
                        st.error(f"**{result.get('semester')}:** {result.get('course_code')} - {result.get('course_name')}")
                        st.write(f"   *Issue:* {result.get('reason')}")
    
    @staticmethod
    def display_welcome_screen():
        """Display welcome screen when no PDF is uploaded."""
        st.info("📋 **Ready for advanced course validation and visualization with FIXED deviation detection!**")
        
        col_info1, col_info2 = st.columns([1, 1])
        
        with col_info1:
            st.markdown("### 🎯 How to use:")
            st.markdown("""
            1. **Select course catalog** (IE 2560 or 2565)
            2. **Upload PDF transcript** in the sidebar
            3. **Wait for processing** ⚡
            4. **View interactive visualizations** 🗂️
            5. **Download various report formats** 📋
            """)
        
        with col_info2:
            st.markdown("### 🚀 Key Features (FIXED):")
            st.markdown("• **Smart course detection** - Automatically categorizes courses")
            st.markdown("• **FIXED deviation detection** - Realistic timing analysis")
            st.markdown("• **Interactive flow chart** - Visual semester progression")
            st.markdown("• **Comprehensive Excel analysis** - Detailed credit breakdowns")
            st.markdown("• **Prerequisite validation** - Checks course requirements")
            st.markdown("• **Progress tracking** - Credit completion by category")
    
    @staticmethod
    def display_status_bar(session_manager):
        """Display status bar at the bottom of the page."""
        st.divider()
        col_status1, col_status2, col_status3 = st.columns([2, 2, 1])
        
        with col_status1:
            unidentified_count = session_manager.get_unidentified_count()
            if unidentified_count > 0:
                st.info(f"🔍 Database expansion opportunity: {unidentified_count} new courses found")
            elif session_manager.is_processing_complete():
                st.success("✅ All courses successfully classified")
        
        with col_status2:
            if session_manager.is_processing_complete():
                validation_results = session_manager.get_validation_results()
                invalid_count = len([r for r in validation_results 
                                   if not r.get("is_valid", True) and r.get("course_code") != "CREDIT_LIMIT"])
                if invalid_count > 0:
                    st.error(f"❌ {invalid_count} validation issues found")
                else:
                    st.success("✅ All validations passed")
        
        with col_status3:
            st.markdown("*Enhanced for Raphin P.*", 
                       help="Advanced course validation with enhanced deviation detection")
    
    @staticmethod
    def display_process_another_option():
        """Display option to process another PDF file."""
        st.divider()
        if st.button("🔄 Process Another PDF", type="secondary"):
            from components.session_manager import SessionManager
            SessionManager.reset_all_state()
            st.rerun()
    
    @staticmethod
    def display_credit_summary(credit_summary: Dict):
        """Display credit summary by category."""
        if not credit_summary:
            return
        
        st.divider()
        st.subheader("📊 Credit Summary by Category")
        
        col_cr1, col_cr2, col_cr3 = st.columns(3)
        
        with col_cr1:
            st.metric("IE Core", f"{credit_summary.get('ie_core', 0)}", help="Required: ~110 credits")
            st.metric("Wellness", f"{credit_summary.get('wellness', 0)}", help="Required: 7 credits")
            st.metric("Entrepreneurship", f"{credit_summary.get('entrepreneurship', 0)}", help="Required: 3 credits")
        
        with col_cr2:
            st.metric("Language & Communication", f"{credit_summary.get('language_communication', 0)}", help="Required: 15 credits")
            st.metric("Thai Citizen & Global", f"{credit_summary.get('thai_citizen_global', 0)}", help="Required: 2 credits")
            st.metric("Aesthetics", f"{credit_summary.get('aesthetics', 0)}", help="Required: 3 credits")
        
        with col_cr3:
            st.metric("Technical Electives", f"{credit_summary.get('technical_electives', 0)}", help="Variable requirement")
            st.metric("Free Electives", f"{credit_summary.get('free_electives', 0)}", help="Variable requirement")
            st.metric("Unidentified", f"{credit_summary.get('unidentified', 0)}", help="Courses needing classification", delta_color="off")
    
    @staticmethod
    def display_unidentified_courses_info(unidentified_courses: List[Dict]):
        """Display information about unidentified courses."""
        if not unidentified_courses:
            return
        
        st.info(f"🔍 **Database Expansion Opportunity:** {len(unidentified_courses)} new courses found")
        with st.expander("🔍 New Courses - Require Classification", expanded=True):
            for course in unidentified_courses:
                st.write(f"• **{course['code']}** - {course['name']} ({course['semester']}) - {course['credits']} credits")
            st.info("💡 These courses are not yet in our classification system and would benefit from being added for more accurate analysis.")


class ComponentHelpers:
    """Helper functions for UI components."""
    
    @staticmethod
    def format_course_name(name: str, max_length: int = 40) -> str:
        """Format course name to fit within specified length."""
        if len(name) <= max_length:
            return name
        return name[:max_length-3] + "..."
    
    @staticmethod
    def get_grade_color(grade: str) -> str:
        """Get color for grade display."""
        if grade in ["A", "B+", "B", "C+", "C", "D+", "D", "P"]:
            return "green"
        elif grade == "F":
            return "red"
        elif grade == "W":
            return "orange"
        else:
            return "gray"
    
    @staticmethod
    def calculate_completion_percentage(completed: int, total: int) -> float:
        """Calculate completion percentage."""
        if total == 0:
            return 0.0
        return min((completed / total) * 100, 100)
