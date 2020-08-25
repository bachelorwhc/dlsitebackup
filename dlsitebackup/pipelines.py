# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import os
from itemadapter import ItemAdapter
from scrapy.pipelines.files import FilesPipeline
from scrapy import Request
import urllib

class DLFilesPipeline(FilesPipeline):
    name='dlfilespipeline'
    def get_media_requests(self, item, info):
        adapter = ItemAdapter(item)
        for file_url in adapter['file_urls']:
            yield Request(file_url, meta=item['meta'])

    def file_path(self, request, response=None, info=None):
        filename = request.meta.get('filename')
        return filename
