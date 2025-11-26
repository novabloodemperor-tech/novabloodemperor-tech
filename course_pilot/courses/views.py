from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import HttpResponse
import csv
import os
import io
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch

# Load all programmes from CSV file
def load_all_programmes():
    programmes = []
    
    possible_paths = [
        "data/cleaned/KUCCPS_ClusterPoints_Cleaned.csv",
        "/opt/render/project/src/data/cleaned/KUCCPS_ClusterPoints_Cleaned.csv",
        "KUCCPS_ClusterPoints_Cleaned.csv"
    ]
    
    csv_file = None
    for path in possible_paths:
        if os.path.exists(path):
            csv_file = path
            break
    
    if not csv_file:
        print("❌ CSV file not found in any location")
        raise FileNotFoundError("KUCCPS_ClusterPoints_Cleaned.csv file not found. Please check if the file exists in data/cleaned/ directory.")
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)
            
            for row_num, row in enumerate(reader, start=2):
                if len(row) >= 5 and row[1] and row[3]:
                    try:
                        programme_code = row[1].strip()
                        programme_name = row[3].strip()
                        university = row[2].strip()
                        
                        cluster_points_str = row[4].strip()
                        if cluster_points_str and cluster_points_str != '-':
                            cluster_points = float(cluster_points_str)
                        else:
                            cluster_points = 0.0
                        
                        programmes.append({
                            'programme_code': programme_code,
                            'programme_name': programme_name,
                            'university': university,
                            'cluster_points': cluster_points
                        })
                    except Exception as e:
                        print(f"⚠️ Skipping row {row_num} due to error: {e}")
                        continue
        
        if not programmes:
            raise ValueError("No valid programmes found in CSV file. File might be empty or incorrectly formatted.")
            
        print(f"✅ Loaded {len(programmes)} programmes from CSV")
        return programmes
        
    except Exception as e:
        print(f"❌ Error reading CSV file: {e}")
        raise Exception(f"Failed to load programmes from CSV: {str(e)}")

# Load programmes - will raise exception if fails
try:
    ALL_PROGRAMMES = load_all_programmes()
    print("✅ Programme data loaded successfully")
except Exception as e:
    print(f"❌ CRITICAL ERROR: {e}")
    ALL_PROGRAMMES = []
    # Don't set test data - let the error propagate

