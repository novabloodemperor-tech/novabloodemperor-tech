from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
import io
from datetime import datetime

@api_view(['POST'])
def download_courses_pdf(request):
    try:
        data = request.data
        eligible_programmes = data.get('eligible_programmes', [])
        user_cluster_points = data.get('cluster_points', 0)
        
        if not eligible_programmes:
            return Response({
                "error": "No courses to download",
                "message": "Please find eligible courses first before downloading PDF"
            }, status=400)
        
        # Create a PDF in memory
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        
        # Container for the 'Flowable' objects
        elements = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            alignment=1,
            textColor=colors.HexColor('#2c5aa0')
        )
        
        elements.append(Paragraph("COURSE PILOT KENYA", title_style))
        elements.append(Paragraph("Eligible Courses Report", styles['Heading2']))
        elements.append(Spacer(1, 12))
        
        # Student info
        info_style = ParagraphStyle(
            'InfoStyle',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=6
        )
        
        elements.append(Paragraph(f"<b>Student Cluster Points:</b> {user_cluster_points}", info_style))
        elements.append(Paragraph(f"<b>Total Eligible Courses:</b> {len(eligible_programmes)}", info_style))
        elements.append(Paragraph(f"<b>Generated on:</b> {datetime.now().strftime('%Y-%m-%d %H:%M')}", info_style))
        elements.append(Spacer(1, 20))
        
        # Course table
        if eligible_programmes:
            # Table data
            table_data = [['No.', 'Programme Name', 'University', 'Req. Points']]
            
            for i, programme in enumerate(eligible_programmes[:50], 1):
                table_data.append([
                    str(i),
                    programme.get('programme_name', 'N/A')[:40],
                    programme.get('university', 'N/A')[:30],
                    str(programme.get('cluster_points', 'N/A'))
                ])
            
            # Create table
            table = Table(table_data, colWidths=[0.5*inch, 3*inch, 2*inch, 1*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5aa0')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(table)
            
            if len(eligible_programmes) > 50:
                elements.append(Spacer(1, 12))
                elements.append(Paragraph(f"<i>Showing first 50 of {len(eligible_programmes)} courses. Visit CoursePilot for complete list.</i>", styles['Italic']))
        
        elements.append(Spacer(1, 20))
        
        # Footer note
        note_style = ParagraphStyle(
            'NoteStyle',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.gray,
            alignment=1
        )
        
        elements.append(Paragraph("Note: This is a preliminary report. Always verify with official KUCCPS portal.", note_style))
        elements.append(Paragraph("CoursePilot Kenya - Making Education Accessible", note_style))
        
        # Build PDF
        doc.build(elements)
        
        # Get PDF value from buffer
        pdf = buffer.getvalue()
        buffer.close()
        
        # Create HTTP response with PDF - Use Django HttpResponse, not DRF Response
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="eligible_courses_{user_cluster_points}_points.pdf"'
        response.write(pdf)
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
    
    # Try different possible file paths
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
        print("CSV file not found in any location")
        # Return some test data so the API works
        return [
            {"programme_code": "TEST001", "programme_name": "Computer Science", "university": "University of Nairobi", "cluster_points": 25.0},
            {"programme_code": "TEST002", "programme_name": "Business Administration", "university": "Kenyatta University", "cluster_points": 22.0},
            {"programme_code": "TEST003", "programme_name": "Education Arts", "university": "Moi University", "cluster_points": 18.0}
        ]
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header row
            
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
                        continue
        
        print("Loaded", len(programmes), "programmes from CSV")
        return programmes
        
    except Exception as e:
        print("Error reading CSV:", e)
        # Return test data if CSV fails
        return [
            {"programme_code": "TEST001", "programme_name": "Computer Science", "university": "University of Nairobi", "cluster_points": 25.0},
            {"programme_code": "TEST002", "programme_name": "Business Administration", "university": "Kenyatta University", "cluster_points": 22.0},
            {"programme_code": "TEST003", "programme_name": "Education Arts", "university": "Moi University", "cluster_points": 18.0}
        ]

# Load programmes
ALL_PROGRAMMES = load_all_programmes()

@api_view(['POST'])
def check_eligibility(request):
    try:
        data = request.data
        user_cluster_points = float(data.get('cluster_points', 0))
        
        print("Checking eligibility with", len(ALL_PROGRAMMES), "programmes")
        print("User cluster points:", user_cluster_points)
        
        # Filter programmes by cluster points
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
        
        print("Found", len(eligible_programmes), "eligible programmes")
        
        return Response({
            'eligible_programmes': eligible_programmes,
            'total_found': len(eligible_programmes),
            'database_total': len(ALL_PROGRAMMES),
            'message': 'Found ' + str(len(eligible_programmes)) + ' courses matching your ' + str(user_cluster_points) + ' cluster points'
        })
        
    except Exception as e:
        print("Error in eligibility check:", e)
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
                "message": "Please find eligible courses first before downloading PDF"
            }, status=400)
        
        # Create a PDF using canvas (simpler approach)
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer)
        
        # Set up the PDF
        p.setTitle(f"Eligible Courses - {user_cluster_points} points")
        
        # Title
        p.setFont("Helvetica-Bold", 16)
        p.drawString(100, 750, "COURSE PILOT KENYA")
        p.setFont("Helvetica-Bold", 14)
        p.drawString(100, 730, "Eligible Courses Report")
        
        # Student info
        p.setFont("Helvetica", 10)
        p.drawString(100, 700, f"Student Cluster Points: {user_cluster_points}")
        p.drawString(100, 685, f"Total Eligible Courses: {len(eligible_programmes)}")
        p.drawString(100, 670, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        # Courses list
        y_position = 640
        p.setFont("Helvetica-Bold", 10)
        p.drawString(100, y_position, "ELIGIBLE COURSES:")
        y_position -= 20
        
        p.setFont("Helvetica", 8)
        for i, programme in enumerate(eligible_programmes[:30], 1):  # Limit to 30 courses
            if y_position < 50:  # Start new page if needed
                p.showPage()
                p.setFont("Helvetica", 8)
                y_position = 750
            
            programme_name = programme.get('programme_name', 'N/A')[:50]
            university = programme.get('university', 'N/A')[:40]
            points = programme.get('cluster_points', 'N/A')
            
            p.drawString(120, y_position, f"{i}. {programme_name}")
            p.drawString(140, y_position - 12, f"   University: {university}")
            p.drawString(140, y_position - 24, f"   Required Points: {points}")
            
            y_position -= 40
        
        # Footer
        p.setFont("Helvetica-Oblique", 8)
        p.drawString(100, 30, "Note: This is a preliminary report. Always verify with official KUCCPS portal.")
        p.drawString(100, 15, "CoursePilot Kenya - Making Education Accessible")
        
        # Finalize PDF
        p.showPage()
        p.save()
        
        # Get PDF value
        pdf = buffer.getvalue()
        buffer.close()
        
        # Create response
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="courses_{user_cluster_points}.pdf"'
        response.write(pdf)
        
        return response
        
    except Exception as e:
        return Response({
            "error": "PDF generation failed",
            "message": str(e)
        }, status=500)
        return response
        
    except Exception as e:
        return Response({
            "error": "PDF generation failed",
            "message": str(e)
        }, status=500)