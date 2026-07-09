import os
import re
from urllib.parse import urlparse, urljoin
from scrapy.pipelines.images import ImagesPipeline
from scrapy import Request


class PakwheelsImagesPipeline(ImagesPipeline):
    """Extend ImagesPipeline to:
    - read image URLs from item['image_urls'] (populated by spider)
    - store local paths in item['image_paths']
    - set item['image'] to the first downloaded path if empty
    """

    def get_media_requests(self, item, info):
        base = 'https://www.pakwheels.com/'
        urls = item.get('image_urls') or []
        seen = set()
        for raw in urls:
            if not raw:
                continue
            u = str(raw).strip()
            # Remove embedded whitespace/newlines mid-URL (seen in some lazy-loaded attrs)
            u = re.sub(r"\s+", "", u)
            # Skip data URIs or JS placeholders
            if u.startswith('data:') or u.startswith('javascript:'):
                continue
            # Build absolute URL safely
            if u.startswith('//'):
                u = 'https:' + u
            else:
                u = urljoin(base, u)
            # Validate scheme
            parsed = urlparse(u)
            if parsed.scheme not in ('http', 'https'):
                continue
            if u in seen:
                continue
            seen.add(u)
            yield Request(u)

    def file_path(self, request, response=None, info=None, *, item=None):
        # Build a stable folder/name based on URL path
        parsed = urlparse(request.url)
        # Use last two path components when possible
        parts = [p for p in parsed.path.split('/') if p]
        if len(parts) >= 2:
            subdir = os.path.join(parts[-2], parts[-1])
        else:
            subdir = parts[-1] if parts else 'image'
        return subdir

    def item_completed(self, results, item, info):
        """results: list of (success, info) from ImagesPipeline.
        Attach 'image_paths' and set 'image' if missing.
        """
        image_paths = [x['path'] for ok, x in results if ok and 'path' in x]
        item['images'] = [x for ok, x in results if ok]
        item['image_paths'] = image_paths
        if not item.get('image') and image_paths:
            item['image'] = image_paths[0]
        return item
