# add_test_data.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'course_pilot.settings')
django.setup()

from course_pilot.courses.models import Programme

def add_test_programmes():
    print("📝 Adding test programmes to database...")
    
    # Clear any existing data
    Programme.objects.all().delete()
    
    # Add 10 test programmes with low cluster points
    test_programmes = [
        {"code": "TEST001", "name": "Computer Science", "uni": "University of Nairobi", "points": 25.0},
        {"code": "TEST002", "name": "Business Administration", "uni": "Kenyatta University", "points": 22.0},
        {"code": "TEST003", "name": "Education Arts", "uni": "Moi University", "points": 18.0},
        {"code": "TEST004", "name": "Hospitality Management", "uni": "Technical University of Kenya", "points": 20.0},
        {"code": "TEST005", "name": "Information Technology", "uni": "JKUAT", "points": 24.0},
        {"code": "TEST006", "name": "Commerce", "uni": "University of Nairobi", "points": 26.0},
        {"code": "TEST007", "name": "Arts in Design", "uni": "Kenyatta University", "points": 19.0},
        {"code": "TEST008", "name": "Environmental Science", "uni": "Egerton University", "points": 21.0},
        {"code": "TEST009", "name": "Communication Studies", "uni": "Daystar University", "points": 23.0},
        {"code": "TEST010", "name": "Agriculture", "uni": "University of Eldoret", "points": 17.0},
    ]
    
    for prog in test_programmes:
        Programme.objects.create(
            programme_code=prog["code"],
            programme_name=prog["name"],
            university=prog["uni"],
            cluster_points=prog["points"]
        )
    
    print(f"✅ Added {len(test_programmes)} test programmes")
    print(f"📊 Total programmes in database: {Programme.objects.count()}")

if __name__ == "__main__":
    add_test_programmes()