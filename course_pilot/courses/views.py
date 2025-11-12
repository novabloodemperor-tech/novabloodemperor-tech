from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .pdf_utils import generate_courses_pdf
from django.http import HttpResponse

@csrf_exempt
def download_courses_pdf(request):
    if request.method == "POST":
        try:
            import json
            data = json.loads(request.body)
            
            eligible_programmes = data.get('eligible_programmes', [])
            user_points = data.get('user_points', '')
            user_grades = data.get('user_grades', {})
            
            # Generate PDF
            pdf_content = generate_courses_pdf(eligible_programmes, user_points, user_grades)
            
            # Create HTTP response with PDF
            response = HttpResponse(pdf_content, content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="coursepilot_courses.pdf"'
            return response
            
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    
    return JsonResponse({"error": "Only POST allowed"}, status=400)



def pay(request):
    if request.method == "POST":
        try:
            import json
            data = json.loads(request.body)
            phone = data.get("phone")
            amount = data.get("amount")
            
            if not phone or not amount:
                return JsonResponse({"error": "Phone and amount are required"}, status=400)
            
            # Format phone number
            if phone.startswith('0'):
                phone = '254' + phone[1:]
            elif phone.startswith('+'):
                phone = phone[1:]
            
            account_ref = data.get("account_ref", "CoursePilot")
            description = data.get("desc", "Course Matching Service")
            
            # Call real M-Pesa
            from .mpesa import stk_push
            res = stk_push(phone, amount, account_ref, description)
            return JsonResponse(res)
            
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    
        return JsonResponse({"error": "Only POST allowed"}, status=400)

@api_view(['POST'])
def check_eligibility(request):
    data = request.data
    
    # Get user's grades and cluster points
    user_grades = data.get('grades', {})
    user_cluster_points = float(data.get('cluster_points', 0))
    
    # Test data - replace with database later
    test_programmes = [
        {
            'programme_code': 'SC001',
            'programme_name': 'Computer Science',
            'university': 'University of Nairobi',
            'cluster_points': 40,
            'required_cluster': 40
        },
        {
            'programme_code': 'BA001',
            'programme_name': 'Business Administration',
            'university': 'Kenyatta University', 
            'cluster_points': 38,
            'required_cluster': 38
        },
        {
            'programme_code': 'ME001',
            'programme_name': 'Medicine',
            'university': 'University of Nairobi',
            'cluster_points': 42,
            'required_cluster': 42
        },
        {
            'programme_code': 'EN001',
            'programme_name': 'Engineering',
            'university': 'JKUAT',
            'cluster_points': 41,
            'required_cluster': 41
        }
    ]
    
    # Filter programmes by cluster points
    eligible_programmes = []
    for programme in test_programmes:
        if user_cluster_points >= programme['cluster_points']:
            eligible_programmes.append(programme)
    
    return Response({
        'eligible_programmes': eligible_programmes,
        'total_found': len(eligible_programmes),
        'message': 'Demo data - Connect database for real course information'
    })