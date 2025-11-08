import pdfplumber
import pandas as pd
from pathlib import Path

# === Input PDFs ===
pdfs = [
    r"C:\Users\HP\Downloads\The course pilot\data\kuccps-pdfs\kuccps_programmes.pdf",
    r"C:\Users\HP\Downloads\The course pilot\data\kuccps-pdfs\kuccps_cluster.pdf",
]

# === Output folder ===
out_dir = Path(r"C:\Users\HP\Downloads\The course pilot\data\cleaned")
out_dir.mkdir(parents=True, exist_ok=True)

for pdf_path in pdfs:
    print(f"📄 Reading {pdf_path} ...")
    all_rows = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            table = page.extract_table()
            if table:
                all_rows.extend(table)
    if all_rows:
        df = pd.DataFrame(all_rows)
        name = "KUCCPS_Requirements_Cleaned.csv" if "programme" in pdf_path.lower() else "KUCCPS_ClusterPoints_Cleaned.csv"
        df.to_csv(out_dir / name, index=False)
        print(f"✅ Saved {name} with {len(df)} rows")
    else:
        print(f"⚠️ No tables found in {pdf_path}")

print("🎉 All done! Check your 'data\\cleaned' folder.")
