from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse

def pay(request):
    if request.method == "POST":
        return JsonResponse({"message": "Payment endpoint - Mpesa integration pending"})
    return JsonResponse({"error": "Only POST allowed"}, status=400)

@api_view(['POST'])
def check_eligibility(request):
    try:
        data = request.data
        
        # Get user's grades and cluster points
        user_grades = data.get('grades', {})
        user_cluster_points = float(data.get('cluster_points', 0))
        
        # Temporary test response - replace with real logic later
        eligible_programmes = []
        
        # Add some test programmes based on cluster points
        if user_cluster_points >= 40:
            eligible_programmes.append({
                'programme_code': 'SC001',
                'programme_name': 'Computer Science',
                'university': 'University of Nairobi',
                'cluster_points': user_cluster_points,
                'required_cluster': 40
            })
        
        if user_cluster_points >= 38:
            eligible_programmes.append({
                'programme_code': 'BA001',
                'programme_name': 'Business Administration', 
                'university': 'Kenyatta University',
                'cluster_points': user_cluster_points,
                'required_cluster': 38
            })
        
        if user_cluster_points >= 42:
            eligible_programmes.append({
                'programme_code': 'ME001',
                'programme_name': 'Medicine',
                'university': 'University of Nairobi',
                'cluster_points': user_cluster_points, 
                'required_cluster': 42
            })
        
        return Response({
            'eligible_programmes': eligible_programmes,
            'total_found': len(eligible_programmes),
            'message': 'This is a test response. Connect database for real data.'
        })
        
    except Exception as e:
        return Response({'error': str(e)}, status=500)