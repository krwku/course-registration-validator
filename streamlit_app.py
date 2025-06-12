import streamlit as st
import sys
from pathlib import Path

# Add your existing modules to path
sys.path.append(str(Path(__file__).parent))

# Import your existing app
from integrated_solution import LauncherApp
from app import TranscriptEditorApp

def main():
    st.set_page_config(
        page_title="Course Registration Validator", 
        page_icon="🎓",
        layout="wide"
    )
    
    st.title("🎓 Course Registration Validation System")
    st.markdown("*Created for Raphin P.*")
    
    # Simple file upload interface
    uploaded_file = st.file_uploader("Upload PDF Transcript", type=['pdf'])
    if uploaded_file:
        # Use your existing PDF processing logic
        pass

if __name__ == "__main__":
    main()