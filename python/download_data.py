import kagglehub
import shutil
from pathlib import Path

path = kagglehub.dataset_download("pavansubhasht/ibm-hr-analytics-attrition-dataset")
print("Path to dataset files:", path)

dest = Path(__file__).resolve().parent.parent / "data_raw"
dest.mkdir(exist_ok=True)

for f in Path(path).glob("*.csv"):
    shutil.copy(f, dest / f.name)
    print("Copied:", f.name, "->", dest)
    