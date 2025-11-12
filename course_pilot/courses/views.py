from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
#from .pdf_utils import generate_courses_pdf
from django.http import HttpResponse


@api_view(['POST'])
def pay(request):
    try:
        phone = request.data.get("phone")
        amount = request.data.get("amount")
        
        if not phone or not amount:
            return Response({"error": "Phone and amount are required"}, status=400)
        
        # Format phone number
        if phone.startswith('0'):
            phone = '254' + phone[1:]
        elif phone.startswith('+'):
            phone = phone[1:]
        
        # Simple test response
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
        eligible_programmes = request.data.get('eligible_programmes', [])
        user_points = request.data.get('user_points', '')
        user_grades = request.data.get('user_grades', {})
        
        # Generate PDF
        pdf_content = generate_courses_pdf(eligible_programmes, user_points, user_grades)
        
        # Create HTTP response with PDF
        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="coursepilot_courses.pdf"'
        return response
        
    except Exception as e:
        return Response({"error": str(e)}, status=500)
@api_view(['POST'])
def check_eligibility(request):
    data = request.data
    
    # Get user's grades and cluster points
    user_grades = data.get('grades', {})
    user_cluster_points = float(data.get('cluster_points', 0))
    
    eligible_programmes = []
    
    # Check all programmes in database
    for programme in Programme.objects.all():
        # Check cluster points
        if user_cluster_points >= programme.cluster_points:
            # Check subject requirements
            requirements = SubjectRequirement.objects.filter(programme=programme).first()
            if requirements and meets_subject_requirements(requirements, user_grades):
                eligible_programmes.append({
                    'programme_code': programme.programme_code,
                    'programme_name': programme.programme_name,
                    'university': programme.university,
                    'cluster_points': programme.cluster_points,
                    'required_cluster': programme.cluster_points
                })
    
    return Response({
        'eligible_programmes': eligible_programmes,
        'total_found': len(eligible_programmes),
        'message': 'Based on official KUCCPS placement data'
    })
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