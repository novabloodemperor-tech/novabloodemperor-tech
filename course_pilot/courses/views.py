from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import HttpResponse
import csv
import os
import io
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter


#############################################
# 1. LOAD PROGRAMMES FROM CSV
#############################################

def load_all_programmes():
    programmes = []

    # All possible locations (local + Render)
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
        print("❌ CSV file not found in any location.")
        return []

    try:
        with open(csv_file, "r", encoding="utf-8") as file:
            reader = csv.reader(file)
            next(reader)  # skip header

            for row in reader:
                if len(row) >= 5:
                    try:
                        programme_code = row[1].strip()
                        university = row[2].strip()
                        programme_name = row[3].strip()

                        cp = row[4].strip()
                        cluster_points = float(cp) if cp and cp != "-" else 0.0

                        programmes.append({
                            "programme_code": programme_code,
                            "programme_name": programme_name,
                            "university": university,
                            "cluster_points": cluster_points
                        })

                    except:
                        continue

        print(f"✅ Loaded {len(programmes)} programmes from CSV")
        return programmes

    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
        return []


# Load CSV at startup
ALL_PROGRAMMES = load_all_programmes()


#############################################
# 2. SIMPLE ELIGIBILITY CHECK (cluster points only)
#############################################

@api_view(['POST'])
def check_eligibility(request):
    try:
        if not ALL_PROGRAMMES:
            return Response({
                "eligible_programmes": [],
                "total_found": 0,
                "message": "Programme data not loaded."
            }, status=500)

        data = request.data
        user_cluster_points = float(data.get("cluster_points", 0))

        eligible = []

        for programme in ALL_PROGRAMMES:
            if user_cluster_points >= programme["cluster_points"]:
                eligible.append({
                    "programme_code": programme["programme_code"],
                    "programme_name": programme["programme_name"],
                    "university": programme["university"],
                    "cluster_points": programme["cluster_points"],
                })

        return Response({
            "message": "Success",
            "eligible_programmes": eligible,
            "total_found": len(eligible)
        })

    except Exception as e:
        return Response({
            "error": str(e),
            "eligible_programmes": [],
            "total_found": 0
        }, status=500)


#############################################
# 3. CHECK DATABASE / HEALTH ENDPOINT
#############################################

@api_view(['GET'])
def check_database(request):
    return Response({
        "total_programmes": len(ALL_PROGRAMMES),
        "message": "Programme data loaded successfully." if ALL_PROGRAMMES else "No programme data found."
    })


#############################################
# 4. PAYMENT ENDPOINT (still works)
#############################################

@api_view(['POST'])
def pay(request):
    phone = request.data.get("phone")
    amount = request.data.get("amount")

    if not phone or not amount:
        return Response({"error": "Phone and amount required"}, status=400)

    return Response({
        "success": True,
        "message": "Payment initiated successfully!",
        "transaction_id": "TEST_12345"
    })


#############################################
# 5. PDF DOWNLOAD ENDPOINT
#############################################

@api_view(['POST'])
def download_courses_pdf(request):
    try:
        data = request.data
        eligible = data.get("eligible_programmes", [])
        user_points = data.get("cluster_points", 0)

        if not eligible:
            return Response({"error": "No courses to download"}, status=400)

        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)

        p.setFont("Helvetica-Bold", 16)
        p.drawString(100, 750, "Eligible Course Report")
        p.setFont("Helvetica", 12)

        p.drawString(100, 720, f"Cluster Points: {user_points}")
        p.drawString(100, 700, f"Total Courses: {len(eligible)}")

        y = 660
        p.setFont("Helvetica", 9)

        for i, course in enumerate(eligible):
            if y < 50:
                p.showPage()
                y = 750

            p.drawString(100, y, f"{i+1}. {course['programme_name']} ({course['programme_code']}) - {course['university']}")
            y -= 15

        p.save()
        pdf = buffer.getvalue()
        buffer.close()

        response = HttpResponse(pdf, content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="eligible_courses.pdf"'

        return response

    except Exception as e:
        return Response({"error": str(e)}, status=500)
