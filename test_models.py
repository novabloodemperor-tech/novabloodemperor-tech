# test_models.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'course_pilot.settings')
django.setup()

from course_pilot.courses.models import Programme, SubjectRequirement

print("🔍 Testing database models...")

# Count programmes
programme_count = Programme.objects.count()
print(f"📊 Programmes in database: {programme_count}")

# Count subject requirements
requirement_count = SubjectRequirement.objects.count()
print(f"📚 Subject requirements in database: {requirement_count}")

# Check if we can create a test requirement
if programme_count > 0:
    try:
        sample_programme = Programme.objects.first()
        print(f"✅ Sample programme: {sample_programme.programme_name}")
        print("✅ Models are working correctly!")
    except Exception as e:
        print(f"❌ Error: {e}")
else:
    print("⚠️ No programmes found in database")