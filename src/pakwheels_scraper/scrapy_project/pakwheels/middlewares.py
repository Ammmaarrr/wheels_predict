import random

class ProxyMiddleware:
    def __init__(self):
        self.proxies = [
            'http://123.45.67.89:8080',
            'http://98.76.54.32:3128',
            'http://username:password@proxy-server.com:8000',  # if your proxies require auth
        ]

    def process_request(self, request, spider):
        proxy = random.choice(self.proxies)
        request.meta['proxy'] = proxy
