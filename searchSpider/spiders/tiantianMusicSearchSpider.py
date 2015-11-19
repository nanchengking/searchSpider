# coding=utf-8
__author__ = 'nancheng'
import sys

reload(sys)
sys.setdefaultencoding('utf-8')
import scrapy
import re
from scrapy import Request
import os
import logging
from searchSpider import settings
from searchSpider.items import *
import datetime
import MySQLdb


class TiantianMusicSearchSpider(scrapy.spiders.Spider):
    name = 'tiantianMusicSearch'
    allow_domains = ['dongting.com']

    def start_requests(self):
        return self.requests

    def __init__(self, keyword, name=None, author=None, album=None, limit=4, projectId=-1, searchTaskId=-1, program='', *args,
                 **kwargs):
        """
        爬虫用来在天天动听音乐搜索页面爬取一系列的关键字
        :param keyword: 关键字，是一个list
        :param targetUrl: 有没有需要直接爬取的链接，暂时不处理
        :param limit: 最多抓取多少页，在这儿，暂且一页代表50条结果
        :param projectId: 项目id
        :param args:
        :param kwargs:
        :return:
        """
        keywords = []
        self.projectId = projectId
        self.searchTaskId = searchTaskId
        self.program = program
        if isinstance(keyword, str):
            keywords = keyword.split(settings.SPLIT_SIGN)
        elif isinstance(keyword, list):
            keywords = keyword
        else:
            self.closed(u'传入keyword参数不合法！无法初始化天天动听音乐爬虫')
        if not keywords:
            self.closed(u'传入keyword参数不合法！无法初始化天天动听音乐爬虫')
        if not isinstance(limit, int):
            limit = int(limit)
        if (not name) or (not author):
            self.closed(u'传入name 或 author参数不合法！无法初始化天天动听音乐爬虫')
        logging.info(u"keywods is : %s" % keywords)
        super(TiantianMusicSearchSpider, self).__init__(*args, **kwargs)
        self.isLinux = os.name == 'posix'  # 判断是否时linux系统
        self.songsURLS = set()
        self.keywordsAndPages = {}
        self.startTime = datetime.datetime.now()
        self.num = 0
        self.limit = limit
        self.name = self.getUnicode(name)
        self.author = self.getUnicode(author)
        self.album = self.getUnicode(album)
        self.file1 = open('jsons.json', 'wb')
        logging.info(u"====天天动听音乐爬虫初始化成功====")
        self.baseURL = ['http://so.ard.iyyin.com/v2/songs/search?q=', '','&page=','1','&size=','50','&callback=jsonp_search']
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
        self.keywordsAndPages[keyword] = 1
        return request

    def parse(self, response):
        self.num += 1
        if response.status == 200:
            true=True#千万不要删除
            false=False
            tem=re.findall(r"^jsonp_search\((.*?)\)$",response.body)
            results=eval(tem[0])['data']
            for result in results:
                item = MusicSearchspiderItem()
                item['platform'] = u"天天动听"
                item['keyword'] = response.meta['keyword']
                item['resultUrl'] = response.meta['url']
                if 'audition_list' in result.keys():
                    item['targetUrl'] = result['audition_list'][0]['url']
                else:
                    item['targetUrl'] = ''
                # item['program'] = result['song_name']
                item['album'] = ''
                item['author'] = result['singer_name']
                item['createDate'] = datetime.datetime.now()
                item['status'] = 0
                item['processDate'] = datetime.datetime.now()
                item['checkStatus'] = 0
                item['searchTask'] = None if self.searchTaskId == -1 else self.searchTaskId
                item['project'] = None if self.projectId == -1 else self.projectId
                item['program'] = self.program
                if not item['targetUrl'] in self.songsURLS:  # 去重操作
                    if self.filters(targetTitle=item['program'], author=item['author']):  # 过滤操作
                        self.songsURLS.add(item['targetUrl'])
                        yield item
            logging.info(u'===这一页有%s条数据==='%results.__len__())
            if results.__len__()==50:#判断还有没有下一页
                keyword = response.meta['keyword']
                self.keywordsAndPages[keyword] += 1
                pageNum = self.keywordsAndPages[keyword]
                keyword = self.getUnicode(keyword)
                nextURL = self.baseURL
                nextURL[1]=keyword
                nextURL[3]=str(pageNum)
                nextURL=''.join(nextURL)
                if pageNum < (self.limit+1):
                    logging.info(u"===现在爬取的关键字是: %s===", keyword)
                    logging.info(u"===现在爬取的关键字的page num是: %s===", pageNum)
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
            logging.warning(u"天天动听音乐爬虫运行结束： %s" % reason)
        logging.info(u"现在有多少songsURLS(抓取到了多少首歌)： %s" % len(self.songsURLS))
        logging.info(u'现在解析了多少页面： %s' % self.num)
        logging.info(u'limit是： %s' % self.limit)
        logging.info(u'tiantiandongtingMusicSearchSpider 爬了这么长时间： %s' % (datetime.datetime.now() - self.startTime))
