# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
import browser_cookie3

from itemadapter import is_item, ItemAdapter
from scrapy.downloadermiddlewares.cookies import CookiesMiddleware

class DlsitebackupDownloaderMiddleware(CookiesMiddleware):
    def __init__(self, debug=False):
        super().__init__(debug)
        jar = self.jars['chrome']
        chrome_cookies = browser_cookie3.chrome()
        for cookie in chrome_cookies:
            jar.set_cookie(cookie)
