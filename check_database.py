import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'course_pilot.settings')
django.setup()

from course_pilot.courses.models import Programme

print("🔍 Checking database contents...")
total_programmes = Programme.objects.count()
print(f"📊 Total programmes in database: {total_programmes}")

if total_programmes > 0:
    print("\n📋 Sample programmes:")
    sample_programmes = Programme.objects.all()[:5]
    for i, prog in enumerate(sample_programmes):
        print(f"   {i+1}. {prog.programme_code}: {prog.programme_name}")
        print(f"      🏛️  {prog.university}")
        print(f"      📊 {prog.cluster_points} points")
        print()
else:
    print("❌ No programmes found in database!")