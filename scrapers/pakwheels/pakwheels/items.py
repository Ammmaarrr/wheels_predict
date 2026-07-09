import scrapy

class PakwheelsItem(scrapy.Item):
    name = scrapy.Field()
    brand = scrapy.Field()
    model = scrapy.Field()
    price = scrapy.Field()
    priceCurrency = scrapy.Field()
    url = scrapy.Field()
    description = scrapy.Field()
    itemCondition = scrapy.Field()
    modelDate = scrapy.Field()
    manufacturer = scrapy.Field()
    fuelType = scrapy.Field()
    image = scrapy.Field()
    # For Scrapy ImagesPipeline
    image_urls = scrapy.Field()  # list of image URLs to download
    images = scrapy.Field()      # results from ImagesPipeline
    image_paths = scrapy.Field() # local paths (derived from images)
    vehicleTransmission = scrapy.Field()
    color = scrapy.Field()
    bodyType = scrapy.Field()
    mileageFromOdometer = scrapy.Field()
    engineDisplacement = scrapy.Field()
    assembly = scrapy.Field()
    registration_city = scrapy.Field()
    seller_info = scrapy.Field()
    seller_location = scrapy.Field()
    inspection_score = scrapy.Field()
    badges = scrapy.Field()
    # legacy/HTML fallback fields
    location = scrapy.Field()
    mileage = scrapy.Field()
    engine = scrapy.Field()
    transmission = scrapy.Field()
    body_type = scrapy.Field()
    fuel_type = scrapy.Field()
