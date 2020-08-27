import os
import sys
import scrapy
import json
from scrapy.utils.log import configure_logging, logging
from scrapy.utils.project import get_project_settings
from scrapy import crawler
import dlsitebackup
from twisted.internet import reactor, defer
import argparse
from datetime import datetime

LIST_JSON_FILENAME = 'rjs.json'

parser = argparse.ArgumentParser()
parser.add_argument('-d', type=str, default=os.path.curdir)
parser.add_argument('--sync', type=bool, default=False ==
                    os.path.exists(LIST_JSON_FILENAME))
args = parser.parse_args()
if args.d and not (os.path.exists(args.d) and os.path.isdir(args.d)):
    print('%s doesn\'t exist' % args.d, file=sys.stderr)
    exit(1)

rjitems = []


class RJPipeline(object):
    name = 'rjpipeline'

    def process_item(self, item, spider):
        if 'filename' in item:
            logging.info('found %s' % item['url'])
            abspath = os.path.join(args.d, item['filename'])
            if os.path.exists(abspath):
                logging.info(
                    '%s exists already, this item was skipped' % abspath)
            else:
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
    'dlsitebackup.pipelines.DLFilesPipeline': 700
})
dl_settings.set('CONCURRENT_ITEMS', 1)
dl_settings.set('CONCURRENT_REQUESTS', 1)
dl_runner = crawler.CrawlerRunner(dl_settings)

logging.basicConfig(
    filename='backup.log',
    format='%(levelname)s: %(message)s',
    level=logging.INFO
)

@defer.inlineCallbacks
def crawl(rjitems):
    if args.sync:
        yield list_runner.crawl(dlsitebackup.spiders.rj.RJSpider)
        list_json = open(LIST_JSON_FILENAME, 'w')
        json.dump(rjitems, list_json, indent=1)
        list_json.close()
    else:
        list_json = open(LIST_JSON_FILENAME, 'r')
        rjitems = json.load(list_json)
        list_json.close()
    yield dl_runner.crawl(dlsitebackup.spiders.rj.DLSpider, rjitems=rjitems, dir=args.d)
    reactor.stop()


crawl(rjitems)
reactor.run()
