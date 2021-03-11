# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import TakeFirst

class GbParseItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class GbAutoyoulaItem(scrapy.Item):
    _id = scrapy.Field()
    url = scrapy.Field(output_processor=TakeFirst())
    title = scrapy.Field(output_processor=TakeFirst())
    price = scrapy.Field()
    photos = scrapy.Field()
    characteristics = scrapy.Field()
    description = scrapy.Field(output_processor=TakeFirst())
    author = scrapy.Field(output_processor=TakeFirst())


class GBHHItem(scrapy.Item):
    _id = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    salary = scrapy.Field()
    description = scrapy.Field()
    skills = scrapy.Field()
    company_url = scrapy.Field()


class GBHHCompanyItem(scrapy.Item):
    _id = scrapy.Field()
    name = scrapy.Field()
    company_site = scrapy.Field()
    company_activities = scrapy.Field()
    company_description = scrapy.Field()
    company_vacancies = scrapy.Field()

class Instagram(scrapy.Item):
    _id = scrapy.Field()
    date_parse = scrapy.Field()
    data = scrapy.Field()
    img = scrapy.Field()


class InstaTag(Instagram):
    pass


class InstaPost(Instagram):
    pass


