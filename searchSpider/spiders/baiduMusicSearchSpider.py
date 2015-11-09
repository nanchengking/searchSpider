# coding=utf-8
__author__ = 'nancheng'
import sys

reload(sys)
sys.setdefaultencoding('utf-8')
import scrapy
from scrapy import Request
import os
import logging
from searchSpider import settings
from searchSpider.items import *
import datetime
import MySQLdb


class BaiduMusicSearchSpider(scrapy.spiders.Spider):
    name = 'baiduMusicSearch'
    allow_domains = ['baidu.com']

    def start_requests(self):
        return self.requests

    def __init__(self, keyword, name=None, author=None, album=None, limit=4, projectId=-1, searchTaskId=-1, *args,
                 **kwargs):
        """
        爬虫用来在百度音乐搜索页面爬取一系列的关键字
        :param keyword: 关键字，是一个list
        :param targetUrl: 有没有需要直接爬取的链接，暂时不处理
        :param limit: 最多抓取多少页
        :param projectId: 项目id
        :param args:
        :param kwargs:
        :return:
        """
        keywords = []
        self.projectId = projectId
        self.searchTaskId = searchTaskId
        if isinstance(keyword, str):
            keywords = keyword.split(settings.SPLIT_SIGN)
        elif isinstance(keyword, list):
            keywords = keyword
        else:
            self.closed(u'传入keyword参数不合法！无法初始化百度音乐爬虫')
        if not keywords:
            self.closed(u'传入keyword参数不合法！无法初始化百度音乐爬虫')
        if not isinstance(limit, int):
            limit = int(limit)
        if (not name) or (not author):
            self.closed(u'传入name 或 author参数不合法！无法初始化百度音乐爬虫')
        self.name = self.getUnicode(name)
        self.author = self.getUnicode(author)
        self.album = self.getUnicode(album)
        self.isLinux = False
        logging.info(u"keywods is : %s" % keywords)
        logging.info(u"====百度音乐爬虫初始化成功====")
        super(BaiduMusicSearchSpider, self).__init__(*args, **kwargs)
        self.songsURLS = set()
        self.startTime = datetime.datetime.now()
        self.num = 0
        self.limit = limit
        self.keywordsAndPages = {}
        self.baseURL = ['http://music.baidu.com/search?key=', '']
        self.requests = map(self.initStartRequests, keywords)

    def initStartRequests(self, keyword):
        """
        初始化起始request
        :param keyword:
        :return:
        """
        keyword = self.getUnicode(keyword)
        url = self.baseURL
        url[1] = keyword
        request = Request(url=''.join(url))
        request.meta['keyword'] = keyword
        request.meta['url'] = ''.join(url)
        self.keywordsAndPages[keyword] = 0  # 每一个关键字开始爬取的都是第一页
        return request

    def parse(self, response):
        self.num += 1
        if response.status == 200:
            results = response.css("div.song-item")
            for result in results:
                item = MusicSearchspiderItem()
                item['platform'] = u"百度音乐"
                item['keyword'] = response.meta['keyword']
                item['resultUrl'] = response.meta['url']
                item['targetUrl'] = u"http://music.baidu.com" + self.getUnicode(
                    ''.join(result.xpath("./span[@class='song-title']/a[@data-songdata]/@href").extract())).strip()
                item['targetTitle'] = self.getUnicode(
                    ''.join(result.xpath("./span[@class='song-title']//text()").extract())).strip()
                item['album'] = self.getUnicode(
                    ''.join(result.xpath("./span[@class='album-title']//text()").extract())).strip()
                item['author'] = self.getUnicode(
                    ''.join(result.xpath("./span[@class='singer']//text()").extract())).strip()
                item['createDate'] = datetime.datetime.now()
                item['status'] = 0
                item['processDate'] = datetime.datetime.now()
                item['checkStatus'] = 0
                item['searchTask'] = None if self.searchTaskId == -1 else self.searchTaskId
                item['project'] = None if self.projectId == -1 else self.projectId
                if not item['targetUrl'] in self.songsURLS:  # 去重操作
                    if self.filters(targetTitle=item['targetTitle'], author=item['album']):  # 过滤操作
                        self.songsURLS.add(item['targetUrl'])
                        yield item

            if response.xpath("//div[@class='page-inner']/a[@class='page-navigator-next']/@href"):
                keyword = response.meta['keyword']
                self.keywordsAndPages[keyword] += 1
                pageNum = self.keywordsAndPages[keyword]
                nextURL = u"http://music.baidu.com" + self.getUnicode(''.join(response.xpath(
                    "//div[@class='page-inner']/a[@class='page-navigator-next']/@href").extract())).strip()
                if pageNum < (self.limit):
                    logging.info(u"==现在爬取的关键字是: %s", keyword)
                    logging.info(u"==现在爬取的关键字的page num是: %s", pageNum)
                    request = Request(url=nextURL)
                    request.meta['keyword'] = keyword
                    request.meta['url'] = nextURL
                    yield request
        else:
            logging.info(response.status)

    def filters(self, targetTitle=None, author=None, album=None):
        """
        过滤操作
        :param targetTitle:
        :param author:
        :param album:关于专辑，暂时不用管
        :return:
        """
        if (self.name in targetTitle and self.author in author) or (
                self.name in targetTitle and self.author in targetTitle):
            return True
        else:
            return False

    def getUnicode(self, keyword):
        """
        解决编码问题，可能出现问题的字符都调用一次这个方法
        :param keyword:
        :return:
        """

        if isinstance(keyword, str):
            try:
                if self.isLinux:
                    keyword = keyword.decode('utf-8')
                else:
                    keyword = keyword.decode('gbk')
            except BaseException, e:
                if self.isLinux:
                    self.isLinux = False
                    keyword = keyword.decode('gbk')
                else:
                    self.isLinux = True
                    keyword = keyword.decode('utf-8')
                logging.error(u'出现编码问题')
                logging.error(keyword)
            finally:
                return keyword
        return keyword

    def closed(self, reason):
        if reason:
            logging.warning(u"百度音乐爬虫运行结束： %s" % reason)
        logging.info(u"现在有多少songsURLS(抓取到了多少首歌)： %s" % len(self.songsURLS))
        logging.info(u'现在解析了多少页面： %s' % self.num)
        logging.info(u'limit是： %s' % self.limit)
        logging.info(u'baiduMusicSearchSpider 爬了这么长时间： %s' % (datetime.datetime.now() - self.startTime))