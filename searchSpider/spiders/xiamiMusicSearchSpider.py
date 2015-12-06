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

class XiamiMusicSearchSpider(scrapy.spiders.Spider):
    name = 'xiamiMusicSearch'
    allow_domains = ['xiami.com']
    # 需要登录操作，暂时不做

    def start_requests(self):
        return self.requests

    def __init__(self, keyword, author=None, album=None, limit=4, projectId=-1, searchTaskId=-1, program='', *args,
                 **kwargs):
        """
        爬虫用来在虾米音乐搜索页面爬取一系列的关键字
        :param keyword: 关键字，是一个list
        :param targetUrl: 有没有需要直接爬取的链接，暂时不处理
        :param limit: 最多抓取多少页
        :param projectId: 项目id
        :param args:
        :param kwargs:
        :return:
        """
        keywords = []
        self.xiami_cookies={"_unsign_token":"903bdb1672935a509a9f0d778222a9f2",
			"bdshare_firstime":"1447407769093",
			"CNZZDATA921634":"cnzz_eid%3D1324777590-1447406045-http%253A%252F%252Fcn.bing.com%252F%26ntime%3D1449319679",
			"user":"84119614%22%E5%8F%AA%E4%BC%9A%E6%B7%98%E7%A7%91%E6%8A%80%22%220%225%22%3Ca+href%3D%27%2Fwebsitehelp%23help9_3%27+%3Edo%3C%2Fa%3E%220%220%220%2251d53a1e85%221449322856",
			"member_auth":"122aG4wZ62FlhfDCH4lhIS0e5eeBGTiGlIoB27EttQUqJNpdZNCow6uZRgpJ0SaSrGHKqydIUZGYmEaKvHh2cxmyHg", 
			"user_from":"1",
			"join_from":"1zufSNtP6D010%2FjCCA", 
			"ahtena_is_show":"false",
			"_xiamitoken":"a42e75f8453ba563cf4cefccd16d26c7",
			"promotion_opened":"1",
			"promotion_opened_toggler":"1",
			"l":"AurqQvOo04S5OpJJpBMQTxKSGlqOdG6h",
			"isg":"2F9F12E938BE16F01EE1D6DF72096BD2",
			"CNZZDATA2629111":"cnzz_eid%3D1999023816-1447403110-http%253A%252F%252Fcn.bing.com%252F%26ntime%3D1449321096"
		}
        self.projectId = projectId
        self.searchTaskId = searchTaskId
        self.program = program
        if isinstance(keyword, str):
            keywords = keyword.split(",")
        elif isinstance(keyword, list):
            keywords = keyword
        else:
            self.closed(u'传入keyword参数不合法！无法初始化虾米音乐爬虫')
        if not keywords:
            self.closed(u'传入keyword参数不合法！无法初始化虾米音乐爬虫')
        if not isinstance(limit, int):
            limit = int(limit)
        if (not program) or (not author):
            self.closed(u'program 或 author参数不合法！无法初始化虾米音乐爬虫')
        logging.info(u"keywods is : %s" % keywords)
        super(XiamiMusicSearchSpider, self).__init__(*args, **kwargs)
        self.isLinux = os.name == 'posix'  # 判断是否时linux系统
        self.songsURLS = set()
        self.startTime = datetime.datetime.now()
        self.num = 0
        self.limit = limit
        self.keywordsAndPages = {}
        self.name = self.getUnicode(program)
        self.author = self.getUnicode(author)
        self.album = self.getUnicode(album)
        self.file1 = open('jsons.json', 'wb')
        logging.info(u"====虾米音乐爬虫初始化成功====")
        self.baseURL = ['http://www.xiami.com/search/song?key=', '']
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
        request = Request(url=''.join(url),cookies=self.xiami_cookies)
        request.meta['keyword'] = keyword
        request.meta['url'] = ''.join(url)
        self.keywordsAndPages[keyword] = 0  # 每一个关键字开始爬取的都是第一页
        return request

    def parse(self, response):
        self.num += 1
        if response.status == 200:
            results = response.css("tbody tr")
            for result in results:
                item = MusicSearchspiderItem()
                item['platform'] = u"虾米音乐"
                item['keyword'] = response.meta['keyword']
                item['resultUrl'] = response.url
                item['targetUrl'] = self.getUnicode(
                    ''.join(result.xpath("./td[@class='song_name']/a[@target]/@href").extract())).strip()
                item['targetTitle'] = self.getUnicode(
                    ''.join(result.xpath("./td[@class='song_name']/a[@target]/@title").extract())).strip()
                item['album'] = self.getUnicode(
                    ''.join(result.xpath("./td[@class='song_album']/a[@target]/@title").extract())).strip()
                item['author'] = self.getUnicode(
                    ''.join(result.xpath("./td[@class='song_artist']/a[@target]/text()").extract())).strip()
                item['createDate'] = datetime.datetime.now()
                item['status'] = 0
                item['processDate'] = datetime.datetime.now()
                item['checkStatus'] = 0
                item['searchTask'] = None if self.searchTaskId == -1 else self.searchTaskId
                item['project'] = None if self.projectId == -1 else self.projectId
                item['program'] = self.program
                if not item['targetUrl'] in self.songsURLS:  # 去重操作
                    if self.filter(targetTitle=item['targetTitle'], author=item['author']):  # 过滤操作
                        self.songsURLS.add(item['targetUrl'])
                        yield item

            if response.xpath("//a[@class='p_redirect_l']/@href"):
                keyword = response.meta['keyword']
                self.keywordsAndPages[keyword] += 1
                pageNum = self.keywordsAndPages[keyword]
                nextURL = u'http://www.xiami.com' + self.getUnicode(''.join(
                    response.xpath("//div[@class='all_page']/a[@class='p_redirect_l']/@href").extract())).strip()
                if pageNum < (self.limit):
                    logging.info(u"==现在爬取的关键字是: %s", keyword)
                    logging.info(u"==现在爬取的关键字的page num是: %s", pageNum)
                    request = Request(url=nextURL)
                    request.meta['keyword'] = keyword
                    request.meta['url'] = nextURL
                    yield request
        else:
            logging.info(response.status)

    def filter(self, targetTitle=None, author=None, album=None):
        """
        过滤操作
        :param targetTitle:
        :param author:
        :param album:关于专辑，暂时不用管
        :return:
        """
        if (self.name.lower() in targetTitle.lower() and self.author.lower() in author.lower()) or (
                        self.name.lower() in targetTitle.lower() and self.author.lower() in targetTitle.lower()):
            logging.debug(u"===我们抓到一只！！！===")
            self.file1.write(self.name)
            self.file1.write(u"targetTitle: " + targetTitle)
            self.file1.write(self.author)
            self.file1.write(u"--author: " + author)
            self.file1.write('\n')
            self.file1.flush()
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
            logging.warning(u"虾米音乐爬虫运行结束： %s" % reason)
        logging.info(u"现在有多少songsURLS(抓取到了多少首歌)： %s" % len(self.songsURLS))
        logging.info(u'现在解析了多少页面： %s' % self.num)
        logging.info(u'limit是： %s' % self.limit)
        logging.info(u'XiamiMusicSearchSpider 爬了这么长时间： %s' % (datetime.datetime.now() - self.startTime))
