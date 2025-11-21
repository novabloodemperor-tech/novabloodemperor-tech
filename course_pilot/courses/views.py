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
        
        return response
        
    except Exception as e:
        return Response({
            "error": "PDF generation failed",
            "message": str(e)
        }, status=500)