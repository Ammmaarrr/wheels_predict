@echo off
REM Batch script to run 12 PakWheels spiders in parallel with different page ranges and log files

start cmd /k "scrapy crawl used_cars -a start_page=67 -a end_page=357 -s LOG_FILE=spider1.log"
start cmd /k "scrapy crawl used_cars -a start_page=358 -a end_page=648 -s LOG_FILE=spider2.log"
start cmd /k "scrapy crawl used_cars -a start_page=649 -a end_page=939 -s LOG_FILE=spider3.log"
start cmd /k "scrapy crawl used_cars -a start_page=940 -a end_page=1230 -s LOG_FILE=spider4.log"
start cmd /k "scrapy crawl used_cars -a start_page=1231 -a end_page=1521 -s LOG_FILE=spider5.log"
start cmd /k "scrapy crawl used_cars -a start_page=1522 -a end_page=1812 -s LOG_FILE=spider6.log"
start cmd /k "scrapy crawl used_cars -a start_page=1813 -a end_page=2103 -s LOG_FILE=spider7.log"
start cmd /k "scrapy crawl used_cars -a start_page=2104 -a end_page=2394 -s LOG_FILE=spider8.log"
start cmd /k "scrapy crawl used_cars -a start_page=2395 -a end_page=2685 -s LOG_FILE=spider9.log"
start cmd /k "scrapy crawl used_cars -a start_page=2686 -a end_page=2976 -s LOG_FILE=spider10.log"
start cmd /k "scrapy crawl used_cars -a start_page=2977 -a end_page=3267 -s LOG_FILE=spider11.log"
start cmd /k "scrapy crawl used_cars -a start_page=3268 -a end_page=3557 -s LOG_FILE=spider12.log"

echo All spiders started in separate terminals with log files.
pause
