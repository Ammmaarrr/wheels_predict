BOT_NAME = 'pakwheels'
SPIDER_MODULES = ['pakwheels.spiders']
NEWSPIDER_MODULE = 'pakwheels.spiders'

ROBOTSTXT_OBEY = True
DOWNLOAD_DELAY = 0.5
CONCURRENT_REQUESTS = 8

DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'scrapy_user_agents.middlewares.RandomUserAgentMiddleware': 400,
}

ITEM_PIPELINES = {
    # 'pakwheels.async_pipelines.AsyncPostgresPipeline': 300,  # temporarily disabled async pipeline
    'pakwheels.pipelines.PostgresPipeline': 300,  # fallback sync pipeline enabled
}
