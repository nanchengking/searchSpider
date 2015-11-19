# -*- coding: utf-8 -*-
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import logging
from django.utils.datetime_safe import strftime
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
            logging.info("insert into db")
            if isinstance(item,SearchspiderItem):
                self.cur.execute("""INSERT INTO web_searchspider_results(
                 platform,keyword,resultUrl,
                 targetUrl,targetTitle,createDate,
                 processDate,project_id,searchTask_id,
                 checkStatus,status,program
                 )
                  VALUES(
                  %s,%s,%s,
                  %s,%s,NOW(),
                  %s,%s,%s,
                  %s,%s,%s)""", (
                    item['platform'], item['keyword'], item['resultUrl'],
                    item['targetUrl'], item['targetTitle'], # strftime(item['createDate'], "%Y-%m-%d %H:%M:%s",
                    item['processDate'], item['project'], item['searchTask'],
                    item['checkStatus'], item['status'],item['program']
                ))
            else:
                self.cur.execute("""INSERT INTO web_searchspider_results(
                 platform,keyword,resultUrl,
                 targetUrl,program,createDate,
                 processDate,project_id,searchTask_id,
                 checkStatus,status,author,album
                 )
                  VALUES(
                  %s,%s,%s,
                  %s,%s,NOW(),
                  %s,%s,%s,
                  %s,%s,%s,%s)""", (
                    item['platform'], item['keyword'], item['resultUrl'],
                    item['targetUrl'], item['program'], # strftime(item['createDate'], "%Y-%m-%d %H:%M:%s",
                    item['processDate'], item['project'], item['searchTask'],
                    item['checkStatus'], item['status'],item['author'],item['album']
                ))
            self.conn.commit()
        except BaseException, e:
            logging.error(u"数据插入出错,%s", e)
            self.conn.rollback()
        return item

    def open_spider(self, spider):
        logging.info(u"==open_spider调用成功 %s ==" % spider.searchTaskId)
        self.conn = MySQLdb.Connect(host=settings.MYSQL_HOST,
                                    port=settings.MYSQL_PORT,
                                    user=settings.MYSQL_USER,
                                    passwd=settings.MYSQL_PASSWD,
                                    db=settings.MYSQL_DB,
                                    charset=settings.MYSQL_CHARSET)
        self.cur = self.conn.cursor()
        if spider is not None and spider.searchTaskId is not None:
            logging.info("Add running spiders counter %s" % spider.searchTaskId)
            self.cur.execute("update web_searchtask set runningSpiders=ifnull(runningSpiders,0) + 1 where id=%s", [spider.searchTaskId])
            self.conn.commit()
        # self.cur.execute("""
        #     CREATE TABLE if not exists web_searchspider_results (
        #     id int(11) PRIMARY KEY AUTO_INCREMENT,
        #     platform varchar(20) references web_platform(name),
        #     keyword varchar(50) NOT NULL,
        #     resultUrl varchar(500) DEFAULT NULL,
        #     targetUrl varchar(500) NOT NULL,
        #     targetTitle varchar(500) DEFAULT NULL,
        #     username varchar(100) DEFAULT NULL,
        #     fetchCode varchar(10) DEFAULT NULL,
        #     createDate datetime NOT NULL,
        #     searchTask_id int(11) references web_searchtask(id),
        #     status int(11) NOT NULL,
        #     processDate datetime DEFAULT NULL,
        #     project_id int(11) references web_project(id),
        #     checkStatus int(11) DEFAULT NULL,
        #     program varchar(50) NULL
        #     )
        # """)
        # self.conn.commit()

    def close_spider(self, spider):
        if spider is not None and spider.searchTaskId is not None:
            logging.info("Reduce running spiders counter %s" % spider.searchTaskId)
            self.cur.execute("update web_searchtask set runningSpiders=ifnull(runningSpiders,0) - 1 where id=%s", [spider.searchTaskId])
        self.conn.commit()
        self.cur.close()
        self.conn.close()
        logging.info(u"==close_spider调用成功==")
