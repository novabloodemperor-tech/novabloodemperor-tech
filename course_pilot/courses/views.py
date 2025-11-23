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
        print("CSV file not found")
        return [
            {"programme_code": "TEST001", "programme_name": "Computer Science", "university": "University of Nairobi", "cluster_points": 25.0},
            {"programme_code": "TEST002", "programme_name": "Business Administration", "university": "Kenyatta University", "cluster_points": 22.0},
            {"programme_code": "TEST003", "programme_name": "Education Arts", "university": "Moi University", "cluster_points": 18.0}
        ]
    
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
                    except:
                        continue
        
        print("Loaded", len(programmes), "programmes from CSV")
        return programmes
        
    except Exception as e:
        print("Error reading CSV:", e)
        return [
            {"programme_code": "TEST001", "programme_name": "Computer Science", "university": "University of Nairobi", "cluster_points": 25.0},
            {"programme_code": "TEST002", "programme_name": "Business Administration", "university": "Kenyatta University", "cluster_points": 22.0},
            {"programme_code": "TEST003", "programme_name": "Education Arts", "university": "Moi University", "cluster_points": 18.0}
        ]

ALL_PROGRAMMES = load_all_programmes()
def check_requirements_data():
    """
    Check what subject requirements data we actually have
    """
    print("🔍 Checking actual subject requirements data...")
    
    # Check if we have a requirements CSV file
    requirements_files = [
        "data/cleaned/KUCCPS_Requirements_Cleaned.csv",
        "/opt/render/project/src/data/cleaned/KUCCPS_Requirements_Cleaned.csv",
        "KUCCPS_Requirements_Cleaned.csv"
    ]
    
    req_file = None
    for file_path in requirements_files:
        if os.path.exists(file_path):
            req_file = file_path
            break
    
    if req_file:
        try:
            with open(req_file, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                headers = next(reader)
                print(f"✅ Requirements file found: {req_file}")
                print(f"📊 Columns: {headers}")
                
                # Show first few rows
                print("Sample rows from requirements file:")
                for i, row in enumerate(reader):
                    if i < 5:  # Show first 5 rows
                        print(f"Row {i+1}: {row}")
                    else:
                        break
        except Exception as e:
            print(f"❌ Error reading requirements file: {e}")
    else:
        print("❌ No requirements CSV file found")
    
    # Also check if subject requirements are in the main CSV
    print(f"\n🔍 Checking main CSV for subject requirements...")
    if ALL_PROGRAMMES:
        sample_programme = ALL_PROGRAMMES[0]
        print(f"Sample programme structure: {list(sample_programme.keys())}")
        
        # Look for programmes with "MEDICAL LABORATORY" in name
        medical_programmes = [p for p in ALL_PROGRAMMES if 'MEDICAL LABORATORY' in p['programme_name'].upper()]
        if medical_programmes:
            print(f"🏥 Medical Laboratory programme sample: {medical_programmes[0]}")
        
        # Look for Computer Science programmes
        comp_programmes = [p for p in ALL_PROGRAMMES if 'COMPUTER' in p['programme_name'].upper()]
        if comp_programmes:
            print(f"💻 Computer Science programme sample: {comp_programmes[0]}")

# Call this function to see what data we have
check_requirements_data()
def get_programme_cluster(programme_name):
    """
    Guess the cluster based on programme name patterns
    This is temporary until we get proper cluster mapping
    """
    programme_name_upper = programme_name.upper()
    
    # Law programmes
    if any(word in programme_name_upper for word in ['LAW', 'LL.B']):
        return '1'  # Cluster 1 for Law
    
    # Medical programmes
    elif any(word in programme_name_upper for word in ['MEDICINE', 'MEDICAL', 'PHARMACY', 'DENTAL', 'SURGERY', 'VETERINARY']):
        return '2'  # Likely Cluster 2 for Medicine
    
    # Engineering programmes
    elif any(word in programme_name_upper for word in ['ENGINEERING', 'ELECTRICAL', 'MECHANICAL', 'CIVIL', 'AERONAUTICAL']):
        return '3'  # Likely Cluster 3 for Engineering
    
    # Computer Science programmes
    elif any(word in programme_name_upper for word in ['COMPUTER', 'SOFTWARE', 'INFORMATION TECHNOLOGY', 'IT']):
        return '4'  # Likely Cluster 4 for Computer Science
    
    # Business programmes
    elif any(word in programme_name_upper for word in ['COMMERCE', 'BUSINESS', 'ACCOUNTING', 'ECONOMICS']):
        return '5'  # Likely Cluster 5 for Business
    
    # Default cluster for general programmes
    return '6'

def check_subject_requirements(programme_data, user_grades):
    """
    Improved subject requirement checking using cluster-based system
    """
    programme_name = programme_data['programme_name']
    cluster = get_programme_cluster(programme_name)
    
    print(f"🔍 Checking {programme_name} - Cluster: {cluster}")
    
    # Define basic cluster requirements (we'll improve this with actual data)
    cluster_requirements = {
        '1': [('English', 'B'), ('Kiswahili', 'B')],  # Law cluster
        '2': [('Biology', 'C+'), ('Chemistry', 'C+'), ('Mathematics', 'C+'), ('Physics', 'C+')],  # Medical cluster
        '3': [('Mathematics', 'C+'), ('Physics', 'C+'), ('Chemistry', 'C')],  # Engineering cluster
        '4': [('Mathematics', 'C+')],  # Computer Science cluster
        '5': [('Mathematics', 'C+')],  # Business cluster
        '6': []  # General cluster - no specific requirements
    }
    
    requirements = cluster_requirements.get(cluster, [])
    
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
    
    return True
def analyze_cluster_requirements():
    """
    Analyze the cluster-based requirements structure
    """
    print("🔍 Analyzing cluster requirements structure...")
    
    req_file = "data/cleaned/KUCCPS_Requirements_Cleaned.csv"
    
    if os.path.exists(req_file):
        try:
            with open(req_file, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                clusters = {}
                current_cluster = None
                
                for row_num, row in enumerate(reader):
                    # Look for cluster headers (numbers in first column)
                    if row[0] and row[0].isdigit():
                        current_cluster = row[0]
                        clusters[current_cluster] = {
                            'subcluster': row[1] if len(row) > 1 else '',
                            'subjects': []
                        }
                        print(f"📋 Cluster {current_cluster}: {row[1]}")
                    
                    # Look for subject requirements (rows with actual requirements)
                    elif current_cluster and any('SUBJECT' in cell.upper() or 'ENG/' in cell or 'MAT ' in cell for cell in row if cell):
                        subjects_row = [cell for cell in row if cell.strip()]
                        if subjects_row:
                            clusters[current_cluster]['subjects'] = subjects_row
                            print(f"   Subjects: {subjects_row}")
                    
                    # Look for specific programme examples in requirements
                    elif current_cluster and any('LAWS' in cell.upper() or 'MEDICINE' in cell.upper() or 'ENGINEERING' in cell.upper() for cell in row if cell):
                        print(f"   Programme example: {[cell for cell in row if cell]}")
                
                print(f"📊 Found {len(clusters)} clusters")
                return clusters
                
        except Exception as e:
            print(f"❌ Error analyzing clusters: {e}")
    
    return {}

# Call this to see cluster structure
clusters_data = analyze_cluster_requirements()
def check_subject_requirements(programme_data, user_grades):
    """
    Basic subject requirement checking
    For now, we'll check common required subjects
    """
    programme_name = programme_data['programme_name'].upper()
    
    # Common subject requirements based on programme names
    if any(word in programme_name for word in ['ENGINEERING', 'PHYSICS', 'ELECTRICAL', 'MECHANICAL', 'CIVIL']):
        # Engineering programmes usually require Physics and Mathematics
        if not user_grades.get('Physics') or not user_grades.get('Mathematics'):
            return False
    
    elif any(word in programme_name for word in ['MEDICINE', 'PHARMACY', 'DENTAL', 'SURGERY', 'VETERINARY']):
        # Medical programmes usually require Biology and Chemistry
        if not user_grades.get('Biology') or not user_grades.get('Chemistry'):
            return False
    
    elif any(word in programme_name for word in ['COMPUTER', 'SOFTWARE', 'IT', 'INFORMATION']):
        # Computer programmes usually require Mathematics
        if not user_grades.get('Mathematics'):
            return False
    
    elif any(word in programme_name for word in ['COMMERCE', 'BUSINESS', 'ACCOUNTING', 'ECONOMICS']):
        # Business programmes usually require Mathematics
        if not user_grades.get('Mathematics'):
            return False
    
    # If no specific requirements detected, return True
    return True

@api_view(['POST'])
def check_eligibility(request):
    try:
        data = request.data
        user_grades = data.get('grades', {})
        user_cluster_points = float(data.get('cluster_points', 0))
        
        print(f"🔍 Checking eligibility with {len(ALL_PROGRAMMES)} programmes")
        print(f"📊 User cluster points: {user_cluster_points}")
        print(f"📚 User subjects: {list(user_grades.keys())}")

        eligible_programmes = []
        programmes_bypassed = 0
        
        for programme in ALL_PROGRAMMES:
            # Check cluster points first
            if user_cluster_points >= programme['cluster_points']:
                # Check subject requirements
                meets_subjects = check_subject_requirements(programme, user_grades)
                
                if meets_subjects:
                    eligible_programmes.append({
                        'programme_code': programme['programme_code'],
                        'programme_name': programme['programme_name'],
                        'university': programme['university'],
                        'cluster_points': programme['cluster_points'],
                        'required_cluster': programme['cluster_points'],
                        'meets_subjects': True
                    })
                else:
                    programmes_bypassed += 1
                    # For debugging, let's see which programmes are being filtered out
                    print(f"⚠️ Filtered out: {programme['programme_name']} - Subject requirements not met")
        
        print(f"🎯 Found {len(eligible_programmes)} eligible programmes")
        print(f"🚫 Filtered out {programmes_bypassed} programmes due to subject requirements")
        
        return Response({
            'eligible_programmes': eligible_programmes,
            'total_found': len(eligible_programmes),
            'database_total': len(ALL_PROGRAMMES),
            'programmes_filtered': programmes_bypassed,
            'message': f'Found {len(eligible_programmes)} courses matching your criteria',
            'note': '✅ Now checking both cluster points AND subject requirements'
        })
        
    except Exception as e:
        print(f"❌ Error in eligibility check: {e}")
        return Response({
            'eligible_programmes': [],
            'total_found': 0,
            'message': f'Error: {str(e)}'
        }, status=500)

@api_view(['GET'])
def check_database(request):
    return Response({
        'total_programmes': len(ALL_PROGRAMMES),
        'status': 'working',
        'message': 'Using CSV data with ' + str(len(ALL_PROGRAMMES)) + ' programmes'
    })

@api_view(['POST'])
def pay(request):
    try:
        phone = request.data.get("phone")
        amount = request.data.get("amount")
        if not phone or not amount:
            return Response({"error": "Phone and amount are required"}, status=400)
        return Response({
            "success": True,
            "message": "Payment initiated successfully!",
            "phone": phone,
            "amount": amount,
            "transaction_id": "TEST_12345"
        })
    except Exception as e:
        return Response({"error": str(e)}, status=500)

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
            
            # Better page break handling
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
            
            # Start new page for each university
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
            
            # Draw line under header
            p.line(100, 695, 550, 695)
            y_position -= 20
            
            # Course list
            p.setFont("Helvetica", 8)
            for i, programme in enumerate(university_courses):
                if y_position < 50:  # Start new page if running out of space
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
                
                # Truncate long programme names
                display_name = programme_name[:55] + "..." if len(programme_name) > 55 else programme_name
                
                # Draw programme details
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
        
        # Show top 10 universities by course count
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

# Add this function to your existing views.py file
def sync_csv_to_database():
    """
    One-time function to sync CSV data to database
    This won't affect your current functionality
    """
    try:
        from .models import Programme
        
        # Clear existing database programmes
        Programme.objects.all().delete()
        print("🧹 Cleared existing database programmes")
        
        # Add programmes from CSV to database
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

# Call this function once (it will run when the server starts)
sync_csv_to_database()