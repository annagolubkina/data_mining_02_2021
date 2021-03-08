import scrapy
from gb_parse.loaders import HHLoader
from gb_parse.loaders import HHCompanyLoader


class HHruSpider(scrapy.Spider):
    name = 'hhru'
    allowed_domains = ['hh.ru']
    start_urls = ['https://hh.ru/search/vacancy?schedule=remote&L_profession_id=0&area=113']

    _xpath_selectors = {
        'pagination': '//div[@data-qa="pager-block"]//a[@data-qa="pager-page"]/@href',
        'vacancy_urls': '//a[@data-qa="vacancy-serp__vacancy-title"]/@href',
    }

    _vacancy_xpath = {
        'title': '//h1[@data-qa="vacancy-title"]/text()',
        'salary': '//span[@data-qa="bloko-header-2"]/text()',
        'description': '//div[@data-qa="vacancy-description"]//text()',
        'skills': '//div[@class="bloko-tag-list"]//span[@data-qa="bloko-tag__text"]/text()',
        'company_url':'//div[contains(@class, "vacancy-company-wrapper")]//a[@data-qa="vacancy-company-name"]/@href'
    }

    _company_xpath = {
        'name': '//span[@data-qa="company-header-title-name"]/text()',
        'company_site': '//a[contains(@data-qa, "sidebar-company-site")]/@href',
        'company_activities': '//div[@class="employer-sidebar"]//div[@class="employer-sidebar-block"]//p/text()',
        'company_description': '//div[@class="g-user-content"]/p/text()',
        'company_vacancies': '//div[@class="company-vacancy-indent"]//div[@class="vacancy-list-item"]//a[@data-qa="vacancy-serp__vacancy-title"]/@href'
    }

    def _get_follow(self, response, select_str, callback, **kwargs):
        for a in response.xpath(select_str):
            yield response.follow(a, callback=callback, cb_kwargs=kwargs)

    def parse(self, response, *args, **kwargs):
        yield from self._get_follow(response,
                                    self._xpath_selectors['pagination'],
                                    callback=self.parse)

        yield from self._get_follow(response,
                                    self._xpath_selectors['vacancy_urls'],
                                    callback=self.vacancy_parse)


    def vacancy_parse(self, response, **kwargs):
        loader = HHLoader(response=response)
        loader.add_value('url', response.url)
        for key, value in self._vacancy_xpath.items():
            loader.add_xpath(key, value)
        yield loader.load_item()

        yield response.follow(response.xpath(self._vacancy_xpath['company_url']).get(), callback=self.company_parse)


    def company_parse(self, response, **kwargs):
        loader = HHCompanyLoader(response=response)
        for key, value in self._company_xpath.items():
            loader.add_xpath(key, value)
        yield loader.load_item()

