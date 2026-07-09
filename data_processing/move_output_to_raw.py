import shutil
from datetime import datetime
import os

RAW_DIR = "data/raw"

# Move output.csv to data/raw/ with a timestamped name
def move_output_csv():
    src = "output.csv"
    if not os.path.exists(src):
        print("output.csv not found in project root.")
        return
    os.makedirs(RAW_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d")
    dst = os.path.join(RAW_DIR, f"output_{timestamp}.csv")
    shutil.move(src, dst)
    print(f"Moved {src} to {dst}")

if __name__ == "__main__":
    move_output_csv()
