#!/usr/bin/env python3
"""
PDF extraction functionality for reading transcript PDFs.
"""
import re
import logging
import PyPDF2
from datetime import datetime

logger = logging.getLogger("pdf_extractor")

class PDFExtractor:
    """Class for extracting and processing text from PDF transcripts."""
    
    def __init__(self):
        """Initialize the PDF extractor."""
        pass
    
    def extract_text_from_pdf(self, pdf_path):
        """
        Extract text content from PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted text as a string
        """
        try:
            all_text = []
            
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                
                for page in reader.pages:
                    # Extract text from the page
                    page_text = page.extract_text()
                    
                    # Skip pages with no text content
                    if not page_text or page_text.strip() == "":
                        continue
                    
                    all_text.append(page_text)
            
            # Join all text
            return "\n".join(all_text)
        
        except Exception as e:
            logger.error(f"Error extracting text from {pdf_path}: {e}")
            return ""
    
    def extract_student_info(self, text):
            """
            Extract student information from the extracted text.
            
            Args:
                text: Extracted text from PDF
                
            Returns:
                Dictionary containing student information
            """
            # Extract student ID
            student_id = "Unknown"
            id_match = re.search(r'Student No\s*(\d+)', text)
            if id_match:
                student_id = id_match.group(1).strip()
            
            # Extract name - stop at "Field of Study" 
            student_name = "Unknown"
            name_match = re.search(r'Name\s+(.*?)(?=Field of Study|Date of Admission|\n|$)', text)
            if name_match:
                student_name = name_match.group(1).strip()
            
            # Extract field of study
            field_of_study = "Unknown"
            field_match = re.search(r'Field of Study\s+(.*?)(?=Date of Admission|\n|$)', text)
            if field_match:
                field_of_study = field_match.group(1).strip()
            
            # Extract date of admission
            date_admission = "Unknown"
            date_match = re.search(r'Date of Admission\s+(.*?)(?:\n|$)', text)
            if date_match:
                date_admission = date_match.group(1).strip()
            
            return {
                "id": student_id,
                "name": student_name,
                "field_of_study": field_of_study,
                "date_admission": date_admission
            }
    
    def extract_semesters(self, text):
    """
    Extract semester data from the extracted text (IMPROVED VERSION).
    Better handles spacing issues and edge cases.
    """
    import re
    
    # More flexible semester patterns
    semester_patterns = [
        r'(First|Second)\s+Semester\s+(\d{4})',
        r'Summer\s+Session\s+(\d{4})',
        r'(First|Second)Semester(\d{4})',  # No space
        r'SummerSession(\d{4})'             # No space
    ]
    
    # IMPROVED: More robust course pattern that handles spacing issues
    # Strategy: Match course code, then grab everything until we hit a grade pattern
    course_pattern = r'(\d{8})\s*(.+?)\s+([A-FWNP][\+\-]?)\s+(\d+)'
    
    gpa_pattern = r'sem\.\s*G\.P\.A\.\s*=\s*(\d+\.\d+).*?cum\.\s*G\.P\.A\.\s*=\s*(\d+\.\d+)'
    
    # Preprocessing to fix common PDF extraction issues
    text = re.sub(r'(\d{8})([A-Z][a-z])', r'\1 \2', text)  # Add space after course code
    text = re.sub(r'([a-z])([A-Z][\+\-]?\s+\d)', r'\1 \2', text)  # Add space before grade
    
    semesters = []
    current_semester = None
    
    lines = text.split('\n')
    
    # First pass: identify semester boundaries
    semester_lines = []
    for line_num, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
            
        for pattern in semester_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                semester_lines.append((line_num, line))
                break
    
    # Second pass: extract courses between semester boundaries
    for idx, (sem_line_num, sem_line) in enumerate(semester_lines):
        # Determine end line for this semester
        end_line = semester_lines[idx + 1][0] if idx + 1 < len(semester_lines) else len(lines)
        
        # Extract semester info
        semester_match = None
        for pattern in semester_patterns:
            semester_match = re.search(pattern, sem_line, re.IGNORECASE)
            if semester_match:
                break
        
        if not semester_match:
            continue
        
        # Parse semester type and year
        groups = semester_match.groups()
        if "Summer" in sem_line:
            semester_type = "Summer"
            year = groups[0] if len(groups) == 1 else groups[1]
        else:
            semester_type = groups[0]
            year = groups[1] if len(groups) > 1 else groups[0]
        
        current_semester = {
            "semester": f"{semester_type} Semester {year}" if semester_type != "Summer" else f"Summer Session {year}",
            "semester_type": semester_type,
            "year": year,
            "year_int": int(year) if year.isdigit() else 0,
            "courses": [],
            "sem_gpa": None,
            "cum_gpa": None,
            "total_credits": 0,
            "semester_order": 0 if semester_type == "Summer" else (1 if semester_type == "First" else 2)
        }
        
        # Extract courses for this semester
        for line_num in range(sem_line_num + 1, end_line):
            line = lines[line_num].strip()
            
            if not line or "http" in line.lower():
                continue
            
            # Check for GPA
            gpa_match = re.search(gpa_pattern, line, re.IGNORECASE)
            if gpa_match:
                try:
                    current_semester["sem_gpa"] = float(gpa_match.group(1))
                    current_semester["cum_gpa"] = float(gpa_match.group(2))
                except (ValueError, IndexError):
                    pass
                continue
            
            # IMPROVED: Try to match course with better pattern
            course_match = re.search(course_pattern, line)
            
            if course_match:
                try:
                    course_code = course_match.group(1)
                    course_name = course_match.group(2).strip()
                    grade = course_match.group(3).strip()
                    credits_str = course_match.group(4)
                    
                    # Clean up course name (remove extra spaces)
                    course_name = re.sub(r'\s+', ' ', course_name)
                    
                    # Sometimes course names have trailing characters before the grade
                    # Remove any single uppercase letters at the end (likely part of grade)
                    course_name = re.sub(r'\s+[A-Z]$', '', course_name)
                    
                    # Parse credits
                    credits = int(credits_str) if credits_str.isdigit() else 0
                    
                    course_data = {
                        "code": course_code,
                        "name": course_name,
                        "grade": grade,
                        "credits": credits
                    }
                    
                    current_semester["courses"].append(course_data)
                    
                    # Count credits for non-withdrawn/non-N courses
                    if grade not in ['W', 'N', '']:
                        current_semester["total_credits"] += credits
                    
                except Exception as e:
                    print(f"Error parsing course from line '{line}': {e}")
                    continue
        
        if current_semester and current_semester["courses"]:
            semesters.append(current_semester)
    
    return semesters
    
    def process_pdf(self, pdf_path, text=None):
        """
        Process a PDF transcript and extract all data.
        
        Args:
            pdf_path: Path to the PDF file
            text: Optional pre-extracted text (used instead of extracting from PDF)
            
        Returns:
            Tuple of (student_info, semesters, extracted_text)
        """
        # Use provided text or extract from PDF
        if text is not None:
            extracted_text = text
        else:
            extracted_text = self.extract_text_from_pdf(pdf_path)
        
        if not extracted_text:
            logger.error("No text extracted from PDF")
            return {}, [], ""
        
        # Extract student info
        student_info = self.extract_student_info(extracted_text)
        
        # Extract semesters
        semesters = self.extract_semesters(extracted_text)
        
        return student_info, semesters, extracted_text
