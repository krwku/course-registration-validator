# Course Registration Validation System

A modular system for managing and validating student course registrations against university prerequisites and rules.

## Features

- **Manual Transcript Editing**: Create and edit student transcripts with a user-friendly interface
- **PDF Extraction**: Extract transcript data from PDF files as a starting point (with manual correction)
- **Course Selection**: Browse and search the course catalog
- **Prerequisite Validation**: Validate course registrations against prerequisites
- **Detailed Reports**: Generate comprehensive validation reports

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

## Installation

### Prerequisites

- Python 3.8 or higher
- Required packages: `tkinter`, `PyPDF2`

### Setup

1. Clone or download this repository to your local machine
2. Install required packages:
   ```bash
   pip install PyPDF2
   ```
3. Run the integrated launcher:
   ```bash
   python integrated_solution.py
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

## Contributing

Contributions to improve the system are welcome:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