def extract_actual_cluster_mappings():
    """
    Extract ACTUAL programme-to-cluster mappings from your KUCCPS document
    """
    print("🔍 Extracting ACTUAL cluster mappings from your KUCCPS document...")
    
    req_file = "data/cleaned/KUCCPS_Requirements_Cleaned.csv"
    cluster_mappings = {}  # programme_name -> cluster
    cluster_requirements = {}  # cluster -> subject_requirements
    
    if not os.path.exists(req_file):
        print("❌ Requirements CSV file not found")
        return {}, {}
    
    try:
        with open(req_file, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            current_cluster = None
            current_subcluster = None
            
            for row_num, row in enumerate(reader):
                # Skip empty rows
                if not any(cell.strip() for cell in row):
                    continue
                
                # Look for cluster numbers (like '1', '2', '3' etc.)
                if row[0] and row[0].strip().isdigit():
                    current_cluster = row[0].strip()
                    current_subcluster = row[1].strip() if len(row) > 1 and row[1] else None
                    print(f"📋 Found Cluster {current_cluster} - {current_subcluster}")
                
                # Look for subject requirements (rows with ENG/, MAT/, BIO/, etc.)
                elif current_cluster and any(any(keyword in cell for keyword in ['ENG/', 'MAT ', 'BIO(', 'CHE(', 'PHY(', 'GEO(', 'HIS(']) for cell in row if cell):
                    subjects = [cell.strip() for cell in row if cell.strip()]
                    if subjects and current_cluster not in cluster_requirements:
                        cluster_requirements[current_cluster] = subjects
                        print(f"   📚 Subject Requirements: {subjects}")
                
                # Look for programme names (rows that contain actual programme names)
                elif any(any(word in cell.upper() for word in ['BACHELOR', 'DEGREE', 'LAW', 'MEDICINE', 'ENGINEERING', 'SCIENCE', 'ARTS', 'COMMERCE']) for cell in row if cell):
                    programme_cells = [cell.strip() for cell in row if cell.strip() and any(word in cell.upper() for word in ['BACHELOR', 'DEGREE'])]
                    
                    for cell in programme_cells:
                        # This is likely a programme name mapped to the current cluster
                        if current_cluster:
                            cluster_mappings[cell.upper()] = current_cluster
                            print(f"   🎯 Programme: '{cell}' → Cluster {current_cluster}")
            
            print(f"\n📊 EXTRACTION RESULTS:")
            print(f"   Found {len(cluster_mappings)} programme-to-cluster mappings")
            print(f"   Found {len(cluster_requirements)} clusters with subject requirements")
            
            return cluster_mappings, cluster_requirements
            
    except Exception as e:
        print(f"❌ Error extracting cluster mappings: {e}")
        return {}, {}

# Extract the actual mappings
ACTUAL_CLUSTER_MAPPINGS, ACTUAL_CLUSTER_REQUIREMENTS = extract_actual_cluster_mappings()

def get_programme_cluster(programme_name):
    """
    Use ACTUAL cluster mapping from your KUCCPS document
    """
    programme_name_upper = programme_name.upper()
    
    # Try exact match first
    if programme_name_upper in ACTUAL_CLUSTER_MAPPINGS:
        cluster = ACTUAL_CLUSTER_MAPPINGS[programme_name_upper]
        return cluster
    
    # Try partial match (in case of small differences)
    for mapped_name, cluster in ACTUAL_CLUSTER_MAPPINGS.items():
        if programme_name_upper in mapped_name or mapped_name in programme_name_upper:
            return cluster
    
    # If no match found, use safe default (don't filter)
    return None

def parse_kuccps_requirements(requirements_text):
    """
    Parse KUCCPS subject requirements like 'BIO(231):C+ CHE(233):C+ MAT A(121):C+'
    """
    requirements = []
    
    # Common KUCCPS subject codes mapping
    subject_map = {
        'MAT A(121)': 'Mathematics', 'MAT B(122)': 'Mathematics',
        'ENG(101)': 'English', 'KIS(102)': 'Kiswahili',
        'BIO(231)': 'Biology', 'CHE(233)': 'Chemistry', 'PHY(232)': 'Physics',
        'GEO(312)': 'Geography', 'HIS(311)': 'History',
        'CRE(313)': 'Christian Religious Education', 'IRE(314)': 'Islamic Religious Education',
        'AGR(443)': 'Agriculture', 'BUS(445)': 'Business Studies'
    }
    
    # Split requirements by spaces and look for pattern: SUBJECT(CODE):GRADE
    for req in requirements_text:
        if ':' in req:
            parts = req.split(':')
            if len(parts) == 2:
                subject_code = parts[0].strip()
                required_grade = parts[1].strip()
                
                # Map subject code to subject name
                subject_name = subject_map.get(subject_code, subject_code)
                requirements.append((subject_name, required_grade))
    
    return requirements

def check_subject_requirements(programme_data, user_grades):
    """
    Use ACTUAL subject requirements from your KUCCPS document
    """
    programme_name = programme_data['programme_name']
    cluster = get_programme_cluster(programme_name)
    
    # If no cluster mapping found, be safe and don't filter
    if not cluster or cluster not in ACTUAL_CLUSTER_REQUIREMENTS:
        return True
    
    requirements_text = ACTUAL_CLUSTER_REQUIREMENTS[cluster]
    requirements = parse_kuccps_requirements(requirements_text)
    
    # If we couldn't parse requirements, be safe
    if not requirements:
        return True
    
    # Grade values for comparison
    grade_values = {
        'A': 12, 'A-': 11, 'B+': 10, 'B': 9, 'B-': 8,
        'C+': 7, 'C': 6, 'C-': 5, 'D+': 4, 'D': 3, 'D-': 2, 'E': 1
    }
    
    # Check each requirement
    for subject, required_grade in requirements:
        user_grade = user_grades.get(subject)
        
        # If user doesn't have this subject at all, they don't qualify
        if not user_grade:
            print(f"❌ {programme_name}: Missing required subject - {subject}")
            return False
        
        # Check if user's grade meets the requirement
        user_value = grade_values.get(user_grade, 0)
        required_value = grade_values.get(required_grade, 0)
        
        if user_value < required_value:
            print(f"❌ {programme_name}: {subject} grade too low - User: {user_grade}, Required: {required_grade}")
            return False
    
    print(f"✅ {programme_name}: Meets all subject requirements")
    return True

@api_view(['POST'])
def check_eligibility(request):
    try:
        data = request.data

        user_cluster_points = float(data.get('cluster_points', 0))
        user_grades = data.get('grades', {})

        eligible_programmes = []

        for programme in ALL_PROGRAMMES:
            if user_cluster_points >= programme['cluster_points']:
                eligible_programmes.append({
                    'programme_code': programme['programme_code'],
                    'programme_name': programme['programme_name'],
                    'university': programme['university'],
                    'cluster_points': programme['cluster_points'],
                    'required_cluster': programme['cluster_points'],
                })

        return Response({
            "message": "Success",
            "eligible_programmes": eligible_programmes,
            "total_found": len(eligible_programmes)
        })

    except Exception as e:
        return Response({
            "error": str(e),
            "eligible_programmes": [],
            "total_found": 0
        }, status=500)
@api_view(['POST'])
def download_courses_pdf(request):
    try:
        data = request.data
        eligible_programmes = data.get('eligible_programmes', [])
        user_cluster_points = data.get('cluster_points', 0)
        
        print(f"📊 PDF Generation: Received {len(eligible_programmes)} courses")
        
        if not eligible_programmes:
            return Response({
                "error": "No courses to download",
                "message": "Please find eligible courses first"
            }, status=400)
        
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        
        # Group courses by university
        courses_by_university = {}
        for programme in eligible_programmes:
            university = programme.get('university', 'Unknown University')
            if university not in courses_by_university:
                courses_by_university[university] = []
            courses_by_university[university].append(programme)
        
        # Sort universities alphabetically
        sorted_universities = sorted(courses_by_university.keys())
        
        p.setTitle(f"Eligible Courses - {user_cluster_points} points")
        
        # Title Page
        p.setFont("Helvetica-Bold", 18)
        p.drawString(100, 750, "COURSE PILOT KENYA")
        p.setFont("Helvetica-Bold", 16)
        p.drawString(100, 720, "Eligible Courses Report")
        
        p.setFont("Helvetica", 12)
        p.drawString(100, 680, f"Student Cluster Points: {user_cluster_points}")
        p.drawString(100, 660, f"Total Eligible Courses: {len(eligible_programmes)}")
        p.drawString(100, 640, f"Total Universities: {len(sorted_universities)}")
        p.drawString(100, 620, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        # University summary
        p.setFont("Helvetica-Bold", 12)
        p.drawString(100, 580, "Universities with Eligible Courses:")
        p.setFont("Helvetica", 10)
        
        y_position = 560
        for i, university in enumerate(sorted_universities):
            course_count = len(courses_by_university[university])
            p.drawString(120, y_position, f"• {university}: {course_count} courses")
            y_position -= 15
            
            if y_position < 100 and i < len(sorted_universities) - 1:
                p.showPage()
                p.setFont("Helvetica-Bold", 12)
                p.drawString(100, 750, "Universities (continued):")
                p.setFont("Helvetica", 10)
                y_position = 730
        
        p.setFont("Helvetica-Oblique", 8)
        p.drawString(100, 50, "Complete course list follows on next pages")
        p.drawString(100, 35, "CoursePilot Kenya - Making Education Accessible")
        
        # Detailed courses by university
        for university_index, university in enumerate(sorted_universities):
            university_courses = courses_by_university[university]
            
            p.showPage()
            
            # University header
            p.setFont("Helvetica-Bold", 14)
            p.drawString(100, 750, f"University: {university}")
            p.setFont("Helvetica", 10)
            p.drawString(100, 730, f"Number of eligible courses: {len(university_courses)}")
            
            # Course list header
            y_position = 700
            p.setFont("Helvetica-Bold", 10)
            p.drawString(100, y_position, "No.")
            p.drawString(120, y_position, "PROGRAMME NAME")
            p.drawString(400, y_position, "CODE")
            p.drawString(470, y_position, "POINTS")
            
            p.line(100, 695, 550, 695)
            y_position -= 20
            
            # Course list
            p.setFont("Helvetica", 8)
            for i, programme in enumerate(university_courses):
                if y_position < 50:
                    p.showPage()
                    p.setFont("Helvetica-Bold", 10)
                    p.drawString(100, 750, f"University: {university} (continued)")
                    p.setFont("Helvetica-Bold", 10)
                    p.drawString(100, 730, "No.")
                    p.drawString(120, 730, "PROGRAMME NAME")
                    p.drawString(400, 730, "CODE")
                    p.drawString(470, 730, "POINTS")
                    p.line(100, 725, 550, 725)
                    y_position = 710
                    p.setFont("Helvetica", 8)
                
                programme_name = programme.get('programme_name', 'N/A')
                programme_code = programme.get('programme_code', 'N/A')
                points = programme.get('cluster_points', 'N/A')
                
                display_name = programme_name[:55] + "..." if len(programme_name) > 55 else programme_name
                
                p.drawString(100, y_position, f"{i+1}.")
                p.drawString(120, y_position, display_name)
                p.drawString(400, y_position, programme_code)
                p.drawString(470, y_position, str(points))
                
                y_position -= 12
        
        # Final summary page
        p.showPage()
        p.setFont("Helvetica-Bold", 16)
        p.drawString(100, 750, "REPORT SUMMARY")
        p.setFont("Helvetica", 12)
        p.drawString(100, 700, f"Total Universities: {len(sorted_universities)}")
        p.drawString(100, 675, f"Total Eligible Courses: {len(eligible_programmes)}")
        p.drawString(100, 650, f"Your Cluster Points: {user_cluster_points}")
        p.drawString(100, 625, f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        p.setFont("Helvetica-Bold", 12)
        p.drawString(100, 550, "Top Universities by Course Count:")
        p.setFont("Helvetica", 10)
        
        university_counts = [(uni, len(courses_by_university[uni])) for uni in sorted_universities]
        university_counts.sort(key=lambda x: x[1], reverse=True)
        
        y_pos = 520
        for i, (uni, count) in enumerate(university_counts[:10]):
            p.drawString(120, y_pos, f"{i+1}. {uni[:40]}: {count} courses")
            y_pos -= 20
        
        p.setFont("Helvetica-Oblique", 8)
        p.drawString(100, 50, "Important: This is a preliminary report. Always verify with official KUCCPS portal.")
        p.drawString(100, 35, "CoursePilot Kenya - Making Education Accessible")
        
        p.save()
        
        pdf = buffer.getvalue()
        buffer.close()
        
        print(f"✅ PDF Generated: {len(pdf)} bytes, {len(eligible_programmes)} courses")
        
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="all_courses_{user_cluster_points}_points.pdf"'
        response.write(pdf)
        
        return response
        
    except Exception as e:
        print(f"❌ PDF Generation Error: {e}")
        return Response({
            "error": "PDF generation failed",
            "message": str(e)
        }, status=500)

def sync_csv_to_database():
    """
    One-time function to sync CSV data to database
    """
    try:
        from .models import Programme
        
        if not ALL_PROGRAMMES:
            print("❌ Cannot sync to database: No programme data available")
            return
            
        Programme.objects.all().delete()
        print("🧹 Cleared existing database programmes")
        
        programme_count = 0
        for programme_data in ALL_PROGRAMMES:
            programme, created = Programme.objects.get_or_create(
                programme_code=programme_data['programme_code'],
                defaults={
                    'programme_name': programme_data['programme_name'],
                    'university': programme_data['university'],
                    'cluster_points': programme_data['cluster_points']
                }
            )
            if created:
                programme_count += 1
        
        print(f"✅ Added {programme_count} programmes to database")
        print(f"📊 Database now has {Programme.objects.count()} programmes")
        
    except Exception as e:
        print(f"⚠️ Database sync note: {e}")

# Call this function once
if ALL_PROGRAMMES:
    sync_csv_to_database()
else:
    print("❌ Skipping database sync: No programme data available")
def analyze_csv_subject_data():
    """
    Analyze what subject requirement data we actually have in the CSV files
    """
    print("🔍 Analyzing subject data in CSV files...")
    
    # Check main CSV for any subject columns
    main_csv = "data/cleaned/KUCCPS_ClusterPoints_Cleaned.csv"
    if os.path.exists(main_csv):
        try:
            with open(main_csv, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                headers = next(reader)
                print(f"📊 Main CSV columns: {headers}")
                
                # Check if there are subject columns (beyond column 5)
                if len(headers) > 5:
                    print(f"📚 Potential subject columns: {headers[5:]}")
                    
                    # Check first few rows for subject data
                    for i, row in enumerate(reader):
                        if i < 3:  # First 3 data rows
                            if len(row) > 5:
                                print(f"Row {i+1} subject data: {row[5:]}")
                        else:
                            break
                else:
                    print("❌ No extra columns for subject data in main CSV")
        except Exception as e:
            print(f"Error reading main CSV: {e}")
    
    # Check requirements CSV structure
    req_csv = "data/cleaned/KUCCPS_Requirements_Cleaned.csv"
    if os.path.exists(req_csv):
        try:
            with open(req_csv, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                headers = next(reader)
                print(f"📊 Requirements CSV columns: {headers}")
                
                # Look for rows with actual subject requirements
                subject_rows = []
                for i, row in enumerate(reader):
                    if any('ENG' in cell or 'MAT' in cell or 'BIO' in cell or 'CHE' in cell or 'PHY' in cell for cell in row if cell):
                        subject_rows.append((i, [cell for cell in row if cell]))
                    if len(subject_rows) > 5:
                        break
                
                print("📚 Sample subject requirement rows:")
                for row_num, row_data in subject_rows:
                    print(f"  Row {row_num}: {row_data}")
                    
        except Exception as e:
            print(f"Error reading requirements CSV: {e}")

# Call this function
analyze_csv_subject_data()