import scrapy
import logging
import urllib
import os


class RJSpider(scrapy.Spider):
    name = "rj"
    meta = {'cookiejar': 'chrome'}

    def start_requests(self):
        yield scrapy.Request(
            'https://www.dlsite.com/maniax/mypage/userbuy/=/type/all/start/all/sort/1/order/1/page/1',
            callback=self.get_total_page,
            meta=self.meta
        )

    def get_total_page(self, response):
        page_nos = response.xpath(
            '//td[@class="page_no"]//ul//li//a/@data-value')
        max = 1
        for p in page_nos:
            n = int(p.get())
            max = n if max < n else max
        for p in range(1, max + 1):
            url = 'https://www.dlsite.com/maniax/mypage/userbuy/=/type/all/start/all/sort/1/order/1/page/%d' % p
            yield scrapy.Request(
                url,
                callback=self.get_list,
                meta=self.meta,
                dont_filter=True
            )

    def get_list(self, response):
        dllist = response.xpath('//a[@class="btn_dl"]/@href')
        for l in dllist:
            url = l.get()
            if url.startswith('https://www.dlsite.com/maniax/download/split/=/product_id/'):
                yield scrapy.Request(
                    url,
                    callback=self.get_split_list,
                    meta=self.meta
                )
            else:
                last = urllib.parse.urlparse(
                    url).path.rsplit('/', 1)[-1].split('.')[0]
                yield {
                    'filename': last + '.zip',
                    'url': url
                }

    def get_split_list(self, response):
        rows = response.xpath(
            '//table[@class="work_list_main"]//tr[not(@class)]')
        for row in rows:
            url = row.xpath('td[@class="work_dl"]//a/@href').get()
            filename = row.xpath(
                'td[@class="work_content"]//p//strong/text()').get()
            yield {
                'filename': filename,
                'url': url
            }


class DLSpider(scrapy.Spider):
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36'
    name = "dl"
    meta = {'cookiejar': 'chrome'}
    handle_httpstatus_list = [302]

    def __init__(self, rjitems=None, dir=None):
        self.rjitems = rjitems
        self.dir = dir
        self.curr = 0

    def next_item(self):
        def _next_item():
            if self.curr >= len(self.rjitems):
                return None
            item = self.rjitems[self.curr]
            self.curr += 1
            return item
        def _item_exists(item):
            abspath = os.path.join(self.dir, item['filename'])
            return os.path.exists(abspath)
        item = None
        while True:
            item = _next_item()
            if item is None or not _item_exists(item):
                break
        return item

    def start_requests(self):
        item = self.next_item()
        if item is None:
            return None
        meta = self.meta.copy()
        meta['filename'] = item['filename']
        meta['url'] = item['url']
        yield scrapy.Request(
            item['url'],
            callback=self.get_redirect_url,
            meta=meta
        )

    def get_redirect_url(self, response):
        filename = response.meta['filename']
        logging.info('start to request %s' % filename)
        if 'Location' in response.headers:
            url = str(response.headers['Location'], encoding='utf-8')
            meta = self.meta.copy()
            meta['filename'] = filename
            yield {'file_urls': [url], 'meta': meta}
        else:
            logging.warn('Skip %s because failed to parse headers' % filename)
        for r in self.start_requests():
            yield r
