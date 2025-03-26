# Course Registration Validation System

A modular system for managing and validating student course registrations against university prerequisites and rules.

## Features

- **Manual Transcript Editing**: Create and edit student transcripts with a user-friendly interface
- **PDF Extraction**: Extract transcript data from PDF files as a starting point (with manual correction)
- **Course Selection**: Browse and search the course catalog
- **Prerequisite Validation**: Validate course registrations against prerequisites
- **Detailed Reports**: Generate comprehensive validation reports

## Quick Start

### Easy Installation (Recommended)

Install directly from GitHub using pip:
```
pip install git+https://github.com/Modern-research-group/course-registration-validator.git
```

After installation, you can run the application from any directory with:
```
course-validator
```

### Installation Troubleshooting

If you encounter any issues:

1. Try uninstalling and reinstalling:
```
pip uninstall -y course-registration-validator
pip install git+https://github.com/Modern-research-group/course-registration-validator.git
```

2. If using Windows and getting permission errors, run Command Prompt as Administrator.

3. For Mac/Linux users, you might need to use `pip3` instead of `pip`:
```
pip3 install git+https://github.com/Modern-research-group/course-registration-validator.git
```

### Manual Installation (Alternative)

If you prefer to run from source:

#### Prerequisites

- Python 3.8 or higher
- PyPDF2 library

#### Installation Steps (Windows)

1. **Clone the repository**:
   - Install Git from [git-scm.com](https://git-scm.com/download/win) if needed
   - Open Command Prompt and run:
   ```
   git clone https://github.com/Modern-research-group/course-registration-validator.git
   cd course-registration-validator
   ```

2. **Install the required dependencies**:
   ```
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```
   python integrated_solution.py
   ```

#### Installation Steps (Mac/Linux)

1. **Clone the repository**:
   ```
   git clone https://github.com/Modern-research-group/course-registration-validator.git
   cd course-registration-validator
   ```

2. **Install the required dependencies**:
   ```
   pip3 install -r requirements.txt
   ```

3. **Run the application**:
   ```
   python3 integrated_solution.py
   ```

## Using the Application

Once the application is running, you can:
- **Launch Transcript Editor**: Create or edit transcript data
- **Validate Transcript (JSON)**: Validate a saved transcript against prerequisites
- **Manage Course Data**: Select or add course data files
- **View Reports**: See validation results

### First-time Usage

1. Start the application with `course-validator` or `python integrated_solution.py`
2. Select "Launch Transcript Editor"
3. Use the editor to create a new transcript:
   - Enter student information
   - Add semesters
   - Add courses to each semester
4. Save your transcript
5. Return to the launcher and select "Validate Transcript"
6. Select your saved transcript to check for prerequisite issues

## Directory Structure

```
├── course_data/          # Course data files (JSON)
├── data/                 # Data management modules
│   ├── course_manager.py
│   ├── semester_manager.py
│   ├── student_manager.py
│   └── transcript_model.py
├── logs/                 # Application logs
├── reports/              # Validation reports
├── ui/                   # User interface components
│   ├── course_lookup.py
│   ├── dialogs.py
│   ├── pdf_extraction_dialog.py
│   └── validation_report.py
├── utils/                # Utility modules
│   ├── config.py
│   ├── file_operations.py
│   ├── logger_setup.py
│   ├── pdf_extractor.py
│   └── validation_adapter.py
├── app.py                # Main application module
├── integrated_solution.py  # Integrated launcher
├── transcript_editor_app.py  # Transcript editor entry point
└── validator.py          # Core validation logic
```

## Usage

### Integrated Launcher

The integrated launcher provides access to all system components:

- **Launch Transcript Editor**: Open the transcript editor for creating or editing transcript data
- **Validate Transcript (JSON)**: Validate a saved JSON transcript file
- **Manage Course Data**: Add or select course data files
- **View Reports**: Open the reports directory to view validation results

### Transcript Editor

The transcript editor allows you to:

1. **Manage Student Information**:
   - Enter student ID, name, field of study, and admission date

2. **Manage Semesters**:
   - Add, edit, and delete semesters
   - Set semester type (First, Second, or Summer) and year
   - Enter semester and cumulative GPA

3. **Manage Courses**:
   - Add, edit, and delete courses in each semester
   - Look up courses from the course catalog
   - Enter grades and credits
   - Move courses between semesters

4. **Extract from PDF**:
   - Attempt to extract transcript data from PDF files
   - Manually correct extracted text
   - Replace current transcript or append extracted semesters

5. **Validate**:
   - Validate the current transcript against prerequisites
   - View a detailed validation report

### Validation

The validation process checks:

1. **Prerequisites**: Students must have completed all prerequisite courses with passing grades
2. **Credit Limits**: Maximum credits per semester (warning only)
3. **Concurrent Registration**: Special rules for taking prerequisites concurrently

## Course Data Structure

Course data is stored in JSON format:

```json
{
  "industrial_engineering_courses": [
    {
      "code": "01234567",
      "name": "Course Name",
      "credits": "3(3-0-6)",
      "prerequisites": ["01234566"],
      "corequisites": []
    }
  ]
}
```

## Development Notes

### Modular Architecture

The system uses a modular architecture:

- **Model**: `TranscriptModel` manages the data structure
- **Managers**: `StudentManager`, `SemesterManager`, and `CourseManager` provide operations on the model
- **UI Components**: Separate modules for different UI elements
- **Utilities**: Configuration, file operations, PDF extraction, and validation

### Extending the System

To add new features:

1. Add new functionality to the appropriate manager class
2. Create or update UI components as needed
3. Update the main application to integrate the new features

## Troubleshooting

- **PDF Extraction Issues**: The PDF extraction is best-effort and may require significant manual correction
- **Missing Course Data**: Ensure course data files are in the `course_data` directory
- **Validation Errors**: Check the logs for detailed error information
- **Installation Problems**: See the Installation Troubleshooting section above

## Contributing

Contributions to improve the system are welcome:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
