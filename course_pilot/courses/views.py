from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Programme, SubjectRequirement

@api_view(['POST'])
def check_eligibility(request):
    data = request.data
    
    # Get user's grades and cluster points
    user_grades = data.get('grades', {})
    user_cluster_points = float(data.get('cluster_points', 0))
    
    eligible_programmes = []
    
    # Check all programmes
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
        'total_found': len(eligible_programmes)
    })

def meets_subject_requirements(requirements, user_grades):
    # Convert grade letters to comparable values
    grade_order = {'A': 12, 'A-': 11, 'B+': 10, 'B': 9, 'B-': 8, 
                   'C+': 7, 'C': 6, 'C-': 5, 'D+': 4, 'D': 3, 'D-': 2, 'E': 1}
    
    # Check each required subject
    required_subjects = [
        (requirements.subject_1, requirements.grade_1),
        (requirements.subject_2, requirements.grade_2),
        (requirements.subject_3, requirements.grade_3),
        (requirements.subject_4, requirements.grade_4),
    ]
    
    for subject, min_grade in required_subjects:
        if subject and min_grade:  # Only check if subject is required
            user_grade = user_grades.get(subject, 'E')
            if grade_order.get(user_grade, 0) < grade_order.get(min_grade, 0):
                return False
    return True