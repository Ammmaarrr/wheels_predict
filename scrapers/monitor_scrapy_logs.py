import time
import glob
import re

def monitor_logs(log_pattern='*.log', interval=10):
    print('Monitoring Scrapy logs for errors and bans...')
    error_regex = re.compile(r'(ERROR|429|403|timeout|ban)', re.IGNORECASE)
    while True:
        for log_file in glob.glob(log_pattern):
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()[-200:]
                for line in lines:
                    if error_regex.search(line):
                        print(f"[ALERT] {log_file}: {line.strip()}")
        time.sleep(interval)

if __name__ == '__main__':
    monitor_logs()
