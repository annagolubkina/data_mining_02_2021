import scrapy
import json
import datetime as dt
from gb_parse.items import InstaTag, InstaPost



class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['www.instagram.com']
    start_urls = ['https://www.instagram.com/']
    _login_url = 'https://www.instagram.com/accounts/login/ajax/'
    _tags_path = '/explore/tags/'
    api_url = '/graphql/query/'

    query_hash = "9b498c08113f1e09617a1703c22b2f32"

    def __init__(self,login, password, tags, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.login = login
        self.password = password
        self.tags = tags
        print(1)

    def parse(self, response):
        try:
            js_data = self.js_data_extract(response)
            yield scrapy.FormRequest(
                self._login_url,
                method='POST',
                callback=self.parse,
                formdata={
                    "username": self.login,
                    "enc_password": self.password
                },
                headers={"X-CSRFToken": js_data["config"]["csrf_token"]}
            )
        except AttributeError as e:
            print(e)
            if response.json()['authenticated']:
                for tag in self.tags:
                    yield response.follow(f"{self._tags_path}{tag}/",callback=self.tag_page_parse)


    def tag_page_parse(self, response):
        tag = self.js_data_extract(response)['entry_data']['TagPage'][0]['graphql']['hashtag']
        yield InstaTag(
            date_parse=dt.datetime.utcnow(),
            data={
                "id": tag["id"],
                "name": tag["name"],
                "profile_pic_url": tag["profile_pic_url"],
            }
        )
        yield from self.get_tag_posts(tag, response)

    def _api_tag_parse(self, response):
        yield from self.get_tag_posts(response.json()['data']['hashtag'], response)

    def get_tag_posts(self, tag, response):
        if tag['edge_hashtag_to_media']['page_info']['has_next_page']:
            variables = {
                'tag_name': tag['name'],
                'first': 100,
                'after': tag['edge_hashtag_to_media']['page_info']['end_cursor'],
            }
            url = f'{self.api_url}?query_hash={self.query_hash}&variables={json.dumps(variables)}'
            yield response.follow(
                url,
                callback=self._api_tag_parse,
            )

        yield from self.get_post_item(tag['edge_hashtag_to_media']['edges'])

    @staticmethod
    def get_post_item(edges):
        for node in edges:
            yield InstaPost(
                date_parse=dt.datetime.utcnow(),
                data=node['node']
            )

    def js_data_extract(self, response):
        script = response.xpath('//script[contains(text(), "window._sharedData")]/text()').extract_first()
        return json.loads(script.replace("window._sharedData = ", "")[:-1])
