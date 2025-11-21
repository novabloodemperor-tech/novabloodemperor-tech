# deploy_with_data.py
import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'course_pilot.settings')
django.setup()

from course_pilot.courses.models import Programme, SubjectRequirement

def deploy_data()
    print(🚀 Deploying data to database...)
    
    # Clear existing data
    Programme.objects.all().delete()
    print(🧹 Cleared existing programmes)
    
    # Import from JSON file
    try
        with open('programmes_export.json', 'r', encoding='utf-8') as f
            programmes_data = json.load(f)
        
        programme_count = 0
        for prog_data in programmes_data
            try
                Programme.objects.create(
                    programme_code=prog_data['programme_code'],
                    programme_name=prog_data['programme_name'],
                    university=prog_data['university'],
                    cluster_points=prog_data['cluster_points']
                )
                programme_count += 1
                
                if programme_count % 100 == 0
                    print(f✅ Added {programme_count} programmes...)
                    
            except Exception as e
                print(f❌ Error adding programme {e})
                continue
        
        print(f🎉 Successfully deployed {programme_count} programmes!)
        print(f📊 Total in database {Programme.objects.count()})
        
    except Exception as e
        print(f❌ Error reading export file {e})

if __name__ == __main__
    deploy_data()