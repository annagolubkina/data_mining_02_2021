import scrapy
import json
import datetime as dt
from gb_parse.items import InstaUser
from gb_parse.items import InstaTag, InstaPost

class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['www.instagram.com']
    start_urls = ['https://www.instagram.com/']
    _login_url = 'https://www.instagram.com/accounts/login/ajax/'
    _tags_path = '/explore/tags/'
    api_url = '/graphql/query/'
    query_hash = {
        # 'tags': "9b498c08113f1e09617a1703c22b2f32",
        'edge_followed_by': 'c76146de99bb02f6415203be841dd25a',
        'edge_follow': 'd04b0a864b4b54837c0d870b0e77e076'
    }

    def __init__(self, login, password, start_users: list, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_users = [f'/{user}/' for user in start_users]
        # self.tags = tags
        self.login = login
        self.password = password

    @staticmethod
    def js_data_extract(response):
        script = response.xpath('//script[contains(text(), "window._sharedData")]/text()').extract_first()
        return json.loads(script.replace("window._sharedData = ", "")[:-1])


    def get_url(self, user_id, after='', flw='edge_followed_by'):
        variables = {"id": user_id,
                     "include_reel": True,
                     "fetch_mutual": False,  # Показывать общих фолловеров
                     "first": 100,
                     "after": after}
        return f'{self.api_url}?query_hash={self.query_hash[flw]}&variables={json.dumps(variables)}'

    def parse(self, response, **kwargs):
        try:
            js_data = self.js_data_extract(response)
            yield scrapy.FormRequest(
                self._login_url,
                method='POST',
                callback=self.parse,
                formdata={
                    'username': self.login,
                    'enc_password': self.password
                },
                headers={
                    'X-CSRFToken': js_data['config']['csrf_token']
                }
            )
        except AttributeError as e:
            print(e)
            if response.json()['authenticated']:
                for user in self.start_users:
                    yield response.follow(user, callback=self.user_parse)
                # for tag in self.tags:
                #     yield response.follow(f"{self._tags_path}{tag}/",callback=self.tag_page_parse)

    def user_parse(self, response):
        js_data = self.js_data_extract(response)
        user_id = js_data['entry_data']['ProfilePage'][0]['graphql']['user']['id']
        user_name = js_data['entry_data']['ProfilePage'][0]['graphql']['user']['username']
        for flw in self.query_hash.keys():
            yield response.follow(self.get_url(user_id, flw=flw), callback=self.follow_parse,
                                  meta={'user_id': user_id, 'user_name': user_name, 'follow': flw})

    def follow_parse(self, response):
        json_data = response.json()
        end_cursor = json_data['data']['user'][response.meta['follow']]['page_info']['end_cursor']
        if json_data['data']['user'][response.meta['follow']]['page_info']['has_next_page']:
            yield response.follow(
                self.get_url(user_id=response.meta['user_id'], after=end_cursor, flw=response.meta['follow']),
                callback=self.follow_parse, meta=response.meta)
        for edge in json_data['data']['user'][response.meta['follow']]['edges']:
            yield InstaUser(date_parse=dt.datetime.utcnow(),
                                data={
                                    'root_user': response.meta['user_name'],
                                    'root_user_id': response.meta['user_id'],
                                    'follow_status': response.meta['follow'],
                                    'node_data': edge['node']
                                },
                                image=edge['node']['profile_pic_url'])

    # def tag_page_parse(self, response):
    #     tag = self.js_data_extract(response)['entry_data']['TagPage'][0]['graphql']['hashtag']
    #     yield InstaTag(
    #         date_parse=dt.datetime.utcnow(),
    #         data={
    #             "id": tag["id"],
    #             "name": tag["name"],
    #             "profile_pic_url": tag["profile_pic_url"],
    #         }
    #     )
    #     yield from self.get_tag_posts(tag, response)
    #
    # def _api_tag_parse(self, response):
    #     yield from self.get_tag_posts(response.json()['data']['hashtag'], response)
    #
    # def get_tag_posts(self, tag, response):
    #     if tag['edge_hashtag_to_media']['page_info']['has_next_page']:
    #         variables = {
    #             'tag_name': tag['name'],
    #             'first': 100,
    #             'after': tag['edge_hashtag_to_media']['page_info']['end_cursor'],
    #         }
    #         url = f'{self.api_url}?query_hash={self.query_hash}&variables={json.dumps(variables)}'
    #         yield response.follow(
    #             url,
    #             callback=self._api_tag_parse,
    #         )
    #
    #     yield from self.get_post_item(tag['edge_hashtag_to_media']['edges'])
    #
    # @staticmethod
    # def get_post_item(edges):
    #     for node in edges:
    #         yield InstaPost(
    #             date_parse=dt.datetime.utcnow(),
    #             data=node['node']
    #         )