# check_requirements.py
import pandas as pd

print("🔍 Checking subject requirements data...")

try:
    # Check if we have requirements CSV
    req_df = pd.read_csv("data/cleaned/KUCCPS_Requirements_Cleaned.csv")
    print(f"✅ Requirements file found: {len(req_df)} rows")
    print("Columns:", req_df.columns.tolist())
    print("\nFirst 5 rows:")
    print(req_df.head())
    
    # Check the structure
    print(f"\n📊 File structure:")
    for col in req_df.columns:
        unique_vals = req_df[col].dropna().unique()
        print(f"Column '{col}': {len(unique_vals)} unique values")
        if len(unique_vals) < 10:
            print(f"   Sample: {list(unique_vals[:5])}")
            
except Exception as e:
    print(f"❌ Error: {e}")