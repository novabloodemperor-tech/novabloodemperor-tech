from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse

def pay(request):
    if request.method == "POST":
        return JsonResponse({"message": "Payment endpoint - Mpesa integration pending"})
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