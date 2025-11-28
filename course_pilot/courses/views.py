from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import HttpResponse
import csv
import os
import io
import re
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

# ------------------------
# CONFIG / GRADE SCALE
# ------------------------
GRADE_ORDER = ["A", "A-", "B+", "B", "B-", "C+", "C", "C-", "D+", "D", "D-", "E"]
GRADE_VALUE = {g: i for i, g in enumerate(reversed(GRADE_ORDER), start=1)}  # higher = better

# Map common frontend subject names -> canonical CSV code prefixes
NAME_TO_CODE = {
    "mathematics": ["MAT"],  # MAT A / MAT B -> MAT
    "math": ["MAT"],
    "maths": ["MAT"],
    "english": ["ENG"],
    "kiswahili": ["KIS"],
    "kis": ["KIS"],
    "biology": ["BIO"],
    "chemistry": ["CHE"],
    "physics": ["PHY"],
    "geography": ["GEO"],
    "history": ["HIS", "HAG"],
    "cre": ["CRE"],
    "religious education": ["CRE", "IRE"],
    "ire": ["IRE"],
    "agriculture": ["AGR"],
    "business studies": ["BST", "BUS"],
    "business": ["BST", "BUS"],
    "computer studies": ["CMP", "CS"],
    "computer science": ["CS", "CMP"],
    "general science": ["GSC"],
    "music": ["MUC", "MUS"],
    "french": ["FRE"],
    "german": ["GER"],
    "arabic": ["ARB"],
    "home science": ["HSC"],
}

# Normalize CSV aliases to canonical codes
ALIAS_TO_CODE = {
    "HAG": "HIS",
    "HIS": "HIS",
    "GSC": "GSC",
    "CMP": "CS",
    "CS": "CS",
    "BST": "BST",
    "BUS": "BST",
    "ENG": "ENG",
    "MAT": "MAT",
    "BIO": "BIO",
    "CHE": "CHE",
    "PHY": "PHY",
    "GEO": "GEO",
    "CRE": "CRE",
    "IRE": "IRE",
    "AGR": "AGR",
}

# Regex to extract prefix: e.g. "MAT A(121)" -> "MAT"
CODE_PREFIX_RE = re.compile(r'\b([A-Z]{2,4})\b')

# ------------------------
# CSV LOADER
# ------------------------
def load_all_programmes():
    programmes = []
    possible_paths = [
        "data/cleaned/KUCCPS_ClusterPoints_Cleaned.csv",
        "/opt/render/project/src/data/cleaned/KUCCPS_ClusterPoints_Cleaned.csv",
        "KUCCPS_ClusterPoints_Cleaned.csv"
    ]

    csv_file = None
    for p in possible_paths:
        if os.path.exists(p):
            csv_file = p
            break

    if not csv_file:
        print("❌ CSV file not found in any known location.")
        return []

    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader, None)  # skip header
            for row in reader:
                if len(row) < 6:
                    continue
                try:
                    programme_code = row[1].strip()
                    university = row[2].strip()
                    programme_name = row[3].strip()

                    # ------------------------------------------
                    # ✔️ EXACT UPDATED CLUSTER BLOCK (your version)
                    # ------------------------------------------
                    cp2024_raw = row[4].strip() if len(row) > 4 else ""
                    cp2023_raw = row[5].strip() if len(row) > 5 else ""

                    def parse_cp(value):
                        try:
                            if value not in ("", "-", "NA", "N/A", None):
                                return float(value.replace(",", "."))
                        except:
                            pass
                        return None

                    cp2024 = parse_cp(cp2024_raw)
                    cp2023 = parse_cp(cp2023_raw)

                    if cp2024 is not None:
                        cluster_points = cp2024
                    elif cp2023 is not None:
                        cluster_points = cp2023
                    else:
                        cluster_points = 0.0
                    # ------------------------------------------

                    # SUBJECT REQUIREMENTS (columns 6..9)
                    subj_reqs = []
                    for idx in range(6, 10):
                        if idx < len(row):
                            cell = row[idx]
                            if cell and cell.strip() and cell.strip() not in ("-", "NA", "N/A"):
                                subj_reqs.append(cell.strip())

                    programmes.append({
                        "programme_code": programme_code,
                        "programme_name": programme_name,
                        "university": university,
                        "cluster_points": cluster_points,
                        "requirements": subj_reqs
                    })

                except Exception:
                    # removed "Skipping row due to parse error"
                    continue

        print(f"✅ Loaded {len(programmes)} programmes from CSV: {csv_file}")
        return programmes

    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
        return []

ALL_PROGRAMMES = load_all_programmes()

# ------------------------
# HELPERS
# ------------------------
def normalize_subject_name(name: str):
    if not name:
        return None
    return name.strip().lower()

def student_grades_to_code_map(student_grades: dict):
    code_grade = {}
    for name, grade in (student_grades or {}).items():
        if not name or not grade:
            continue
        key = normalize_subject_name(name)
        codes = NAME_TO_CODE.get(key)

        if not codes:
            heuristic = re.sub(r'[^A-Za-z]', '', key)[:3].upper()
            codes = [heuristic]

        for code in codes:
            canon = ALIAS_TO_CODE.get(code, code)
            code_grade[canon] = grade.strip().upper()

    return code_grade

def extract_codes_from_requirement_token(token: str):
    if not token:
        return []
    token = token.replace("/", "/").replace(" / ", "/")
    parts = [p.strip() for p in re.split(r'[\/;|]', token) if p.strip()]
    codes = []
    for p in parts:
        m = CODE_PREFIX_RE.search(p.upper())
        if m:
            code = m.group(1)
            code = ALIAS_TO_CODE.get(code, code)
            codes.append(code)
    return codes

