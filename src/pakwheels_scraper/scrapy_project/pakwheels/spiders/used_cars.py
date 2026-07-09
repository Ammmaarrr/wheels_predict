import scrapy
from pakwheels.items import PakwheelsItem
import json
import re
from utils.logger import setup_logger, log_error

logger = setup_logger(__name__)

class UsedCarsSpider(scrapy.Spider):
    name = 'used_cars'
    allowed_domains = ['pakwheels.com']

    def __init__(self, start_page=1, end_page=1, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_page = int(start_page)
        self.end_page = int(end_page)

    def start_requests(self):
        try:
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
                    yield scrapy.Request(detail_url, callback=self.parse_detail, errback=self.handle_error)

            # ✅ Pagination handling
            next_page = response.css('ul.pagination li a[rel="next"]::attr(href)').get()
            if next_page:
                if next_page.startswith('/'):
                    next_page = 'https://www.pakwheels.com' + next_page
                yield scrapy.Request(next_page, callback=self.parse, errback=self.handle_error)
            else:
                logger.info("🚀 No more pages to crawl. Spider finished.")
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
        # Images
        images = response.css('img.ad-image::attr(src)').getall()
        if not images:
            images = response.css('img::attr(src)').re(r'ad_pictures/.+?\.webp')
        item['image'] = images[0] if images else ''
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
        # URL
        item['url'] = response.url
        # Debug print
        logger.debug(f'DEBUG ITEM: {dict(item)}')
        yield item
