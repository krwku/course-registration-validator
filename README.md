# KU IE Course Planner Helper

Comprehensive Streamlit web app for Industrial Engineering students at Kasetsart University to plan, track, and validate their academic progress.

## Features

### 📋 Current Features
- **PDF Transcript Upload** - Extract and analyze existing course data
- **Auto-Curriculum Selection** - Automatically selects curriculum based on student ID
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

## Usage

1. Upload PDF transcript in sidebar
2. Curriculum is automatically selected based on your student ID
3. View validation results and progress analysis
4. Download interactive reports and flow charts

## Course Data Structure

The course data has been redesigned for easier maintenance and automatic curriculum selection based on student IDs.

### Directory Structure
```
course_data/
├── B-IE-2560/
│   ├── courses.json      # Course definitions for 2560 curriculum
│   └── template.json     # Mandatory course structure for 2560
├── B-IE-2565/
│   ├── courses.json      # Course definitions for 2565 curriculum  
│   └── template.json     # Mandatory course structure for 2565
└── gen_ed_courses.json   # Shared general education courses
```

### Auto-Selection Logic

The system automatically selects the appropriate curriculum based on student ID:

- **Student ID 65XXXXXXXX or higher** → B-IE-2565 (newest)
- **Student ID 60-64XXXXXXXX** → B-IE-2560  
- **Student ID 59XXXXXXXX or lower** → B-IE-2560 (oldest available)
- **Default (no student ID)** → B-IE-2565 (newest)

### Streamlit Interface Features

#### Auto-Selection
- ✅ **Checkbox**: "Auto-select curriculum based on Student ID" (enabled by default)
- ✅ **Smart Detection**: Automatically selects curriculum after PDF upload
- ✅ **Manual Override**: Can disable auto-selection and choose manually
- ✅ **Visual Feedback**: Shows which curriculum was auto-selected and why

#### User Experience
1. **Before PDF Upload**: Shows newest curriculum (B-IE-2565) by default
2. **After PDF Upload**: Automatically switches to appropriate curriculum based on student ID
3. **Manual Control**: User can uncheck auto-selection to choose manually
4. **Smart Re-validation**: Automatically re-validates courses when curriculum changes
5. **Manual Re-validation**: "🔄 Re-validate with this curriculum" button for manual refresh

## For Developers

### Adding a New Curriculum (e.g., B-IE-2570)

1. Create new folder: `course_data/B-IE-2570/`
2. Add two files:
   - `courses.json` (copy from existing and modify)
   - `template.json` (copy from existing and modify)
3. Update the logic in `utils/curriculum_selector.py` if needed

### Usage Examples

```python
from utils.curriculum_selector import get_curriculum_for_student_id
from utils.course_data_loader import load_curriculum_data

# Auto-select curriculum for a student
curriculum = get_curriculum_for_student_id("6512345678")  # Returns "B-IE-2565"

# Load complete curriculum data
data = load_curriculum_data(student_id="6512345678")
courses = data['courses']
template = data['template']

# Load specific curriculum
data = load_curriculum_data("B-IE-2560")
```

### Benefits of Current Structure

- ✅ **Simple**: Only 2 levels deep, clear naming
- ✅ **Automatic**: Student ID-based curriculum selection
- ✅ **Concurrent**: Multiple curricula can be active simultaneously
- ✅ **Easy Updates**: Just replace files in the relevant folder
- ✅ **No Config**: No configuration files to maintain
- ✅ **Backward Compatible**: Existing functionality preserved

## File Structure

```
├── streamlit_app.py        # Main application
├── validator.py           # Course validation logic
├── course_data/          # Course catalogs (JSON)
│   ├── B-IE-2560/       # 2560 curriculum data
│   ├── B-IE-2565/       # 2565 curriculum data
│   └── gen_ed_courses.json
└── utils/               # PDF processing & report generation
    ├── curriculum_selector.py
    └── course_data_loader.py
```

## Requirements

- Python 3.8+
- Streamlit
- PyPDF2
- Pandas
- OpenPyXL

---
*Comprehensive academic planning tool for KU Industrial Engineering students*
