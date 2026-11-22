import os
import pandas as pd
from pathlib import Path
from urllib.parse import quote_plus
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data_raw"
load_dotenv(ROOT / ".env")

user = os.getenv("MYSQL_USER")
pwd = quote_plus(os.getenv("MYSQL_PASSWORD", ""))
host = os.getenv("MYSQL_HOST", "localhost")
port = os.getenv("MYSQL_PORT", "3306")

engine = create_engine(f"mysql+pymysql://{user}:{pwd}@{host}:{port}/wfm_staging?charset=utf8mb4")

SKIP = {"WA_Fn-UseC_-HR-Employee-Attrition.csv"}
CHUNK = 50_000

files = sorted(f for f in RAW.glob("*.csv") if f.name not in SKIP)
print(f"Loading {len(files)} files into wfm_staging...\n")

results = []
for f in files:
    table = f.stem
    csv_rows = 0
    first = True
    for chunk in pd.read_csv(f, dtype=str, chunksize=CHUNK):
        chunk.to_sql(table, engine, if_exists="replace" if first else "append",
                     index=False, chunksize=5000, method="multi")
        csv_rows += len(chunk)
        first = False
    with engine.connect() as conn:
        db_rows = conn.execute(text(f"SELECT COUNT(*) FROM `{table}`")).scalar()
    ok = "OK" if csv_rows == db_rows else "MISMATCH"
    results.append((table, csv_rows, db_rows, ok))
    print(f"{table:28s} csv={csv_rows:>9,}  table={db_rows:>9,}  {ok}")

print("\nAll counts match." if all(r[3] == "OK" for r in results)
      else "\nSome counts do not match. Check the lines marked MISMATCH.")