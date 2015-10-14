# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import logging
from searchSpider import  settings
import json
from json import  *
from searchSpider.items import *
class SearchspiderPipeline(object):
    def process_item(self, item, spider):
        item['createDate']=str(item['createDate'])
        item['processDate']=str(item['processDate'])
        item['keyword']=item['keyword']
        item['targetTitle']=item['targetTitle']
        jsonItem=JSONEncoder().encode(dict(item))
        self.file.write(jsonItem)
        self.file.write('\n')
        self.file.flush()
        return item
    def filter(self):
        """
        这儿加入过滤条件，只抓取符合要求，也就是侵权的item
        :return:
        """
        pass
    def open_spider(self,spider):
        logging.info("==open_spider调用成功==")
        self.file=open("searchSpider.json",'w')
    def close_spider(self,spider):
        self.file.flush()
        self.file.close()
        logging.info("==close_spider调用成功==")
