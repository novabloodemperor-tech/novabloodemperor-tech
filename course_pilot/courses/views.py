from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse

@api_view(['POST'])
def check_eligibility(request):
    try:
        data = request.data
        user_cluster_points = float(data.get('cluster_points', 0))
        
        # Import models
        from .models import Programme
        
        # Get all programmes that match the cluster points
        matching_programmes = Programme.objects.filter(cluster_points__lte=user_cluster_points)
        
        # Convert to response format
        eligible_programmes = []
        for programme in matching_programmes:
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
            'message': f'Found {len(eligible_programmes)} courses matching your cluster points'
        })
        
    except Exception as e:
        return Response({
            'eligible_programmes': [],
            'total_found': 0,
            'message': f'Error: {str(e)}'
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
    """Check how many programmes are in the database"""
    from .models import Programme
    count = Programme.objects.count()
    
    sample_programmes = []
    for programme in Programme.objects.all()[:5]:
        sample_programmes.append({
            'code': programme.programme_code,
            'name': programme.programme_name,
            'university': programme.university,
            'points': programme.cluster_points
        })
    
    return Response({
        'total_programmes': count,
        'sample_programmes': sample_programmes,
        'status': 'working' if count > 0 else 'empty'
    })