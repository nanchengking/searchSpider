# coding=utf-8
__author__ = 'nancheng'
import scrapy
from scrapy import Request
import sys

reload(sys)
sys.setdefaultencoding('utf-8')
import os
import logging
from searchSpider import settings
from searchSpider.items import *
import datetime


class BaiduSearchSpider(scrapy.spiders.Spider):
    name = 'baiduSearch'
    allow_domains = ['baidu.com']

    def start_requests(self):
        return self.requests

    def __init__(self, keyword, targetUrl=None, limit=4, projectId=-1, *args, **kwargs):
        """
        爬虫用来在百度搜索页面爬取一系列的关键字
        :param keyword: 关键字，是一个list
        :param targetUrl: 有没有需要直接爬取的链接，暂时不处理
        :param limit: 最多显示多少页
        :param args:
        :param kwargs:
        :return:
        """
        keywords = []
        self.projectId = projectId
        if isinstance(keyword, str):
            keywords = keyword.split(' ')
        elif isinstance(keyword, list):
            keywords = keyword
        else:
            logging.info(u'传入keyword参数不合法！无法初始化百度爬虫')
            return
        if not keywords:
            logging.info(u'传入keyword参数不合法！无法初始化百度爬虫')
            return
        if not isinstance(limit, int):
            limit = int(limit)
        logging.error(keywords)
        super(BaiduSearchSpider, self).__init__(*args, **kwargs)
        self.startTime = datetime.datetime.now()
        self.num = 0
        self.limit = limit
        self.keywordsAndPages = {}
        self.baseURL = ['http://www.baidu.com/s?wd=', '']
        self.requests = map(self.initStartRequests, keywords)

    def initStartRequests(self, keyword):
        """
        初始化起始request
        :param keyword:
        :return:
        """
        keyword = self.getUnicode(keyword)
        # logging.info(u"====调用: "+keyword)
        url = self.baseURL
        url[1] = keyword
        request = Request(url=''.join(url))
        request.meta['keyword'] = keyword
        request.meta['url'] = ''.join(url)
        self.keywordsAndPages[keyword] = 10  # 每一个关键字开始爬取的都是第一页
        return request

    def createNextPageRequest(self, keyword, pn):
        """
        针对每一个关键字，生成一个request，可以增长页面的
        :param keyword: 需要查询的关键字
        :param pn: 0代表第一页，10代表第二页，20代表第三页……
        :return:一个request
        """
        self.keywordsAndPages[keyword] += 10  # 每新建一个requet，都要把这个关键字的页面加一页
        tem = self.baseURL
        tem[1] = keyword
        url = ''.join(tem) + '&pn=' + str(pn)
        request = Request(url=url)
        request.meta['keyword'] = keyword
        request.meta['url'] = url
        return request

    def parse(self, response):
        self.num += 1
        if response.status == 200:
            results = response.xpath("//div[@id='content_left']/div[@class]")
            for result in results:
                item = SearchspiderItem()
                item['platform'] = u"百度搜索"
                item['keyword'] = response.meta['keyword']
                item['resultUrl'] = response.meta['url']
                item['targetUrl'] = result.xpath("h3[@class]/a[@href]/@href").extract()[0]
                item['targetTitle'] =  ''.join(result.xpath("h3[@class]/a[@href]//text()").extract())
                item['createDate'] = datetime.datetime.now()
                item['status'] = 0
                item['processDate'] = datetime.datetime.now()
                item['checkStatus'] = 0
                item['searchTask'] = 0
                item['project'] = self.projectId
                yield item
            keyword = response.meta['keyword']
            pageNum = self.keywordsAndPages[keyword]
            if pageNum < (self.limit * 10):
                yield self.createNextPageRequest(keyword=response.meta['keyword'], pn=pageNum)
        else:
            logging.info(response.status)

    def getUnicode(self, keyword):
        """
        解决编码问题，可能出现问题的字符都调用一次这个方法
        :param keyword:
        :return:
        """
        if isinstance(keyword, str):
            try:
                keyword= keyword.decode('gbk')
            except BaseException,e:
                logging.error(u'出现编码问题')
        return keyword

    def getRealURL(self,response):
        """
        得到真实的（重定向之后的）url
        :param response:
        :return:
        """
        pass

    def closed(self, reason):
        logging.info(u'现在解析了多少页面： %s' % self.num)
        logging.info(u'limit是： %s' % self.limit)
        logging.info(u'spider closed 爬了这么长时间： %s' % (datetime.datetime.now() - self.startTime))
