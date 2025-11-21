from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse

@api_view(['POST'])
def pay(request):
    try:
        phone = request.data.get("phone")
        amount = request.data.get("amount")
        
        if not phone or not amount:
            return Response({"error": "Phone and amount are required"}, status=400)
        
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
        return Response({
            "error": "PDF feature coming soon",
            "message": "PDF download will be available in the next update"
        }, status=503)
        
    except Exception as e:
        return Response({"error": str(e)}, status=500)


@api_view(['POST'])
def check_eligibility(request):
    try:
        data = request.data

        # Get user's grades and cluster points
        user_grades = data.get('grades', {})
        user_cluster_points = float(data.get('cluster_points', 0))

        # Import here to avoid circular imports
        from .models import Programme, SubjectRequirement

        eligible_programmes = []

        # Check all programmes in database
        for programme in Programme.objects.all():
            # Check cluster points first
            if user_cluster_points >= programme.cluster_points:
                # Check if programme has subject requirements
                requirements = SubjectRequirement.objects.filter(programme=programme).first()
                
                # If no specific requirements found, include the programme
                if not requirements:
                    eligible_programmes.append({
                        'programme_code': programme.programme_code,
                        'programme_name': programme.programme_name,
                        'university': programme.university,
                        'cluster_points': programme.cluster_points,
                        'required_cluster': programme.cluster_points
                    })
                else:
                    # For now, include programmes even if they have requirements
                    # We'll implement proper subject checking later
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