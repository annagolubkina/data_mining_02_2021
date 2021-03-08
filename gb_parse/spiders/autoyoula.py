import scrapy
from ..loaders import AutoyoulaLoader


class AutoyoulaSpider(scrapy.Spider):
    name = 'autoyoula'
    allowed_domains = ['auto.youla.ru']
    start_urls = ['https://auto.youla.ru/']

    _xpath_selectors = {
        'brands': '//div[@class="TransportMainFilters_brandsList__2tIkv"]//a[@class="blackLink"]/@href',
        'pagination': '//div[contains(@class, "Paginator_block")]//a/@href',
        'car': '//article[contains(@class, "SerpSnippet_snippet")]//a[contains(@class, "SerpSnippet_name")]/@href',
    }
    # _css_selectors = {
    #     'brands': '.TransportMainFilters_brandsList__2tIkv '
    #     '.ColumnItemList_container__5gTrc '
    #     'a.blackLink',
    #     'pagination': 'a.Paginator_button__u1e7D',
    #     'car': '.SerpSnippet_titleWrapper__38bZM a.SerpSnippet_name__3F7Yu',
    # }

    # data_query = {
    #     'title': lambda response: response.css('div.AdvertCard_advertTitle__1S1Ak::text').get(),
    #     'price': lambda response: float(response.css("div.AdvertCard_price__3dDCr::text").get().replace("\u2009", "")),
    #     'images': lambda response: [image.attrib.get('src') for image in response.css('figure.PhotoGallery_photo__36e_r img')],
    #     'full_description': lambda response: response.css('.AdvertCard_descriptionInner__KnuRi::text').extract_first(),
    #     'characteristics': lambda resp: [
    #         {
    #             "name": itm.css(".AdvertSpecs_label__2JHnS::text").extract_first(),
    #             "value": itm.css(".AdvertSpecs_data__xK2Qx::text").extract_first()
    #             or itm.css(".AdvertSpecs_data__xK2Qx a::text").extract_first(),
    #         }
    #         for itm in resp.css("div.AdvertCard_specs__2FEHc .AdvertSpecs_row__ljPcX")
    #     ],
    #     'author': lambda response: AutoyoulaSpider.get_author_url(response),
    # } #сыc#css selectors #

    _car_path = {
         'title': "//div[@data-target='advert']//div[@data-target='advert-title']/text()",
         'price': "//div[@data-target ='advert']//div[@data-target='advert-price']/text()",
         'photos': "//div[@data-target ='advert']//figure[contains(@class,'PhotoGallery_photo')]//img/@src",
         'description': '//div[contains(@class, "AdvertCard_descriptionInner")]//text()',
         'characteristics': "//div[@data-target ='advert']//h3[contains(text(), 'Характеристики')]/../div/div",
         'author': '//script[contains(text(), "window.transitState =")]/text()',
     }

    # def get_author_url(response):
    #     script = response.xpath('//script[contains(text(), "window.transitState =")]/text()').get()
    #     re_str = re.compile(r"youlaId%22%2C%22([0-9|a-zA-Z]+)%22%2C%22avatar")
    #     result = re.findall(re_str, script)
    #     return f'https://youla.ru/user/{result[0]}' if result else None

    # def _get_follow_css(self, response, select_str, callback, **kwargs):
    #     for a in response.css(select_str):
    #         link = a.attrib.get('href')
    #         yield response.follow(link, callback=callback, cb_kwargs=kwargs)
    #
    def _get_follow(self, response, select_str, callback, **kwargs):
        for link in response.xpath(select_str):
            yield response.follow(link, callback=callback, cb_kwargs=kwargs)

    def parse(self, response, *args, **kwargs):
        yield from self._get_follow(response,
                                    self._xpath_selectors['brands'],
                                    callback=self.brand_parse)

    def brand_parse(self, response, *args, **kwargs):
        yield from self._get_follow(response,
                                    self._xpath_selectors['pagination'],
                                    callback=self.brand_parse)

        yield from self._get_follow(response,
                                    self._xpath_selectors['car'],
                                    callback=self.car_parse
                                    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    def car_parse(self, response):
        loader = AutoyoulaLoader(response=response)
        loader.add_value('url', '')
        loader.add_value('url', response.url)
        for key, selector in self._car_path.items():
            loader.add_xpath(key, selector)

        yield loader.load_item()





