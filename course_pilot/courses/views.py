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
    "history": ["HIS", "HAG"],  # CSV may use HAG / HIS
    "cre": ["CRE"],
    "religious education": ["CRE", "IRE"],
    "ire": ["IRE"],
    "agriculture": ["AGR"],
    "business studies": ["BST", "BUS"],  # CSV uses BST code for Business Studies
    "business": ["BST", "BUS"],
    "computer studies": ["CMP", "CS"],
    "computer science": ["CS", "CMP"],
    "general science": ["GSC"],
    "music": ["MUC", "MUS"],
    "french": ["FRE"],
    "german": ["GER"],
    "arabic": ["ARB"],
    "home science": ["HSC"],
    # add more synonyms as needed
}

# Some CSV tokens may appear with slashes/variants, normalize them to canonical code
ALIAS_TO_CODE = {
    "HAG": "HIS",
    "HIS": "HIS",
    "GSC": "GSC",
    "CMP": "CS",  # we will allow both CMP and CS when matching
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
    # ... extend if you see more codes in CSV
}

# Regex to extract code prefix e.g. "MAT A(121)" -> "MAT", "BIO(231)" -> "BIO"
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
            header = next(reader, None)  # skip header if present
            for row in reader:
                # Ensure row long enough
                if len(row) < 6:
                    continue
                try:
                    programme_code = row[1].strip()
                    university = row[2].strip()
                    programme_name = row[3].strip()

                    # 2024 cluster points is column index 5 (0-based)
                    cp_raw = row[5].strip() if len(row) > 5 else ""
                    try:
                        cluster_points = float(cp_raw) if cp_raw not in ("", "-", None) else 0.0
                    except:
                        # if comma decimal or other format, try replace
                        cp_clean = cp_raw.replace(",", ".")
                        cluster_points = float(cp_clean) if cp_clean not in ("", "-", None) else 0.0

                    # requirements columns (SUBJECT 1..4) are indices 6..9
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
                        "requirements": subj_reqs  # list of up to 4 strings
                    })
                except Exception as e:
                    # skip malformed row but continue
                    print(f"Skipping row due to parse error: {e}")
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
    key = name.strip().lower()
    return key

def student_grades_to_code_map(student_grades: dict):
    """
    Convert frontend grades dict { "Mathematics": "B+" } to code->grade mapping,
    e.g. { "MAT": "B+", "ENG": "C" }
    """
    code_grade = {}
    for name, grade in (student_grades or {}).items():
        if not name or not grade:
            continue
        key = normalize_subject_name(name)
        # try direct mapping
        codes = NAME_TO_CODE.get(key)
        if not codes:
            # attempt heuristic: take first 3 letters uppercase
            heuristic = re.sub(r'[^A-Za-z]', '', key)[:3].upper()
            codes = [heuristic]
        for code in codes:
            # canonical via alias mapping
            canon = ALIAS_TO_CODE.get(code, code)
            code_grade[canon] = grade.strip().upper()
    return code_grade

def extract_codes_from_requirement_token(token: str):
    """
    Given a token like "BIO(231)" or "MAT A(121)" or "HAG / HIS" extract list of code prefixes
    """
    if not token:
        return []
    # normalize separators
    token = token.replace("/", "/").replace(" / ", "/")
    parts = [p.strip() for p in re.split(r'[\/;|]', token) if p.strip()]
    codes = []
    for p in parts:
        # find code-like parts
        m = CODE_PREFIX_RE.search(p.upper())
        if m:
            code = m.group(1)
            code = ALIAS_TO_CODE.get(code, code)
            codes.append(code)
    return codes

def parse_requirement_cell(cell_text: str):
    """
    Parse one requirement cell like:
      "MAT A(121):C+"
      "BIO(231)/CHE(233)/PHY(232):C"
    Returns list of groups: each group is (list_of_codes, required_grade)
    For a single cell, we return a list with one group.
    """
    if not cell_text or not str(cell_text).strip():
        return []
    text = str(cell_text).strip()
    # Some rows could have multiple requirements separated by commas within a cell - treat cell as single group.
    # Split on ':' to separate subjects and grade
    try:
        if ":" in text:
            left, right = text.rsplit(":", 1)
            required_grade = right.strip().upper()
            codes = extract_codes_from_requirement_token(left)
            if codes:
                return [(codes, required_grade)]
            else:
                return []
        else:
            # if no colon, try to find grade token at end e.g. "... C+" -> last token
            parts = text.split()
            possible_grade = parts[-1].strip().upper()
            if possible_grade in GRADE_VALUE:
                # subjects are everything before last token
                left = " ".join(parts[:-1])
                codes = extract_codes_from_requirement_token(left)
                return [(codes, possible_grade)] if codes else []
            else:
                return []
    except Exception as e:
        print(f"Error parsing requirement cell '{cell_text}': {e}")
        return []

def meets_group_requirement(codes: list, required_grade: str, student_code_grade_map: dict):
    """
    codes: list of possible code prefixes (OR group)
    required_grade: e.g. 'C+'
    student_code_grade_map: e.g. {'MAT': 'B+', 'CHE': 'C'}
    If student has any of the codes with >= required_grade -> True
    """
    if not codes:
        return True  # empty group -> treat as satisfied
    required_value = GRADE_VALUE.get(required_grade, 0)
    for code in codes:
        # student may have code directly or equivalent alias
        stud_grade = student_code_grade_map.get(code)
        if not stud_grade:
            # try alternate aliases (e.g. 'CS' vs 'CMP')
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

        # Convert student grades (names) -> code->grade map
        student_code_grade_map = student_grades_to_code_map(user_grades)

        eligible_programmes = []
        filtered_out = 0

        for prog in ALL_PROGRAMMES:
            prog_cp = prog.get('cluster_points', 0)
            if user_cluster_points < prog_cp:
                continue  # fails cluster points

            # Collect all requirement groups from SUBJECT 1-4 cells
            requirements_cells = prog.get('requirements', [])  # list up to 4 strings
            groups = []
            for cell in requirements_cells:
                parsed = parse_requirement_cell(cell)
                if parsed:
                    groups.extend(parsed)

            # If no parsed requirements (empty) --> allow by cluster points only
            if not groups:
                eligible_programmes.append({
                    'programme_code': prog.get('programme_code'),
                    'programme_name': prog.get('programme_name'),
                    'university': prog.get('university'),
                    'cluster_points': prog.get('cluster_points'),
                    'meets_subjects': True
                })
                continue

            # Evaluate every group (AND across groups)
            all_groups_met = True
            for codes, req_grade in groups:
                met = meets_group_requirement(codes, req_grade, student_code_grade_map)
                if not met:
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
# Health / DB check
# ------------------------
@api_view(['GET'])
def check_database(request):
    return Response({
        'total_programmes': len(ALL_PROGRAMMES),
        'message': 'Programme data loaded successfully.' if ALL_PROGRAMMES else 'No programme data loaded.'
    })


# ------------------------
# Payment (simple stub)
# ------------------------
@api_view(['POST'])
def pay(request):
    phone = request.data.get('phone')
    amount = request.data.get('amount')
    if not phone or not amount:
        return Response({'error': 'Phone and amount required'}, status=400)
    return Response({'success': True, 'transaction_id': 'TEST_12345'})


# ------------------------
# PDF download (keeps your previous logic)
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
