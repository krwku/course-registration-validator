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
        
        # Extract name
        student_name = "Unknown"
        name_match = re.search(r'Name\s+(.*?)(?:\n|$)', text)
        if name_match:
            student_name = name_match.group(1).strip()
        
        # Extract field of study
        field_of_study = "Unknown"
        field_match = re.search(r'Field of Study\s+(.*?)(?:\n|$)', text)
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
        Extract semester data from the extracted text.
        
        Args:
            text: Extracted text from PDF
            
        Returns:
            List of semester dictionaries
        """
        # Regular expressions to find semester headers and course data
        semester_pattern = r'(First|Second) Semester (\d{4})|Summer Session (\d{4})|(First|Second|Summer) (\d{4})'
        course_pattern = r'(\d{8})\s+([\w &\'\-\+\.\,\/\(\)]+?)([A-Z\+\-]+|\s+[A-Z\+\-]+)?\s+(\d+)'
        gpa_pattern = r'sem\. G\.P\.A\. = (\d+\.\d+)\s+cum\. G\.P\.A\. = (\d+\.\d+)'
        
        # Find all semesters
        semesters = []
        current_semester = None
        
        lines = text.split('\n')
        for line in lines:
            # Skip lines that appear to be URLs or footers
            if "http" in line or ".php" in line or ".html" in line:
                continue
                
            # Check for semester header
            semester_match = re.search(semester_pattern, line)
            if semester_match:
                if current_semester:
                    semesters.append(current_semester)
                
                # Extract semester type and year
                if semester_match.group(1) and semester_match.group(2):  # "First Semester 2019"
                    semester_type = semester_match.group(1)
                    year = semester_match.group(2)
                elif semester_match.group(3):  # "Summer Session 2019"
                    semester_type = "Summer"
                    year = semester_match.group(3)
                elif semester_match.group(4) and semester_match.group(5):  # "First 2019"
                    semester_type = semester_match.group(4)
                    year = semester_match.group(5)
                else:
                    semester_type = "Unknown"
                    year = "Unknown"
                
                current_semester = {
                    "semester": f"{semester_type} {year}",
                    "semester_type": semester_type,
                    "year": year,
                    "year_int": int(year) if year.isdigit() else 0,
                    "courses": [],
                    "sem_gpa": None,
                    "cum_gpa": None,
                    "total_credits": 0
                }
                
                # Assign semester order
                if semester_type == "Summer":
                    current_semester["semester_order"] = 0
                elif semester_type == "First":
                    current_semester["semester_order"] = 1
                elif semester_type == "Second":
                    current_semester["semester_order"] = 2
                else:
                    current_semester["semester_order"] = 3
                
                continue
            
            # Check for GPA info
            gpa_match = re.search(gpa_pattern, line)
            if gpa_match and current_semester:
                try:
                    current_semester["sem_gpa"] = float(gpa_match.group(1))
                    current_semester["cum_gpa"] = float(gpa_match.group(2))
                except (IndexError, ValueError):
                    pass
                continue
            
            # Check for course data if we're inside a semester
            if current_semester:
                course_match = re.search(course_pattern, line)
                if course_match:
                    try:
                        course_code = course_match.group(1)
                        course_name = course_match.group(2).strip()
                        
                        # Handle the case where the grade might have a leading space
                        grade_raw = course_match.group(3) if len(course_match.groups()) > 2 else ""
                        if grade_raw:
                            grade = grade_raw.strip()
                        else:
                            grade = ""
                        
                        credits_str = course_match.group(4) if len(course_match.groups()) > 3 else "0"
                        
                        # Parse credits
                        try:
                            credits = int(credits_str)
                        except ValueError:
                            credits = 0
                        
                        # Add course
                        current_semester["courses"].append({
                            "code": course_code,
                            "name": course_name,
                            "grade": grade,
                            "credits": credits
                        })
                        
                        # Count credits for non-withdrawn courses
                        if grade not in ['W', 'N']:
                            current_semester["total_credits"] += credits
                    
                    except Exception as e:
                        logger.error(f"Error parsing course data: {e}")
        
        # Add the last semester
        if current_semester:
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
