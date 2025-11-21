from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import HttpResponse
import csv
import os
import io
from datetime import datetime
from reportlab.pdfgen import canvas

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

@api_view(['POST'])
def check_eligibility(request):
    try:
        data = request.data
        user_cluster_points = float(data.get('cluster_points', 0))
        
        eligible_programmes = []
        for programme in ALL_PROGRAMMES:
            if user_cluster_points >= programme['cluster_points']:
                eligible_programmes.append({
                    'programme_code': programme['programme_code'],
                    'programme_name': programme['programme_name'],
                    'university': programme['university'],
                    'cluster_points': programme['cluster_points'],
                    'required_cluster': programme['cluster_points']
                })
        
        return Response({
            'eligible_programmes': eligible_programmes,
            'total_found': len(eligible_programmes),
            'database_total': len(ALL_PROGRAMMES),
            'message': 'Found ' + str(len(eligible_programmes)) + ' courses'
        })
        
    except Exception as e:
        return Response({
            'eligible_programmes': [],
            'total_found': 0,
            'message': 'Error: ' + str(e)
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
        
        # Add a summary table
        p.setFont("Helvetica-Bold", 12)
        p.drawString(100, 580, "Summary by University:")
        p.setFont("Helvetica", 10)
        
        y_position = 560
        for i, university in enumerate(sorted_universities[:15]):  # Show first 15 on title page
            course_count = len(courses_by_university[university])
            p.drawString(120, y_position, f"• {university[:50]}: {course_count} courses")
            y_position -= 15
            if y_position < 100 and i < len(sorted_universities) - 1:
                p.drawString(120, y_position, f"... and {len(sorted_universities) - 15} more universities")
                break
        
        p.setFont("Helvetica-Oblique", 8)
        p.drawString(100, 50, "Note: Complete course list follows on next pages")
        p.drawString(100, 35, "CoursePilot Kenya - Making Education Accessible")
        
        # Start new page for detailed courses
        p.showPage()
        
        # Detailed courses by university
        for university_index, university in enumerate(sorted_universities):
            university_courses = courses_by_university[university]
            
            # Start new page for each university if needed
            if university_index > 0:
                p.showPage()
            
            # University header
            p.setFont("Helvetica-Bold", 14)
            p.drawString(100, 750, f"University: {university}")
            p.setFont("Helvetica", 10)
            p.drawString(100, 730, f"Number of eligible courses: {len(university_courses)}")
            
            # Course list
            y_position = 700
            p.setFont("Helvetica-Bold", 10)
            p.drawString(100, y_position, "PROGRAMME NAME")
            p.drawString(350, y_position, "CODE")
            p.drawString(420, y_position, "POINTS")
            y_position -= 20
            
            p.setFont("Helvetica", 8)
            for i, programme in enumerate(university_courses):
                if y_position < 50:  # Start new page if running out of space
                    p.showPage()
                    p.setFont("Helvetica-Bold", 10)
                    p.drawString(100, 750, f"University: {university} (continued)")
                    p.setFont("Helvetica-Bold", 10)
                    p.drawString(100, 730, "PROGRAMME NAME")
                    p.drawString(350, 730, "CODE")
                    p.drawString(420, 730, "POINTS")
                    y_position = 710
                    p.setFont("Helvetica", 8)
                
                programme_name = programme.get('programme_name', 'N/A')[:60]
                programme_code = programme.get('programme_code', 'N/A')[:15]
                points = programme.get('cluster_points', 'N/A')
                
                # Draw programme details
                p.drawString(100, y_position, f"{i+1}. {programme_name}")
                p.drawString(350, y_position, programme_code)
                p.drawString(420, y_position, str(points))
                
                y_position -= 12
                
                # Add small gap every 10 courses for readability
                if (i + 1) % 10 == 0:
                    y_position -= 5
        
        # Final page with footer
        p.showPage()
        p.setFont("Helvetica-Bold", 12)
        p.drawString(100, 750, "REPORT SUMMARY")
        p.setFont("Helvetica", 10)
        p.drawString(100, 720, f"Total Universities: {len(sorted_universities)}")
        p.drawString(100, 700, f"Total Eligible Courses: {len(eligible_programmes)}")
        p.drawString(100, 680, f"Your Cluster Points: {user_cluster_points}")
        p.drawString(100, 660, f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        p.setFont("Helvetica-Oblique", 8)
        p.drawString(100, 50, "Important: This is a preliminary report. Always verify with official KUCCPS portal.")
        p.drawString(100, 35, "CoursePilot Kenya - Making Education Accessible")
        p.drawString(100, 20, "Contact: support@coursepilot.co.ke")
        
        p.showPage()
        p.save()
        
        pdf = buffer.getvalue()
        buffer.close()
        
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="all_courses_{user_cluster_points}_points.pdf"'
        response.write(pdf)
        
        return response
        
    except Exception as e:
        return Response({
            "error": "PDF generation failed",
            "message": str(e)
        }, status=500)