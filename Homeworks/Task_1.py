import json
import requests
import time
from pathlib import Path


class Parser5ka:
    _params = {'records_per_page': 50, }
    _headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:81.0) Gecko/20100101 Firefox/81.0',}

    def __init__(self, start_url):
        self.start_url = start_url

    @staticmethod
    def _get(*args, **kwargs):
        while True:
            try:
                response = requests.get(*args, **kwargs)
                if response.status_code != 200:
                    raise Exception
                time.sleep(0.1)
                return response
            except Exception:
                time.sleep(0.250)

    def parse(self, url):
        params = self._params
        while url:
            response = self._get(url, params=params, headers=self._headers)
            if params:
                params = {}
            data: dict = response.json()
            url = data.get('next')

            yield data.get('results')

    @staticmethod
    def _save(data: dict, file_path):
        jdata = json.dumps(data, ensure_ascii=False)
        file_path.write_text(jdata, encoding="UTF-8")


class ParserCatalog(Parser5ka):

    def __init__(self, start_url, category_url, products_path: Path ):
        self.category_url = category_url
        self.products_path = products_path
        super().__init__(start_url)

    def get_categories(self, url):
        response = requests.get(url, headers=self._headers)
        return response.json()

    def run(self):
        for category in self.get_categories(self.category_url):
            data = {
                "name": category['parent_group_name'],
                'code': category['parent_group_code'],
                "products": [],
            }

            self._params['categories'] = category['parent_group_code']

            for products in self.parse(self.start_url):
                data["products"].extend(products)
                product_path = self.products_path.joinpath(f"{category['parent_group_code']}.json")
                self._save(data, product_path)


if __name__ == "__main__":
    url = "https://5ka.ru/api/v2/special_offers/"
    url_categories = 'https://5ka.ru/api/v2/categories/'
    save_path = Path(__file__).parent.joinpath("products")
    if not save_path.exists():
        save_path.mkdir()

    parser = ParserCatalog(url, url_categories, save_path)
    parser.run()



