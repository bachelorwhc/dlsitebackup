import os
import sys
import scrapy
from scrapy.utils.log import configure_logging, logging
from scrapy.utils.project import get_project_settings
from scrapy import crawler
import dlsitebackup
from twisted.internet import reactor, defer
import argparse
from datetime import datetime

parser = argparse.ArgumentParser()
parser.add_argument('-d', type=str)
args = parser.parse_args()
if args.d and not (os.path.exists(args.d) and os.path.isdir(args.d)):
    print('%s doesn\'t exist' % args.d, file=sys.stderr)
    exit(1)
elif args.d is None:
    args.d = os.path.curdir

rjitems = []


class RJPipeline(object):
    name = 'rjpipeline'

    def process_item(self, item, spider):
        if 'filename' in item:
            logging.info('found %s' % item['url'])
            rjitems.append(item)
        return item


list_settings = get_project_settings()
list_settings.set('ITEM_PIPELINES', {
    '__main__.RJPipeline': 100,
})
list_runner = crawler.CrawlerRunner(list_settings)
dl_settings = get_project_settings()
dl_settings.set('FILES_STORE', args.d)
dl_settings.set('ITEM_PIPELINES', {
    'scrapy.pipelines.files.FilesPipeline': None,
    'dlsitebackup.pipelines.DLFilesPipeline': 100
})
dl_settings.set('CONCURRENT_ITEMS', 1)
dl_settings.set('CONCURRENT_REQUESTS', 1)
dl_runner = crawler.CrawlerRunner(dl_settings)

logfilename = datetime.now().strftime('%Y%m%d_%H%M%S') + '.log'
logging.basicConfig(
    filename=logfilename,
    format='%(levelname)s: %(message)s',
    level=logging.INFO
)

@defer.inlineCallbacks
def crawl():
    yield list_runner.crawl(dlsitebackup.spiders.rj.RJSpider)
    yield dl_runner.crawl(dlsitebackup.spiders.rj.DLSpider, rjitems=rjitems)
    reactor.stop()

crawl()
reactor.run()
