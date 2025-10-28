import streamlit as st
from typing import Dict, List, Any, Optional


class SessionManager:
    """Manages Streamlit session state for the application."""
    
    @staticmethod
    def initialize_session_state():
        """Initialize session state variables."""
        if 'student_info' not in st.session_state:
            st.session_state.student_info = {}
        if 'semesters' not in st.session_state:
            st.session_state.semesters = []
        if 'validation_results' not in st.session_state:
            st.session_state.validation_results = []
        if 'selected_course_data' not in st.session_state:
            st.session_state.selected_course_data = None
        if 'processing_complete' not in st.session_state:
            st.session_state.processing_complete = False
        if 'unidentified_count' not in st.session_state:
            st.session_state.unidentified_count = 0
        if 'course_categories' not in st.session_state:
            st.session_state.course_categories = None
    
    @staticmethod
    def is_processing_complete() -> bool:
        """Check if PDF processing is complete."""
        return st.session_state.get('processing_complete', False)
    
    @staticmethod
    def store_processing_results(student_info: Dict, semesters: List[Dict], 
                               validation_results: List[Dict], pdf_name: str):
        """Store processing results in session state."""
        st.session_state.student_info = student_info
        st.session_state.semesters = semesters
        st.session_state.validation_results = validation_results
        st.session_state.processing_complete = True
        st.session_state.last_pdf_name = pdf_name
    
    @staticmethod
    def get_student_info() -> Dict:
        """Get student information from session state."""
        return st.session_state.get('student_info', {})
    
    @staticmethod
    def get_semesters() -> List[Dict]:
        """Get semesters data from session state."""
        return st.session_state.get('semesters', [])
    
    @staticmethod
    def get_validation_results() -> List[Dict]:
        """Get validation results from session state."""
        return st.session_state.get('validation_results', [])
    
    @staticmethod
    def get_unidentified_count() -> int:
        """Get count of unidentified courses."""
        return st.session_state.get('unidentified_count', 0)
    
    @staticmethod
    def set_unidentified_count(count: int):
        """Set count of unidentified courses."""
        st.session_state.unidentified_count = count
    
    @staticmethod
    def get_course_categories() -> Optional[Dict]:
        """Get course categories from session state."""
        return st.session_state.get('course_categories')
    
    @staticmethod
    def set_course_categories(categories: Dict):
        """Set course categories in session state."""
        st.session_state.course_categories = categories
    
    @staticmethod
    def reset_processing_state():
        """Reset processing-related session state."""
        st.session_state.processing_complete = False
        st.session_state.student_info = {}
        st.session_state.semesters = []
        st.session_state.validation_results = []
        st.session_state.unidentified_count = 0
        # Reset curriculum validation tracking
        if 'last_validation_curriculum' in st.session_state:
            del st.session_state.last_validation_curriculum
    
    @staticmethod
    def should_reset_for_new_file(pdf_name: str) -> bool:
        """Check if processing should be reset for a new file."""
        last_pdf = st.session_state.get('last_pdf_name')
        return last_pdf is None or last_pdf != pdf_name
    
    @staticmethod
    def reset_all_state():
        """Reset all session state variables."""
        keys_to_reset = [
            'processing_complete', 'student_info', 'semesters', 
            'validation_results', 'unidentified_count', 'last_pdf_name'
        ]
        
        for key in keys_to_reset:
            if key in st.session_state:
                if key in ['student_info']:
                    st.session_state[key] = {}
                elif key in ['semesters', 'validation_results']:
                    st.session_state[key] = []
                elif key == 'unidentified_count':
                    st.session_state[key] = 0
                elif key == 'processing_complete':
                    st.session_state[key] = False
                else:
                    del st.session_state[key]
