from pathlib import Path
import os

BOT_NAME = 'pakwheels'
SPIDER_MODULES = ['pakwheels.pakwheels.spiders']
NEWSPIDER_MODULE = 'pakwheels.pakwheels.spiders'

ROBOTSTXT_OBEY = True
DOWNLOAD_DELAY = 0.5
CONCURRENT_REQUESTS = 8

# Retry/Timeouts for robustness
RETRY_ENABLED = True
RETRY_TIMES = 3
DOWNLOAD_TIMEOUT = 20
RETRY_HTTP_CODES = [429, 500, 502, 503, 504, 522, 524, 408]

# AutoThrottle to play nice
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 0.5
AUTOTHROTTLE_MAX_DELAY = 10.0
AUTOTHROTTLE_TARGET_CONCURRENCY = 2.0
AUTOTHROTTLE_DEBUG = False

# Feed export defaults
FEED_EXPORT_ENCODING = 'utf-8'
FEEDS = {
    # When -o is provided on CLI, that takes precedence
}

# Dupe filter and job persistence (can be overridden per run)
DUPEFILTER_CLASS = 'scrapy.dupefilters.RFPDupeFilter'
JOBDIR = 'scrapy-job/pakwheels'

DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'scrapy_user_agents.middlewares.RandomUserAgentMiddleware': 400,
}

ITEM_PIPELINES = {
    # Download images first so CSV has local image paths
    'pakwheels.pakwheels.image_pipeline.PakwheelsImagesPipeline': 80,
    # Unified CSV pipeline (activated via env var UNIFIED_CSV_PATH); runs after images
    'pakwheels.pakwheels.unified_csv_pipeline.UnifiedCsvPipeline': 100,
    # 'pakwheels.async_pipelines.AsyncPostgresPipeline': 300,
    # 'pakwheels.pipelines.PostgresPipeline': 300,
}

# Default headers
DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
}

# Images storage configuration
try:
    # settings.py is at scrapers/pakwheels/pakwheels/settings.py
    # parents[3] -> workspace root (d:\data_scrapping_pakwheels)
    ROOT = Path(__file__).resolve().parents[3]
except Exception:
    ROOT = Path.cwd()

IMAGES_STORE = os.environ.get('IMAGES_STORE', str(ROOT / 'data' / 'images'))
MEDIA_ALLOW_REDIRECTS = True
IMAGES_EXPIRES = 90  # days to keep without re-downloading
