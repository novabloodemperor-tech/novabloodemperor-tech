import pandas as pd
import os

print("🔍 Checking CSV file structure...")

try:
    # Check cluster points file
    cluster_file = "data/cleaned/KUCCPS_ClusterPoints_Cleaned.csv"
    cluster_df = pd.read_csv(cluster_file)
    print("\n📊 CLUSTER POINTS FILE:")
    print(f"Rows: {len(cluster_df)}")
    print("Columns:", cluster_df.columns.tolist())
    print("\nFirst 3 rows:")
    print(cluster_df.head(3))
    
    # Check requirements file  
    req_file = "data/cleaned/KUCCPS_Requirements_Cleaned.csv"
    req_df = pd.read_csv(req_file)
    print("\n\n📚 REQUIREMENTS FILE:")
    print(f"Rows: {len(req_df)}")
    print("Columns:", req_df.columns.tolist())
    print("\nFirst 3 rows:")
    print(req_df.head(3))
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("Current directory:", os.getcwd())
    print("Files in data/cleaned directory:")
    try:
        print(os.listdir("data/cleaned"))
    except:
        print("Could not list directory")