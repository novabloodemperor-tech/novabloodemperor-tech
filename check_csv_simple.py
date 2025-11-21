import csv
import os

print("🔍 Checking CSV file structure...")

def check_csv_file(filepath, description):
    print(f"\n{description}:")
    print(f"File: {filepath}")
    
    if not os.path.exists(filepath):
        print("❌ File not found!")
        return
    
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            # Read first few lines to understand structure
            reader = csv.reader(file)
            
            # Get header row
            headers = next(reader)
            print(f"✅ Columns ({len(headers)}): {headers}")
            
            # Get first 3 data rows
            print("First 3 rows:")
            row_count = 0
            for row in reader:
                print(f"  Row {row_count + 1}: {row}")
                row_count += 1
                if row_count >= 3:
                    break
            
            # Count total rows (including header)
            total_rows = 1 + sum(1 for _ in reader)  # 1 for header + data rows
            print(f"📊 Total rows: {total_rows}")
            
    except Exception as e:
        print(f"❌ Error reading file: {e}")

# Check both files
check_csv_file("data/cleaned/KUCCPS_ClusterPoints_Cleaned.csv", "📊 CLUSTER POINTS FILE")
check_csv_file("data/cleaned/KUCCPS_Requirements_Cleaned.csv", "📚 REQUIREMENTS FILE")

print(f"\nCurrent directory: {os.getcwd()}")