from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
import traceback

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
        
        print("DEBUG: Starting eligibility check...")
        
        # Try to import Programme
        try:
            from .models import Programme
            print(f"DEBUG: Programme import successful, count: {Programme.objects.count()}")
        except Exception as e:
            print(f"DEBUG: Programme import failed: {e}")
            return Response({
                'eligible_programmes': [],
                'total_found': 0,
                'message': f'Database error: {str(e)}'
            }, status=500)
        
        eligible_programmes = []
        
        # Check all programmes in database
        for programme in Programme.objects.all():
            # Check cluster points
            if user_cluster_points >= programme.cluster_points:
                eligible_programmes.append({
                    'programme_code': programme.programme_code,
                    'programme_name': programme.programme_name,
                    'university': programme.university,
                    'cluster_points': programme.cluster_points,
                    'required_cluster': programme.cluster_points
                })
        
        print(f"DEBUG: Found {len(eligible_programmes)} eligible programmes")
        
        return Response({
            'eligible_programmes': eligible_programmes,
            'total_found': len(eligible_programmes),
            'message': 'Based on official KUCCPS placement data'
        })
        
    except Exception as e:
        print(f"DEBUG: General error: {e}")
        print(f"DEBUG: Traceback: {traceback.format_exc()}")
        return Response({
            'eligible_programmes': [],
            'total_found': 0,
            'message': f'General error: {str(e)}'
        }, status=500)