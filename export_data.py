# export_data.py
import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'course_pilot.settings')
django.setup()

from course_pilot.courses.models import Programme, SubjectRequirement

print("📤 Exporting database data...")

# Export programmes
programmes_data = []
for programme in Programme.objects.all():
    programmes_data.append({
        'programme_code': programme.programme_code,
        'programme_name': programme.programme_name,
        'university': programme.university,
        'cluster_points': programme.cluster_points
    })

# Save to JSON file
with open('programmes_export.json', 'w', encoding='utf-8') as f:
    json.dump(programmes_data, f, indent=2, ensure_ascii=False)

print(f"✅ Exported {len(programmes_data)} programmes to programmes_export.json")
print("📁 File created: programmes_export.json")