def parse_requirement_cell(cell_text: str):
    if not cell_text or not str(cell_text).strip():
        return []
    text = str(cell_text).strip()
    try:
        if ":" in text:
            left, right = text.rsplit(":", 1)
            required_grade = right.strip().upper()
            codes = extract_codes_from_requirement_token(left)
            if codes:
                return [(codes, required_grade)]
            return []
        else:
            parts = text.split()
            possible_grade = parts[-1].strip().upper()
            if possible_grade in GRADE_VALUE:
                left = " ".join(parts[:-1])
                codes = extract_codes_from_requirement_token(left)
                return [(codes, possible_grade)] if codes else []
            return []
    except:
        return []

def meets_group_requirement(codes: list, required_grade: str, student_code_grade_map: dict):
    if not codes:
        return True
    required_value = GRADE_VALUE.get(required_grade, 0)
    for code in codes:
        stud_grade = student_code_grade_map.get(code)
        if not stud_grade:
            for alias, canon in ALIAS_TO_CODE.items():
                if canon == code and alias in student_code_grade_map:
                    stud_grade = student_code_grade_map[alias]
                    break
        if stud_grade:
            stud_val = GRADE_VALUE.get(stud_grade.upper(), 0)
            if stud_val >= required_value:
                return True
    return False

# ------------------------
# MAIN ELIGIBILITY ENDPOINT
# ------------------------
@api_view(['POST'])
def check_eligibility(request):
    try:
        if not ALL_PROGRAMMES:
            return Response({
                'eligible_programmes': [],
                'total_found': 0,
                'message': 'System error: programmes not loaded'
            }, status=500)

        data = request.data or {}
        user_cluster_points = float(data.get('cluster_points', 0))
        user_grades = data.get('grades', {})

        student_code_grade_map = student_grades_to_code_map(user_grades)
        eligible_programmes = []
        filtered_out = 0

        for prog in ALL_PROGRAMMES:
            prog_cp = prog.get('cluster_points', 0)
            if user_cluster_points < prog_cp:
                continue

            requirements_cells = prog.get('requirements', [])
            groups = []
            for cell in requirements_cells:
                parsed = parse_requirement_cell(cell)
                if parsed:
                    groups.extend(parsed)

            if not groups:
                eligible_programmes.append({
                    'programme_code': prog.get('programme_code'),
                    'programme_name': prog.get('programme_name'),
                    'university': prog.get('university'),
                    'cluster_points': prog.get('cluster_points'),
                    'meets_subjects': True
                })
                continue

            all_groups_met = True
            for codes, req_grade in groups:
                if not meets_group_requirement(codes, req_grade, student_code_grade_map):
                    all_groups_met = False
                    break

            if all_groups_met:
                eligible_programmes.append({
                    'programme_code': prog.get('programme_code'),
                    'programme_name': prog.get('programme_name'),
                    'university': prog.get('university'),
                    'cluster_points': prog.get('cluster_points'),
                    'meets_subjects': True
                })
            else:
                filtered_out += 1

        return Response({
            'eligible_programmes': eligible_programmes,
            'total_found': len(eligible_programmes),
            'database_total': len(ALL_PROGRAMMES),
            'programmes_filtered': filtered_out,
            'message': f'Found {len(eligible_programmes)} programmes matching criteria (cluster + subjects)'
        })

    except Exception as e:
        print(f"Eligibility error: {e}")
        return Response({
            'eligible_programmes': [],
            'total_found': 0,
            'message': f'Error: {str(e)}'
        }, status=500)

# ------------------------
# Health Check
# ------------------------
@api_view(['GET'])
def check_database(request):
    return Response({
        'total_programmes': len(ALL_PROGRAMMES),
        'message': 'Programme data loaded successfully.' if ALL_PROGRAMMES else 'No programme data loaded.'
    })

# ------------------------
# Payment Stub
# ------------------------
@api_view(['POST'])
def pay(request):
    phone = request.data.get('phone')
    amount = request.data.get('amount')
    if not phone or not amount:
        return Response({'error': 'Phone and amount required'}, status=400)
    return Response({'success': True, 'transaction_id': 'TEST_12345'})

# ------------------------
# PDF DOWNLOAD
# ------------------------
@api_view(['POST'])
def download_courses_pdf(request):
    try:
        data = request.data or {}
        eligible_programmes = data.get('eligible_programmes', [])
        user_cluster_points = data.get('cluster_points', 0)

        if not eligible_programmes:
            return Response({'error': 'No courses to download'}, status=400)

        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)

        p.setFont("Helvetica-Bold", 16)
        p.drawString(100, 750, "Eligible Course Report")
        p.setFont("Helvetica", 12)
        p.drawString(100, 720, f"Cluster Points: {user_cluster_points}")
        p.drawString(100, 700, f"Total Courses: {len(eligible_programmes)}")

        y = 660
        p.setFont("Helvetica", 9)
        for i, course in enumerate(eligible_programmes):
            if y < 50:
                p.showPage()
                y = 750
            p.drawString(100, y, f"{i+1}. {course.get('programme_name')} ({course.get('programme_code')}) - {course.get('university')}")
            y -= 15

        p.save()
        pdf = buffer.getvalue()
        buffer.close()

        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="eligible_courses_{user_cluster_points}.pdf"'
        return response
    
    except Exception as e:
        return Response({'error': str(e)}, status=500)
