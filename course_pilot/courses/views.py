from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
from django.db import connection

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
    return Response({
        "error": "PDF feature coming soon",
        "message": "PDF download will be available in the next update"
    }, status=503)

@api_view(['POST'])
def check_eligibility(request):
    try:
        data = request.data
        
        # Get user's grades and cluster points
        user_grades = data.get('grades', {})
        user_cluster_points = float(data.get('cluster_points', 0))
        
        # Check if database tables exist
        tables = connection.introspection.table_names()
        if 'courses_programme' not in tables:
            return Response({
                'eligible_programmes': [],
                'total_found': 0,
                'message': 'Database not ready. Please wait a moment and try again.'
            }, status=503)
        
        # Import Programme model
        from .models import Programme
        
        # Get all programmes from database
        programmes = Programme.objects.all()
        
        if programmes.count() == 0:
            return Response({
                'eligible_programmes': [],
                'total_found': 0,
                'message': 'No courses found in database. Please contact support.'
            }, status=503)
        
        eligible_programmes = []
        
        # Check all programmes in database
        for programme in programmes:
            # Check cluster points
            if user_cluster_points >= programme.cluster_points:
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
            'message': f'Based on {programmes.count()} KUCCPS courses'
        })
        
    except Exception as e:
        return Response({
            'eligible_programmes': [],
            'total_found': 0,
            'message': f'Database error: {str(e)}'
        }, status=500)