import subprocess
from datetime import datetime
import os

def run_scrapy_spider():
    # Create data/raw directory if it doesn't exist
    os.makedirs("data/raw", exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d")
    output_file = f"data/raw/output_{timestamp}.csv"
    cmd = f"scrapy crawl used_cars -o \"{output_file}\" -s CONCURRENT_REQUESTS=20"
    subprocess.run(cmd, shell=True)

if __name__ == "__main__":
    run_scrapy_spider()
