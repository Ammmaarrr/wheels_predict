@echo off
REM Batch script to run multiple PakWheels spiders in parallel with different page ranges

start cmd /k "scrapy crawl used_cars -a start_page=1 -a end_page=2000"
start cmd /k "scrapy crawl used_cars -a start_page=2001 -a end_page=4000"
start cmd /k "scrapy crawl used_cars -a start_page=4001 -a end_page=6000"
start cmd /k "scrapy crawl used_cars -a start_page=6001 -a end_page=8000"
REM Add more lines as needed for more parallel spiders

echo All spiders started in separate terminals.
pause
