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
        ULTRA-ROBUST VERSION: Extract semester data with maximum flexibility.
        Handles various PDF extraction quirks and spacing issues.
        """
        import re
        
        # Semester detection patterns
        semester_patterns = [
            r'(First|Second)\s+Semester\s+(\d{4})',
            r'Summer\s+Session\s+(\d{4})',
            r'(First|Second)Semester(\d{4})',
            r'SummerSession(\d{4})'
        ]
        
        # Multiple course extraction strategies
        course_patterns = [
            # Pattern 1: Normal spacing with any grade format
            r'(\d{8})\s+([^\d]+?)\s+([A-Z][\+\-]?|W|N|F|P)\s+(\d+)',
            # Pattern 2: Tight spacing
            r'(\d{8})([A-Za-z][^\d]{10,80}?)([A-Z][\+\-]?|W|N|F|P)\s*(\d+)',
            # Pattern 3: Very loose - capture course code and look for grade + credit at end
            r'(\d{8})\s*(.+?)\s+([A-FWNP][\+\-]?)\s+(\d+)\s*,
        ]
        
        gpa_pattern = r'sem\.\s*G\.P\.A\.\s*=\s*(\d+\.\d+).*?cum\.\s*G\.P\.A\.\s*=\s*(\d+\.\d+)'
        
        semesters = []
        current_semester = None
        
        lines = text.split('\n')
        
        # Find all semester headers with their line numbers
        semester_markers = []
        for line_num, line in enumerate(lines):
            line_clean = line.strip()
            if not line_clean:
                continue
                
            for pattern in semester_patterns:
                match = re.search(pattern, line_clean, re.IGNORECASE)
                if match:
                    semester_markers.append((line_num, line_clean, match))
                    break
        
        # Process each semester
        for idx, (sem_line_num, sem_line, sem_match) in enumerate(semester_markers):
            # Determine end boundary
            end_line = semester_markers[idx + 1][0] if idx + 1 < len(semester_markers) else len(lines)
            
            # Parse semester info
            groups = sem_match.groups()
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
            
            # Collect all lines for this semester into a block
            semester_block = []
            for line_num in range(sem_line_num + 1, end_line):
                line = lines[line_num].strip()
                if line and "http" not in line.lower() and ".php" not in line.lower():
                    semester_block.append(line)
            
            # Process semester block
            for line in semester_block:
                # Check for GPA line
                gpa_match = re.search(gpa_pattern, line, re.IGNORECASE)
                if gpa_match:
                    try:
                        current_semester["sem_gpa"] = float(gpa_match.group(1))
                        current_semester["cum_gpa"] = float(gpa_match.group(2))
                    except (ValueError, IndexError):
                        pass
                    continue
                
                # Try all course patterns
                course_matched = False
                for pattern_num, pattern in enumerate(course_patterns):
                    course_match = re.search(pattern, line)
                    
                    if course_match:
                        try:
                            course_code = course_match.group(1).strip()
                            course_name = course_match.group(2).strip()
                            grade = course_match.group(3).strip()
                            credits_str = course_match.group(4).strip()
                            
                            # Aggressive course name cleaning
                            course_name = re.sub(r'\s+', ' ', course_name)  # normalize spaces
                            course_name = re.sub(r'^\s*[IVX]+\s*', '', course_name)  # remove leading roman numerals
                            course_name = course_name.strip()
                            
                            # Validate grade format
                            valid_grades = ['A', 'B+', 'B', 'C+', 'C', 'D+', 'D', 'F', 'W', 'N', 'P', 'I', 'S', 'U']
                            if grade not in valid_grades:
                                continue
                            
                            # Parse credits
                            credits = int(credits_str) if credits_str.isdigit() else 0
                            
                            # Validate we haven't seen this exact course code already
                            if any(c['code'] == course_code for c in current_semester['courses']):
                                continue
                            
                            course_data = {
                                "code": course_code,
                                "name": course_name,
                                "grade": grade,
                                "credits": credits
                            }
                            
                            current_semester["courses"].append(course_data)
                            
                            # Count credits
                            if grade not in ['W', 'N', '']:
                                current_semester["total_credits"] += credits
                            
                            course_matched = True
                            break  # Found match, stop trying patterns
                            
                        except (IndexError, ValueError) as e:
                            continue
                
                # If no pattern matched but line has course code, log it for debugging
                if not course_matched and re.search(r'\d{8}', line):
                    # DEBUG: Uncomment to see what's not matching
                    # print(f"UNMATCHED LINE WITH COURSE CODE: {line}")
                    pass
            
            # Only add semester if it has courses
            if current_semester["courses"]:
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
