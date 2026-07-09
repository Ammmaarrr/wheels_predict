import scrapy
from pakwheels.pakwheels.items import PakwheelsItem
import json
import re
import sys
from pathlib import Path
# add repository root to sys.path so we can import shared utils/logger
try:
    _ROOT = Path(__file__).resolve().parents[4]
    if str(_ROOT) not in sys.path:
        sys.path.append(str(_ROOT))
except Exception:
    pass
from utils.logger import setup_logger, log_error

logger = setup_logger(__name__)

class UsedCarsSpider(scrapy.Spider):
    name = 'used_cars'
    allowed_domains = ['pakwheels.com']
    # Provide a state dict to satisfy scrapy.extensions.spiderstate.SpiderState
    state = {}

    def __init__(self, start_page=1, end_page=1, urls_file=None, *args, **kwargs):
        """Initialize spider.

        Notes:
        - If start_page/end_page are explicitly provided via -a, we treat the crawl as
          bounded and will not paginate beyond end_page.
        - If not provided (default values), we allow unlimited pagination via next links.
        """
        # Consider crawl bounded when values differ from defaults (1/1)
        try:
            _sp = int(start_page)
            _ep = int(end_page)
        except Exception:
            _sp, _ep = 1, 1
        self._bounded_range = not (_sp == 1 and _ep == 1)
        super().__init__(*args, **kwargs)
        self.start_page = int(start_page)
        self.end_page = int(end_page)
        self.urls_file = urls_file
        self._seen_urls = set()

    def start_requests(self):
        try:
            # If a file with detail URLs is provided, refetch details directly
            if self.urls_file:
                logger.info(f"Refetching details from URLs file: {self.urls_file}")
                try:
                    with open(self.urls_file, 'r', encoding='utf-8') as f:
                        for line in f:
                            u = line.strip()
                            if not u:
                                continue
                            if u.startswith('/'):
                                u = 'https://www.pakwheels.com' + u
                            if u not in self._seen_urls:
                                self._seen_urls.add(u)
                                yield scrapy.Request(u, callback=self.parse_detail, errback=self.handle_error)
                    return
                except Exception as e:
                    log_error(logger, e, {'stage': 'start_requests', 'mode': 'urls_file', 'file': self.urls_file})

            # Otherwise, proceed page-wise
            for page in range(self.start_page, self.end_page + 1):
                url = f'https://www.pakwheels.com/used-cars/search/-/?page={page}'
                logger.info(f"Starting scrape for URL: {url}")
                yield scrapy.Request(url, callback=self.parse, errback=self.handle_error)
        except Exception as e:
            log_error(logger, e, {'stage': 'start_requests'})

    def handle_error(self, failure):
        """Handle request failures."""
        log_error(logger, failure.value, {
            'url': failure.request.url,
            'stage': 'request'
        })

    def parse(self, response):
        try:
            logger.info(f"Parsing response from {response.url}")
            listings = response.css('li[data-listing-id]')
            for li in listings:
                detail_url = li.css('div.search-title a.car-name::attr(href)').get()
                if detail_url:
                    if detail_url.startswith('/'):
                        detail_url = 'https://www.pakwheels.com' + detail_url
                    if detail_url not in self._seen_urls:
                        self._seen_urls.add(detail_url)
                        yield scrapy.Request(detail_url, callback=self.parse_detail, errback=self.handle_error)

            # ✅ Pagination handling
            next_page = response.css('ul.pagination li a[rel="next"]::attr(href)').get()
            if next_page:
                if next_page.startswith('/'):
                    next_page = 'https://www.pakwheels.com' + next_page
                # If bounded, do not go past end_page
                if self._bounded_range:
                    try:
                        import urllib.parse as _up
                        q = _up.urlparse(next_page).query
                        params = dict(_up.parse_qsl(q))
                        nxt = int(params.get('page', '0'))
                        if nxt <= int(self.end_page):
                            yield scrapy.Request(next_page, callback=self.parse, errback=self.handle_error)
                        else:
                            logger.info(f"Reached end_page={self.end_page}; stopping pagination from {response.url}")
                    except Exception:
                        # On any parsing error, be conservative and stop if bounded
                        logger.info("Pagination parsing failed in bounded mode; stopping to prevent overlap")
                else:
                    # Unbounded crawl: follow next indefinitely
                    yield scrapy.Request(next_page, callback=self.parse, errback=self.handle_error)
            else:
                # Avoid non-ASCII in logs to prevent UnicodeEncodeError on some Windows consoles
                logger.info("No more pages to crawl. Spider finished.")
        except Exception as e:
            log_error(logger, e, {
                'url': response.url,
                'stage': 'parse'
            })

    def extract_jsonld_seller(self, response):
        ld_json = response.css('script[type="application/ld+json"]::text').getall()
        for entry in ld_json:
            try:
                data = json.loads(entry)
                if isinstance(data, dict) and 'seller' in data:
                    seller = data['seller']
                    if isinstance(seller, dict):
                        return seller.get('name', '').strip()
                    elif isinstance(seller, str):
                        return seller.strip()
            except Exception as e:
                logger.debug(f"JSON-LD parse error: {e}")
        return ''

    def extract_seller_info(self, response, desc):
        # Try JSON-LD
        seller = self.extract_jsonld_seller(response)
        if seller:
            return seller
        # Try main selectors
        seller = response.css('div.seller-info h3::text').get(default='').strip()
        if seller and seller.lower() != 'now':
            return seller
        seller = response.css('div.seller-info span.name::text').get(default='').strip()
        if seller and seller.lower() != 'now':
            return seller
        # Regex in page text, but avoid 'Contact Seller Now!'
        m = re.search(r'Seller[:\s]+([A-Za-z ]+)', response.text)
        if m:
            possible = m.group(1).strip()
            if possible.lower() != 'now':
                return possible
        # Try to extract from description (look for phone/email or names)
        m = re.search(r'(\b[\w.-]+@[\w.-]+\.[A-Za-z]{2,6}\b)', desc)
        if m:
            return m.group(1)
        m = re.search(r'(\+92[0-9\- ]{10,}|03[0-9]{9})', desc)
        if m:
            return m.group(1)
        m = re.search(r'(Owner|Dealer|Contact)[:\s]+([A-Za-z ]+)', desc)
        if m:
            return m.group(2).strip()
        return ''

    def parse_detail(self, response):
        item = PakwheelsItem()
        # Title/Name
        item['name'] = response.css('h1::text').get(default='').strip()
        # If brand/model missing later, try to split title early
        if item['name']:
            # e.g., "Toyota Corolla 2017 ..."
            parts = item['name'].split()
            if len(parts) >= 2 and not item.get('brand'):
                item['brand'] = parts[0]
            if len(parts) >= 3 and not item.get('model'):
                # join middle tokens until a 4-digit year appears
                year_idx = next((i for i, p in enumerate(parts) if re.fullmatch(r'\d{4}', p)), None)
                if year_idx and year_idx > 1:
                    item['model'] = ' '.join(parts[1:year_idx])
                else:
                    item['model'] = parts[1]
        # Price
        price_text = response.css('div.price-section span.price::text').get(default='').strip()
        item['price'] = re.sub(r'[^0-9.]', '', price_text.replace(',', ''))
        # If price is a 4-digit year, treat as invalid
        if re.fullmatch(r'20\d{2}|19\d{2}', item['price']):
            item['price'] = ''
        item['priceCurrency'] = 'PKR' if 'PKR' in price_text or 'lacs' in price_text else ''
        # Fallback: Try to extract price from description if missing or if price is empty
        if not item['price']:
            desc = response.css('div.comment p::text').get(default='').strip()
            if not desc:
                desc = response.css('meta[name="description"]::attr(content)').get(default='').strip()
            # Try to extract 'PKR xx.x lacs' first
            m = re.search(r'PKR\s*([0-9,.]+)\s*lacs?', desc, re.I)
            if m:
                lacs = float(m.group(1).replace(',', ''))
                item['price'] = str(int(lacs * 100000))
                item['priceCurrency'] = 'PKR'
            else:
                m = re.search(r'(PKR|Rs\.?|Rupees|Lacs|Lakh|\u20a8)?\s*([0-9,.]+)', desc, re.I)
                if m:
                    price_val = m.group(2).replace(',', '')
                    item['price'] = price_val
                    if m.group(1):
                        item['priceCurrency'] = 'PKR'
        # Summary bar (year, mileage, engine, fuel, transmission)
        summary = response.css('div.key-details span::text').getall()
        summary = [s.strip() for s in summary if s.strip()]
        # Try to extract year, mileage, engine, fuel, transmission
        for s in summary:
            if re.match(r'^[0-9]{4}$', s):
                item['modelDate'] = s
            elif 'km' in s.lower():
                item['mileageFromOdometer'] = re.sub(r'[^0-9]', '', s)
            elif 'cc' in s.lower():
                item['engineDisplacement'] = re.sub(r'[^0-9]', '', s)
            elif s.lower() in ['automatic', 'manual']:
                item['vehicleTransmission'] = s
            elif s.lower() in ['petrol', 'diesel', 'hybrid', 'cng', 'lpg']:
                item['fuelType'] = s
        # Year fallback from title if missing
        if not item.get('modelDate') and item.get('name'):
            m = re.search(r'(19|20)\d{2}', item['name'])
            if m:
                item['modelDate'] = m.group(0)
        # Car Info Table
        info_rows = response.css('div.car-info table tr')
        for row in info_rows:
            key = row.css('th::text').get(default='').strip().lower()
            value = row.css('td::text').get(default='').strip()
            if not key or not value:
                continue
            if 'brand' in key:
                item['brand'] = value
            elif 'model' in key:
                item['model'] = value
            elif 'color' in key:
                item['color'] = value
            elif 'assembly' in key:
                item['assembly'] = value
            elif 'body type' in key:
                item['bodyType'] = value
            elif 'engine' in key and not item.get('engineDisplacement'):
                item['engineDisplacement'] = re.sub(r'[^0-9]', '', value)
            elif 'registration' in key or 'registered in' in key:
                item['registration_city'] = value
            elif 'mileage' in key and not item.get('mileageFromOdometer'):
                item['mileageFromOdometer'] = re.sub(r'[^0-9]', '', value)
            elif 'transmission' in key and not item.get('vehicleTransmission'):
                item['vehicleTransmission'] = value
            elif 'fuel' in key and not item.get('fuelType'):
                item['fuelType'] = value
        # Description
        item['description'] = response.css('div.comment p::text').get(default='').strip()
        if not item['description']:
            item['description'] = response.css('meta[name="description"]::attr(content)').get(default='').strip()
        desc = item.get('description', '')
        # Seller info (improved extraction)
        item['seller_info'] = self.extract_seller_info(response, desc)
        if not item['seller_info']:
            item['seller_info'] = 'Unknown'
            logger.warning(f"Seller info missing for {response.url}")
        seller_loc = response.css('div.seller-info p.location::text').get(default='').strip()
        if not seller_loc:
            seller_loc = response.css('div.seller-info span.location::text').get(default='').strip()
        if not seller_loc:
            m = re.search(r'Location[:\s]+([A-Za-z ]+)', response.text)
            if m:
                seller_loc = m.group(1).strip()
        # Fallback: extract city from description (e.g., 'Used for sale in Islamabad')
        if not seller_loc:
            m = re.search(r'Used for sale\s+in\s+([A-Za-z .-]+)', desc)
            if m:
                city = m.group(1).strip()
                city = re.split(r'\s+for\b|\s+with\b|\s+at\b|\s+on\b', city)[0].strip()
                seller_loc = city
        item['seller_location'] = seller_loc
        if not item['seller_location']:
            logger.warning(f"Seller location missing for {response.url}")
        # Inspection score
        item['inspection_score'] = response.css('div.carsure-score span.score::text').get(default='').strip()
        # Badges
        badges = response.css('div.badges span::text').getall()
        if badges:
            item['badges'] = ', '.join([b.strip() for b in badges if b.strip()])
        # Images: collect all possible image URLs for ImagesPipeline
        images = response.css('img.ad-image::attr(src), img.ad-image::attr(data-src)').getall()
        if not images:
            # Fallback: any <img> with ad_pictures pattern
            images = response.css('img::attr(src), img::attr(data-src)').re(r'ad_pictures/.+?\.(?:webp|jpg|jpeg|png)')
        # Normalize to absolute URLs
        norm = []
        for u in images:
            if not u:
                continue
            u = u.strip()
            # Skip obvious non-image schemes
            if u.startswith('data:') or u.startswith('javascript:'):
                continue
            if u.startswith('//'):
                u = 'https:' + u
            elif u.startswith('/'):
                u = 'https://www.pakwheels.com' + u
            elif u.startswith('ad_pictures') or u.startswith('media/'):
                # Relative path without leading slash
                u = 'https://www.pakwheels.com/' + u
            elif not re.match(r'^https?://', u):
                # Any other scheme-less path, make it absolute just in case
                u = 'https://www.pakwheels.com/' + u.lstrip('/')
            norm.append(u)
        # De-duplicate preserving order
        seen = set()
        image_urls = []
        for u in norm:
            if u not in seen:
                seen.add(u)
                image_urls.append(u)
        item['image_urls'] = image_urls
        # Let ImagesPipeline populate item['image'] with the first downloaded path
        item['image'] = ''
        # Fallbacks from description if still missing
        if desc:
            # Price fallback: handle 'PKR 34.5 lacs' and similar
            if not item.get('price') or float(item.get('price', '0')) < 1000:
                m = re.search(r'PKR\s*([0-9,.]+)\s*lacs?', desc, re.I)
                if m:
                    lacs = float(m.group(1).replace(',', ''))
                    item['price'] = str(int(lacs * 100000))
                    item['priceCurrency'] = 'PKR'
                else:
                    m = re.search(r'PKR\s*([0-9,.]+)', desc, re.I)
                    if m:
                        item['price'] = m.group(1).replace(',', '')
                        item['priceCurrency'] = 'PKR'
            if not item.get('engineDisplacement'):
                m = re.search(r'(\d{3,4})\s*cc', desc)
                if m:
                    item['engineDisplacement'] = m.group(1)
            if not item.get('mileageFromOdometer'):
                m = re.search(r'([\d,]+)\s*KM', desc)
                if m:
                    item['mileageFromOdometer'] = m.group(1).replace(',', '')
            if not item.get('color'):
                m = re.search(r'(Black|White|Silver|Blue|Red|Grey|Gray|Green|Yellow|Gold|Brown)', desc, re.I)
                if m:
                    item['color'] = m.group(1)
            if not item.get('fuelType'):
                if re.search(r'\bhybrid\b', desc, re.I):
                    item['fuelType'] = 'Hybrid'
                elif re.search(r'\bdiesel\b', desc, re.I):
                    item['fuelType'] = 'Diesel'
                elif re.search(r'\bcng\b', desc, re.I):
                    item['fuelType'] = 'CNG'
                elif re.search(r'\blpg\b', desc, re.I):
                    item['fuelType'] = 'LPG'
                elif re.search(r'\bpetrol\b', desc, re.I):
                    item['fuelType'] = 'Petrol'
            if not item.get('vehicleTransmission'):
                if re.search(r'\bautomatic\b', desc, re.I):
                    item['vehicleTransmission'] = 'Automatic'
                elif re.search(r'\bmanual\b', desc, re.I):
                    item['vehicleTransmission'] = 'Manual'
        # URL
        item['url'] = response.url

        # Basic validation & normalization
        def to_int(s, default=None):
            try:
                return int(str(s).replace(',', '').strip())
            except Exception:
                return default

        price_val = to_int(item.get('price'))
        if price_val is not None and price_val < 10000:
            # likely invalid price
            item['price'] = ''

        # Drop items missing critical identifiers
        if not item.get('name') or not item.get('url'):
            logger.warning(f"Dropping item due to missing name/url: {response.url}")
            return

        # Emit item
        logger.debug(f'DEBUG ITEM: {dict(item)}')
        yield item
