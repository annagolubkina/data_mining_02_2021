import scrapy
import pymongo
import re


class AutoyoulaSpider(scrapy.Spider):
    name = 'autoyoula'
    allowed_domains = ['auto.youla.ru']
    start_urls = ['https://auto.youla.ru/']

    _css_selectors = {
        'brands': '.TransportMainFilters_brandsList__2tIkv '
        '.ColumnItemList_container__5gTrc '
        'a.blackLink',
        'pagination': 'a.Paginator_button__u1e7D',
        'car': '.SerpSnippet_titleWrapper__38bZM a.SerpSnippet_name__3F7Yu',
    }

    def _get_follow(self, response, select_str, callback, **kwargs):
        for a in response.css(select_str):
            link = a.attrib.get('href')
            yield response.follow(link, callback=callback, cb_kwargs=kwargs)

    def parse(self, response, *args, **kwargs):
        yield from self._get_follow(response,
                                    self._css_selectors['brands'],
                                    callback=self.brand_parse)

    def brand_parse(self, response, *args, **kwargs):
        yield from self._get_follow(response,
                                    self._css_selectors['pagination'],
                                    callback=self.brand_parse)

        yield from self._get_follow(response,
                                    self._css_selectors['car'],
                                    callback=self.car_parse
                                    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db_client = pymongo.MongoClient()

    def car_parse(self, response):
        title = response.css('.AdvertCard_advertTitle__1S1Ak::text').extract_first()
        images = [image.attrib['src'] for image in response.css('figure.PhotoGallery_photo__36e_r img')]
        full_description = response.css('.AdvertCard_descriptionInner__KnuRi::text').extract_first()
        specifications = self.get_specification(response)
        author = self.get_author_url(response)
        self.db_client['gb_parse_autoyoula_02_03'][self.name].insert_one({
            'title': title,
            'images': images,
            'specifications': specifications,
            'full_description': full_description,
            'author': author
        })

    def get_specification(self,response):
        result = {itm.css('.AdvertSpecs_label__2JHnS::text').get():
                      itm.css( '.AdvertSpecs_data__xK2Qx::text').get()  for itm in
                    response.css('.AdvertSpecs_row__ljPcX')}
        return result

    def get_author_url(self, response):
        script = response.xpath('//script[contains(text(), "window.transitState =")]/text()').get()
        re_str = re.compile(r"youlaId%22%2C%22([0-9|a-zA-Z]+)%22%2C%22avatar")
        result = re.findall(re_str, script)
        return f'https://youla.ru/user/{result[0]}' if result else None

