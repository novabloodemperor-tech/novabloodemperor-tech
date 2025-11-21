from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
from .models import Programme

@api_view(['POST'])
def check_eligibility(request):
    try:
        data = request.data
        user_cluster_points = float(data.get('cluster_points', 0))
        
        # Get ALL programmes from database
        all_programmes = Programme.objects.all()
        print(f"📊 Checking {all_programmes.count()} programmes from database")
        
        # Filter programmes by cluster points
        eligible_programmes = []
        for programme in all_programmes:
            if user_cluster_points >= programme.cluster_points:
                eligible_programmes.append({
                    'programme_code': programme.programme_code,
                    'programme_name': programme.programme_name,
                    'university': programme.university,
                    'cluster_points': programme.cluster_points,
                    'required_cluster': programme.cluster_points
                })
        
        print(f"🎯 Found {len(eligible_programmes)} eligible programmes")
        
        return Response({
            'eligible_programmes': eligible_programmes,
            'total_found': len(eligible_programmes),
            'database_total': all_programmes.count(),
            'message': f'Found {len(eligible_programmes)} out of {all_programmes.count()} total courses'
        })
        
    except Exception as e:
        print(f"❌ Error in eligibility check: {e}")
        return Response({
            'eligible_programmes': [],
            'total_found': 0,
            'message': f'Database error: {str(e)}'
        }, status=500)

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

@api_view(['GET'])
def check_database(request):
    """Check database status and contents"""
    try:
        total_programmes = Programme.objects.count()
        
        sample_programmes = []
        for programme in Programme.objects.all()[:10]:  # First 10 programmes
            sample_programmes.append({
                'programme_code': programme.programme_code,
                'programme_name': programme.programme_name,
                'university': programme.university,
                'cluster_points': programme.cluster_points
            })
        
        return Response({
            'total_programmes': total_programmes,
            'sample_programmes': sample_programmes,
            'status': 'working' if total_programmes > 0 else 'empty',
            'message': f'Database has {total_programmes} programmes'
        })
        
    except Exception as e:
        return Response({
            'total_programmes': 0,
            'sample_programmes': [],
            'status': 'error',
            'message': str(e)
        }, status=500)