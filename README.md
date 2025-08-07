# KU IE Course Planner Helper

Comprehensive Streamlit web app for Industrial Engineering students at Kasetsart University to plan, track, and validate their academic progress.

## Features

### 📋 Current Features
- **PDF Transcript Upload** - Extract and analyze existing course data
- **Course Validation** - Automatic prerequisite checking
- **Interactive Flow Chart** - Visual curriculum progression
- **Credit Analysis** - Track progress by course categories
- **Smart Excel Reports** - Detailed academic analysis

### 🚀 Planned Features
- **Course Recommendation Engine** - Suggest optimal course sequences
- **Semester Planning** - Interactive course selection for upcoming terms
- **Graduation Timeline** - Project completion dates and requirements
- **GPA Forecasting** - Predict academic outcomes
- **Schedule Optimization** - Avoid time conflicts and balance workload

## Quick Start

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Current Usage

1. Upload PDF transcript in sidebar
2. Select course catalog (IE 2560 or 2565)
3. View validation results and progress analysis
4. Download interactive reports and flow charts

## File Structure

```
├── streamlit_app.py        # Main application
├── validator.py           # Course validation logic
├── course_data/          # Course catalogs (JSON)
└── utils/               # PDF processing & report generation
```

## Requirements

- Python 3.8+
- Streamlit
- PyPDF2
- Pandas
- OpenPyXL

---
*Comprehensive academic planning tool for KU Industrial Engineering students*
