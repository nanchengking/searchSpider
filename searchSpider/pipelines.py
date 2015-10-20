# -*- coding: utf-8 -*-
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import logging
from searchSpider import settings
import json
from json import *
import codecs
from searchSpider.items import *
import MySQLdb
import settings


class SearchspiderPipeline(object):
    def process_item(self, item, spider):
        try:
            self.cur.execute("""INSERT INTO web_searchspider_results(
             platform,keyword,resultUrl,
             targetUrl,targetTitle,createDate,
             processDate,project_id,searchTask_id,
             checkStatus,status
             )
              VALUES(
              %s,%s,%s,
              %s,%s,%s,
              %s,%s,%s,
              %s,%s)""", (
                item['platform'], item['keyword'], item['resultUrl'],
                item['targetUrl'], item['targetTitle'], item['createDate'],
                item['processDate'], item['project'], item['searchTask'],
                item['checkStatus'], item['status']
            ))
            self.conn.commit()
        except BaseException, e:
            logging.error(u"数据插入出错")
            self.conn.rollback()
        return item

    def open_spider(self, spider):
        logging.info(u"==open_spider调用成功==")
        self.conn = MySQLdb.Connect(host=settings.MYSQL_HOST,
                                    port=settings.MYSQL_PORT,
                                    user=settings.MYSQL_USER,
                                    passwd=settings.MYSQL_PASSWD,
                                    db=settings.MYSQL_DB,
                                    charset=settings.MYSQL_CHARSET)
        self.cur = self.conn.cursor()
        self.cur.execute("""
            CREATE TABLE if not exists web_searchspider_results (
            id int(11) PRIMARY KEY AUTO_INCREMENT,
            platform varchar(20) references web_platform(name),
            keyword varchar(50) NOT NULL,
            resultUrl varchar(500) DEFAULT NULL,
            targetUrl varchar(500) NOT NULL,
            targetTitle varchar(500) DEFAULT NULL,
            username varchar(100) DEFAULT NULL,
            fetchCode varchar(10) DEFAULT NULL,
            createDate date NOT NULL,
            searchTask_id int(11) references web_searchtask(id),
            status int(11) NOT NULL,
            processDate datetime DEFAULT NULL,
            project_id int(11) references web_project(id),
            checkStatus int(11) DEFAULT NULL
            )
        """)
        self.conn.commit()

    def close_spider(self, spider):
        self.conn.commit()
        self.cur.close()
        self.conn.close()
        logging.info(u"==close_spider调用成功==")
