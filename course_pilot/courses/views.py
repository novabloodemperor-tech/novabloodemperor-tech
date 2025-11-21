from rest_framework.decorators import api_view
from rest_framework.response import Response
import csv
import os

# Load all programmes from CSV file
def load_all_programmes():
    programmes = []
    csv_file = "data/cleaned/KUCCPS_ClusterPoints_Cleaned.csv"
    
    if not os.path.exists(csv_file):
        print("CSV file not found:", csv_file)
        return programmes
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header row
            
            for row_num, row in enumerate(reader, start=2):
                if len(row) >= 5 and row[1] and row[3]:  # Check if has programme code and name
                    try:
                        programme_code = row[1].strip()
                        programme_name = row[3].strip()
                        university = row[2].strip()
                        
                        # Convert cluster points to float
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
                        print("Skipping row", row_num, ":", e)
                        continue
        
        print("Loaded", len(programmes), "programmes from CSV")
        return programmes
        
    except Exception as e:
        print("Error reading CSV:", e)
        return programmes

# Load programmes once when the server starts
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
        
        # Create PDF content
        pdf_content = f"""
        COURSE PILOT - ELIGIBLE COURSES REPORT
        ======================================
        
        Student Cluster Points: {user_cluster_points}
        Total Eligible Courses: {len(eligible_programmes)}
        Generated on: Current date
        
        ELIGIBLE COURSES:
        =================
        """
        
        for i, programme in enumerate(eligible_programmes, 1):
            pdf_content += f"""
        {i}. {programme.get('programme_name', 'N/A')}
           University: {programme.get('university', 'N/A')}
           Programme Code: {programme.get('programme_code', 'N/A')}
           Required Points: {programme.get('cluster_points', 'N/A')}
           ---
            """
        
        pdf_content += """
        ======================================
        Note: This is a preliminary report. Always verify with official KUCCPS portal.
        CoursePilot Kenya - Making Education Accessible
        """
        
        return Response({
            "success": True,
            "message": "PDF generated successfully",
            "pdf_content": pdf_content,
            "total_courses": len(eligible_programmes),
            "file_name": f"eligible_courses_{user_cluster_points}_points.pdf",
            "note": "This is a text preview. Full PDF download will be implemented in the next update."
        })
        
    except Exception as e:
        return Response({
            "error": "PDF generation failed",
            "message": str(e)
        }, status=500)