from scrapy import Selector
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, MapCompose
from gb_parse.items import GbAutoyoulaItem
from gb_parse.items import GBHHItem
from gb_parse.items import GBHHCompanyItem
import re


def get_characteristics(item) -> dict:  #прилетает одна строка
    selector = Selector(text=item)
    return {
        'name': selector.xpath("//div[contains(@class, 'AdvertSpecs_label')]/text()").extract_first(),
        'value': selector.xpath("//div[contains(@class, 'AdvertSpecs_data')]//text()").extract_first()
    }


def get_auhtor(json_string):
    re_str = re.compile(r"youlaId%22%2C%22([0-9|a-zA-Z]+)%22%2C%22avatar")
    result = re.findall(re_str, json_string)
    return f'https://youla.ru/user/{result[0]}' if result else None


class AutoyoulaLoader(ItemLoader):
    default_item_class = GbAutoyoulaItem
    characteristics_in = MapCompose(get_characteristics)
    author_in = MapCompose(get_auhtor)


class HHLoader(ItemLoader):
    default_item_class = GBHHItem
    title_out = TakeFirst()
    url_out = TakeFirst()
    description_in = "".join
    description_out = TakeFirst()
    salary_in = "".join
    salary_out = TakeFirst()
    company_url_out = TakeFirst()


class HHCompanyLoader(ItemLoader):
    default_item_class = GBHHCompanyItem
    name_out = TakeFirst()
    company_site_out = TakeFirst()
    company_activities_out = TakeFirst()
    company_description_out = TakeFirst()
    company_vacancies_out = TakeFirst()





