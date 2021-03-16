import os
import dotenv
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from gb_parse.spiders.autoyoula import AutoyoulaSpider
from gb_parse.spiders.hhru import HHruSpider
from gb_parse.spiders.instagram import InstagramSpider



if __name__ == "__main__":
    dotenv.load_dotenv('.env')
    # tags = ['python','java', 'programm']
    user_list = ['katrinbuka', 'merilipsman','brezhneva_alena']
    crawler_settings = Settings()
    crawler_settings.setmodule("gb_parse.settings")
    crawler_proc = CrawlerProcess(settings=crawler_settings)
    # crawler_proc.crawl(AutoyoulaSpider)
    #crawler_proc.crawl(HHruSpider)
    crawler_proc.crawl(InstagramSpider,
                       login=os.getenv('INST_LOGIN'),
                       password=os.getenv('INST_PASSWORD'),
                       # tags=tags
                       start_users=user_list
                       )
    crawler_proc.start()
