import os
import django
import csv
import re

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'course_pilot.settings')
django.setup()

from course_pilot.courses.models import Programme, SubjectRequirement

def parse_subject_requirements(subject_string):
    """Parse subject requirements like 'MAT A(121):C+'"""
    if not subject_string or subject_string == '-':
        return [], []
    
    subjects = []
    grades = []
    
    # Split by multiple subjects if they exist
    subject_parts = subject_string.split(',')
    
    for part in subject_parts:
        part = part.strip()
        if ':' in part:
            subject_part, grade_part = part.split(':', 1)
            # Extract subject name (remove codes in parentheses)
            subject_name = re.sub(r'\([^)]*\)', '', subject_part).strip()
            subjects.append(subject_name)
            grades.append(grade_part.strip())
    
    return subjects, grades

def import_kuccps_data():
    # Clear existing data
    Programme.objects.all().delete()
    SubjectRequirement.objects.all().delete()
    
    programmes_added = 0
    skipped_rows = 0
    
    # Import from cluster points file
    with open('data/cleaned/KUCCPS_ClusterPoints_Cleaned.csv', 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header row
        
        for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is row 1)
            try:
                if len(row) < 6:
                    skipped_rows += 1
                    continue
                
                # Skip rows that contain "CUTOFF" or other non-course data
                if any('CUTOFF' in str(cell) for cell in row):
                    skipped_rows += 1
                    continue
                
                # Map columns
                programme_code = row[1]  # Column 1: programme code
                university = row[2]      # Column 2: university
                programme_name = row[3]  # Column 3: programme name
                
                # Handle cluster points - skip if invalid
                cluster_points_str = row[4]
                if not cluster_points_str or cluster_points_str == '-' or cluster_points_str.strip() == '':
                    skipped_rows += 1
                    continue
                
                try:
                    cluster_points = float(cluster_points_str)
                except ValueError:
                    skipped_rows += 1
                    continue
                
                # Skip if essential data is missing
                if not programme_code or not programme_name or not university:
                    skipped_rows += 1
                    continue
                
                # Create programme
                programme = Programme.objects.create(
                    programme_code=programme_code.strip(),
                    programme_name=programme_name.strip(),
                    university=university.strip(),
                    cluster_points=cluster_points
                )
                
                # Parse and add subject requirements from column 6
                if len(row) > 6 and row[6] and row[6] != '-':
                    subjects, grades = parse_subject_requirements(row[6])
                    
                    requirements = SubjectRequirement(
                        programme=programme,
                        subject_1=subjects[0] if len(subjects) > 0 else '',
                        grade_1=grades[0] if len(grades) > 0 else '',
                        subject_2=subjects[1] if len(subjects) > 1 else '',
                        grade_2=grades[1] if len(grades) > 1 else '',
                        subject_3=subjects[2] if len(subjects) > 2 else '',
                        grade_3=grades[2] if len(grades) > 2 else '',
                        subject_4=subjects[3] if len(subjects) > 3 else '',
                        grade_4=grades[3] if len(grades) > 3 else ''
                    )
                    requirements.save()
                
                programmes_added += 1
                
                if programmes_added % 100 == 0:
                    print(f"Added {programmes_added} programmes...")
                    
            except Exception as e:
                print(f"Error adding row {row_num}: {e}")
                skipped_rows += 1
    
    return programmes_added, skipped_rows

# Run the import
if __name__ == "__main__":
    print("Starting KUCCPS data import...")
    
    # First, let's count total rows
    with open('data/cleaned/KUCCPS_ClusterPoints_Cleaned.csv', 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        total_rows = sum(1 for row in reader) - 1  # Subtract header
    
    print(f"Total rows in CSV: {total_rows}")
    
    programmes, skipped = import_kuccps_data()
    
    print(f"\n✅ Import complete!")
    print(f"Programmes successfully added: {programmes}")
    print(f"Rows skipped (invalid data): {skipped}")
    print(f"Total programmes in database: {Programme.objects.count()}")