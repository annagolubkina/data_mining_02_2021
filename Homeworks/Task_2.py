import requests
import bs4
import pymongo
import datetime as dt
from urllib.parse import urljoin

dict_month = {
    'янв': 1,
    'фев': 2,
    'мар': 3,
    'апр': 4,
    'май': 5,
    'июн': 6,
    'июл': 7,
    'авг': 8,
    'сен': 9,
    'окт': 10,
    'ноя': 11,
    'дек': 12,
}


class MagnitParser:

    def __init__(self, start_url, db_client):
        self.start_url = start_url
        self.db = db_client["gb_data_mining_16_2021"]

    def _get_response(self, url):
        try:
            response = requests.get(url, timeout=40)
            response.raise_for_status()
        except requests.Timeout:
            print('Ошибка Timeout, url:', url)

        except requests.RequestException:
            print('Ошибка скачивания url: ', url)

        except requests.HTTPError as err:
            code = err.response.status_code
            print('Ошибка url , code: {0}'.format(code))

        except requests.TooManyRedirects as e:
            print(f' Ошибка бесконечный список перенаправлений {url} : {e}')
        return response

    def _get_soup(self, url):
        response = self._get_response(url)
        soup = bs4.BeautifulSoup(response.text, 'lxml')
        return soup

    def run(self):
        soup = self._get_soup(self.start_url)
        catalog = soup.find('div', attrs={'class': 'сatalogue__main'})
        for product_a in catalog.find_all('a', recursive=False):  # список ссылок а
            product_data = self._parse(product_a)
            self.save(product_data)
            print(1)

    def _template(self):
        return {
            'url': lambda a: urljoin(self.start_url, a.attrs.get('href')),
            'promo_name': lambda a: a.find('div', attrs={'class': 'card-sale__header'}).text,
            'product_name': lambda a: a.find('div', attrs={'class': 'card-sale__title'}).text,
            'old_price': lambda a: float(
                '.'.join(itm for itm in a.find('div', attrs={'class': 'label__price_old'}).text.split())),
            'new_price': lambda a: float(
                ".".join(
                    itm for itm in a.find("div", attrs={"class": "label__price_new"}).text.split()
                )),
            'image_url': lambda a: urljoin(self.start_url, a.find('img').attrs.get('data-src')),
            'date_from': lambda a: self._convert_date(a.find("div", attrs={"class": "card-sale__date"}).text)[0],
            'date_to': lambda a: self._convert_date(a.find("div", attrs={"class": "card-sale__date"}).text)[1],
        }

    def _convert_date(self, date_string: str):
        date_list = date_string.replace('с ', '', 1).replace('\n', '').split('до')
        result = []
        for date in date_list:
            temp_date = date.split()
            result.append(
                dt.datetime(
                    year=dt.datetime.now().year,
                    day=int(temp_date[0]),
                    month=dict_month[temp_date[1][:3]],
                )
            )
        if result[0] > result[1]:
            result[1] = dt.datetime(year=dt.datetime.now().year + 1,
                                    day=int(temp_date[0]),
                                    month=dict_month[temp_date[1][:3]],
                                    )
        return result

    def _parse(self, product_a: bs4.Tag) -> dict:
        product_data = {}
        for key, funk in self._template().items():
            try:
                product_data[key] = funk(product_a)
            except (ValueError, AttributeError):
                pass
        return product_data

    def save(self, data: dict):
        collection = self.db['magnit']
        collection.insert_one(data)


if __name__ == '__main__':
    url = 'https://magnit.ru/promo/?geo=moskva'
    db_client = pymongo.MongoClient('mongodb://localhost:27017')
    parser = MagnitParser(url, db_client)
    parser.run()




