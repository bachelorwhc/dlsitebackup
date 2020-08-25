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

settings = get_project_settings()
settings.set('FILES_STORE', args.d)
runner = crawler.CrawlerRunner(settings)

logfilename = datetime.now().strftime('%Y%m%d_%H%M%S') + '.log'
logging.basicConfig(
    filename=logfilename,
    format='%(levelname)s: %(message)s',
    level=logging.INFO
)


@defer.inlineCallbacks
def crawl():
    yield runner.crawl(dlsitebackup.spiders.rj.RJSpider)
    reactor.stop()


crawl()
reactor.run()
