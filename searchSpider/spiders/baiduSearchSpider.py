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

    def __init__(self, keyword, filters='',targetUrl=None, limit=4, projectId=-1, *args, **kwargs):
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
            logging.error(u'传入keyword参数不合法！无法初始化百度爬虫')
            self.closed(u'传入keyword参数不合法！无法初始化百度爬虫')
        if not keywords:
            logging.error(u'传入keyword参数不合法！无法初始化百度爬虫')
            self.closed(u'传入keyword参数不合法！无法初始化百度爬虫')
        if not isinstance(limit, int):
            limit = int(limit)
        if isinstance(filters,str):
            self.filters= keyword.split(' ')
        else:
            logging.error(u'传入filters参数不合法，必须为str！无法初始化百度爬虫')
            self.closed(u'传入filters参数不合法，必须为str！无法初始化百度爬虫')
        if len(self.filters)<1:
            logging.error(u'传入filters参数为空！无法初始化百度爬虫')
            self.closed(u'传入filters参数为空！无法初始化百度爬虫')
        logging.info(u"keywods is : %s"%keywords)
        super(BaiduSearchSpider, self).__init__(*args, **kwargs)
        self.realURLs=set()
        self.faceURLs=set()
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
                if self.filter(targetTitle=item['targetTitle']):
                    logging.info(u"===开始检测url===")
                    if not item['targetUrl'] in self.faceURLs:#去重操作
                        self.faceURLs.add(item['targetUrl'])
                        yield self.checkURLis200(url=item['targetUrl'],item=item)
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

    def checkURLis200(self,url,item):
        """
        名字起的不太好，这儿其实是一个调用getRealURL的中转站而已。
        :param url:
        :param item:
        :return:
        """

        request=Request(url=url,callback=self.getRealURL)
        request.meta['item']=item
        logging.info(u"===发出一个请求真是url的请求===")
        return request

    def getRealURL(self,response):
        """
        得到真实的（重定向之后的）url
        当然，这儿还有一步去重的操作，把真实url相同的去除
        :param response:
        :return:
        """
        logging.info(u"======调用getRealURL======")
        logging.info(response)
        if response.status==200:
            item=response.meta['item']
            item['resultUrl']=response.url
            if not response.url in self.realURLs:
                self.realURLs.add(response.url)
                return item


    def filter(self,targetTitle):
        """
         使用简单的关键词过滤，如果存在关键字，就返回True，否则，返回false
        :param targetTitle: 需要顾虑的部分，这儿选用标题
        :return:
        """
        count=0
        for filter in self.filters:
            if self.getUnicode(filter) in self.getUnicode(targetTitle):
                logging.info(u'===filter===')
                count+=1#考虑可能需要分级，命中关键字多的，嫌疑也比较大，这儿暂时不加处理
                logging.info(str(count))
        if count>=1:
            return True
        else:
            return False


    def closed(self, reason):
        if reason:
            logging.warning(reason)
        logging.info(u'现在解析了多少页面： %s' % self.num)
        logging.info(u'limit是： %s' % self.limit)
        logging.info(u'baiduSearchSpider 爬了这么长时间： %s' % (datetime.datetime.now() - self.startTime))
