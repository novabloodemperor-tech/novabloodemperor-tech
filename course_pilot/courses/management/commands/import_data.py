import os
import pandas as pd
from django.core.management.base import BaseCommand
from courses.models import Programme, SubjectRequirement

class Command(BaseCommand):
    help = 'Import KUCCPS data from CSV files'
    
    def handle(self, *args, **options):
        self.stdout.write("📊 Starting data import...")
        
        try:
            # Path to your CSV files
            cluster_file = "C:/Users/HP/Downloads/The course pilot/data/cleaned/KUCCPS_ClusterPoints_Cleaned.csv"
            
            # Read the CSV files
            cluster_df = pd.read_csv(cluster_file, header=None, skiprows=1)
            
            self.stdout.write(f"✅ Loaded {len(cluster_df)} programmes")
            
            # Clear existing data
            Programme.objects.all().delete()
            SubjectRequirement.objects.all().delete()
            self.stdout.write("🗑️ Cleared existing data")
            
            # Import programmes from cluster file
            programme_map = {}
            imported_count = 0
            skipped_count = 0
            duplicate_count = 0
            
            for index, row in cluster_df.iterrows():
                if len(row) >= 6:  # Make sure we have enough columns
                    programme_code = str(row[1]) if pd.notna(row[1]) else None
                    programme_name = str(row[3]) if pd.notna(row[3]) else None
                    university = str(row[2]) if pd.notna(row[2]) else "Unknown University"
                    cluster_points_str = str(row[4]) if pd.notna(row[4]) else None
                    
                    # Skip if essential data is missing
                    if not programme_code or not programme_name or programme_code == 'nan':
                        skipped_count += 1
                        continue
                    
                    # Skip if we already processed this programme code
                    if programme_code in programme_map:
                        duplicate_count += 1
                        continue
                    
                    # Handle cluster points - convert to float or use 0.0 for invalid values
                    try:
                        cluster_points = float(cluster_points_str) if cluster_points_str and cluster_points_str != '-' and 'CUTOFF' not in cluster_points_str else 0.0
                    except:
                        cluster_points = 0.0
                    
                    # Create programme
                    programme = Programme.objects.create(
                        programme_code=programme_code,
                        programme_name=programme_name,
                        university=university,
                        cluster_points=cluster_points
                    )
                    programme_map[programme_code] = programme
                    imported_count += 1
            
            self.stdout.write(f"✅ Imported {imported_count} programmes")
            self.stdout.write(f"⚠️ Skipped {skipped_count} invalid rows")
            self.stdout.write(f"⚠️ Skipped {duplicate_count} duplicate programme codes")
            
            # Create placeholder requirements
            requirements_count = 0
            for programme_code, programme in programme_map.items():
                SubjectRequirement.objects.create(
                    programme=programme,
                    subject_1="Mathematics",
                    grade_1="C+",
                    subject_2="English",
                    grade_2="C+",
                    subject_3="",
                    grade_3="",
                    subject_4="",
                    grade_4="",
                )
                requirements_count += 1
            
            self.stdout.write(f"✅ Created {requirements_count} placeholder requirements")
            self.stdout.write("🎉 Data import completed successfully!")
            
        except Exception as e:
            self.stdout.write(f"❌ Error: {e}")