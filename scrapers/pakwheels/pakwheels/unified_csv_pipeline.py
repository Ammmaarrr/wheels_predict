import os
import csv
import time
from typing import Dict, Any, List
from scrapy import Item
from scrapy.exceptions import NotConfigured

# Default field order to match existing CSV headers in this repo
DEFAULT_FIELDS: List[str] = [
    'assembly', 'badges', 'bodyType', 'body_type', 'brand', 'color', 'description',
    'engine', 'engineDisplacement', 'fuelType', 'fuel_type', 'image', 'inspection_score',
    'itemCondition', 'location', 'manufacturer', 'mileage', 'mileageFromOdometer', 'model',
    'modelDate', 'name', 'price', 'priceCurrency', 'registration_city', 'seller_info',
    'seller_location', 'transmission', 'url', 'vehicleTransmission'
]


class UnifiedCsvPipeline:
    """Pipeline to write all items into a single CSV across multiple processes.

    Controlled via env var UNIFIED_CSV_PATH. Uses a simple lock file to serialize writes
    across processes (portable, no extra deps). Writes header exactly once when file is empty.
    """

    def __init__(self):
        self.path = os.environ.get('UNIFIED_CSV_PATH')
        # Start with default fields; may be replaced with existing header in open_spider
        self.fields: List[str] = list(DEFAULT_FIELDS)
        if not self.path:
            # Defer NotConfigured to open_spider so Scrapy can construct the pipeline class
            # but we will still validate in open_spider.
            pass

    @staticmethod
    def _acquire_lock(lock_path: str, retry: float = 0.05, max_wait: float = 30.0):
        start = time.time()
        while True:
            try:
                fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_RDWR)
                return fd
            except FileExistsError:
                if time.time() - start > max_wait:
                    raise TimeoutError(f"Timed out acquiring lock: {lock_path}")
                time.sleep(retry)

    @staticmethod
    def _release_lock(fd: int, lock_path: str):
        try:
            if fd is not None:
                os.close(fd)
        finally:
            try:
                os.remove(lock_path)
            except FileNotFoundError:
                pass

    def open_spider(self, spider):
        # Prefer environment variable, else allow passing via Scrapy settings (-s UNIFIED_CSV_PATH=...)
        self.path = os.environ.get('UNIFIED_CSV_PATH') or spider.crawler.settings.get('UNIFIED_CSV_PATH')
        if not self.path:
            raise NotConfigured("UNIFIED_CSV_PATH not set; UnifiedCsvPipeline disabled")
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        # Reuse existing header if file already exists to avoid schema changes mid-run
        if os.path.exists(self.path) and os.stat(self.path).st_size > 0:
            try:
                with open(self.path, 'r', encoding='utf-8', newline='') as f:
                    reader = csv.reader(f)
                    header = next(reader, None)
                    if header:
                        self.fields = header
            except Exception:
                # Keep default fields if header cannot be read
                self.fields = list(DEFAULT_FIELDS)

    def process_item(self, item: Item, spider):
        row: Dict[str, Any] = dict(item)
        # Ensure required columns present; fill missing with '' and normalize lists
        out: Dict[str, Any] = {}
        for k in self.fields:
            v = row.get(k, '')
            if v is None:
                v = ''
            # Flatten common container types for CSV
            if isinstance(v, (list, tuple)):
                try:
                    v = ';'.join(map(str, v))
                except Exception:
                    v = str(v)
            elif isinstance(v, dict):
                try:
                    import json as _json
                    v = _json.dumps(v, ensure_ascii=False)
                except Exception:
                    v = str(v)
            out[k] = v

        lock_path = self.path + '.lock'
        fd = None
        try:
            fd = self._acquire_lock(lock_path)
            file_exists = os.path.exists(self.path)
            need_header = (not file_exists) or (os.stat(self.path).st_size == 0)
            with open(self.path, 'a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self.fields)
                if need_header:
                    writer.writeheader()
                writer.writerow(out)
        finally:
            self._release_lock(fd, lock_path)
        return item
