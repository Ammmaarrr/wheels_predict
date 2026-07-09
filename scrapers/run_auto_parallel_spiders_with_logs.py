import math
import subprocess

def main():
    total_listings = 59666  # Update if needed
    listings_per_page = 25
    total_pages = math.ceil(total_listings / listings_per_page)
    start_page = 67  # Update if you want to skip already scraped pages
    end_page = total_pages
    num_spiders = int(input(f"How many parallel spiders do you want to run? "))
    pages_per_spider = math.ceil((end_page - start_page + 1) / num_spiders)

    print(f"Total pages: {total_pages}, Pages per spider: {pages_per_spider}")

    for i in range(num_spiders):
        s_page = start_page + i * pages_per_spider
        e_page = min(s_page + pages_per_spider - 1, end_page)
        if s_page > end_page:
            break
        log_file = f"spider{i+1}.log"
        cmd = [
            "scrapy", "crawl", "used_cars",
            "-a", f"start_page={s_page}",
            "-a", f"end_page={e_page}",
            "-s", f"LOG_FILE={log_file}"
        ]
        print(f"Launching spider for pages {s_page} to {e_page} (log: {log_file})...")
        subprocess.Popen(cmd)

if __name__ == "__main__":
    main()
