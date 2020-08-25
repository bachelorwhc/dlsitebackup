import scrapy
import logging
import urllib


class RJSpider(scrapy.Spider):
    handle_httpstatus_list = [302]
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
                meta = self.meta.copy()
                meta['filename'] = last + '.zip'
                logging.info(url)
                yield scrapy.Request(
                    url,
                    callback=self.get_redirect_url,
                    meta=meta
                )

    def get_split_list(self, response):
        rows = response.xpath(
            '//table[@class="work_list_main"]//tr[not(@class)]')
        for row in rows:
            meta = self.meta.copy()
            url = row.xpath('td[@class="work_dl"]//a/@href').get()
            logging.info(url)
            meta['filename'] = row.xpath(
                'td[@class="work_content"]//p//strong/text()').get()
            yield scrapy.Request(
                url,
                callback=self.get_redirect_url,
                meta=meta
            )

    def get_redirect_url(self, response):
        url = str(response.headers['Location'], encoding='utf-8')
        yield {'file_urls': [url], 'meta': response.meta}
