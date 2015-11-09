# coding=utf-8
import MySQLdb

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


class SogouSearchSpider(scrapy.spiders.Spider):
    name = 'sogouSearch'
    # allow_domains = ['baidu.com']

    def start_requests(self):
        return self.requests

    def __init__(self, keyword, filters='', blackWords='', whiteWords='', blackURLs='', whiteURLs='', targetUrl=None,
                 limit=4, projectId=-1, searchTaskId=-1, *args, **kwargs):
        """
        爬虫用来在搜狗搜索页面爬取一系列的关键字
        :param keyword: 关键字，是一个list
        :param filters: 标准过滤方式，目标item存在任意一个filters里面的关键字就有可能侵权
        :param blackWords: 存在该关键字就一定是侵权，暂时不处理
        :param whiteWords: 存在该关键字就一定不会是侵权
        :param blackURLs: 该域名的网站都是侵权的
        :param whiteURLs: 该域名的网站都不是侵权的
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
            self.closed(u'传入keyword参数不合法！无法初始化搜狗爬虫')
        if not keywords:
            self.closed(u'传入keyword参数不合法！无法初始化搜狗爬虫')
        if not isinstance(limit, int):
            limit = int(limit)
        if isinstance(filters, str):
            logging.info("传入的filters参数值为：%s" % filters)
            self.filters = filters.split(settings.SPLIT_SIGN)
        else:
            self.closed(u'传入filters参数不合法，必须为str！无法初始化搜狗爬虫')
        if len(self.filters) < 1:
            self.closed(u'传入filters参数为空！无法初始化搜狗爬虫')
        logging.info(u"keywods is : %s" % keywords)
        logging.info(u"搜狗爬虫初始化成功")
        self.isLinux = False
        super(SogouSearchSpider, self).__init__(*args, **kwargs)
        self.initFilterPramas(whiteWords=whiteWords, blackWords=blackWords, blackURLs=blackURLs, whiteURLs=whiteURLs)
        self.realURLs = set()
        self.faceURLs = set()
        self.startTime = datetime.datetime.now()
        self.num = 0
        self.limit = limit
        self.keywordsAndPages = {}
        # "https://www.sogou.com/web?query=%E5%A6%B9%E5%AD%90&sut=1013&lkt=1%2C1445092071106%2C1445092071106&sst0=1445092071216&page=21&ie=utf8&p=40040100&dp=1&w=01019900&dr=1"
        self.baseURL = ['https://www.sogou.com/web?query=', '', '&page=', '1']
        self.requests = map(self.initStartRequests, keywords)

    def initFilterPramas(self, whiteWords, blackWords, blackURLs, whiteURLs):
        """
        初始化一些过滤参数
        :param whiteWords: 白名单关键字
        :param blackWords: 黑名单关键字，暂时不处理
        :param blackURLs: 黑名单域名
        :param whiteURLs: 白名单域名
        :return:
        """
        if isinstance(whiteWords, str):
            self.whiteWords = map(self.getUnicode, whiteWords.split(settings.SPLIT_SIGN))
        if isinstance(blackWords, str):
            self.blackWords = map(self.getUnicode, blackWords.split(settings.SPLIT_SIGN))
        if isinstance(blackURLs, str):
            self.blackURLs = map(self.getUnicode, blackURLs.split(settings.SPLIT_SIGN))
        if isinstance(whiteURLs, str):
            self.whiteURLs = map(self.getUnicode, whiteURLs.split(settings.SPLIT_SIGN))

        conn = MySQLdb.Connect(host=settings.MYSQL_HOST,
                                    port=settings.MYSQL_PORT,
                                    user=settings.MYSQL_USER,
                                    passwd=settings.MYSQL_PASSWD,
                                    db=settings.MYSQL_DB,
                                    charset=settings.MYSQL_CHARSET)
        cur = conn.cursor()
        cur.execute("select `name`, `type`, `whiteorblack` from `web_whiteblacklist` where `status` = 1")
        results = cur.fetchall()
        for row in results:
            name = row[0]
            type = row[1]
            whiteorblack = row[2]
            if type == 0: # 标题
                if whiteorblack == 0: # 白名单
                    self.whiteWords.append(self.getUnicode(name))
                elif whiteorblack == 1: # 黑名单
                    self.blackWords.append(self.getUnicode(name))
            elif type == 1: # url
                if whiteorblack == 0: # 白名单
                    self.whiteURLs.append(self.getUnicode(name))
                elif whiteorblack == 1:
                    self.blackURLs.append(self.getUnicode(name))
        cur.close()
        conn.close()
        arr = [ x for x in self.whiteWords if x != '' ]
        self.whiteWords = arr
        arr = [ x for x in self.blackWords if x != '' ]
        self.blackWords = arr
        arr = [ x for x in self.whiteURLs if x != '' ]
        self.whiteURLs = arr
        arr = [ x for x in self.blackURLs if x != '' ]
        self.blackURLs = arr
        logging.info("White words: %s" % self.whiteWords)
        logging.info("Black words: %s" % self.blackWords)
        logging.info("White urls: %s" % self.whiteURLs)
        logging.info("Black urls: %s" % self.blackURLs)

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
        self.keywordsAndPages[keyword] = 1  # 每一个关键字开始爬取的都是第一页
        return request

    def createNextPageRequest(self, keyword, pn):
        """
        针对每一个关键字，生成一个request，可以增长页面的
        :param keyword: 需要查询的关键字
        :param pn: 1代表第一页，2代表第二页，3代表第三页……
        :return:一个request
        """
        tem = self.baseURL
        tem[1] = keyword
        tem[3] = str(pn)
        url = ''.join(tem)
        request = Request(url=url)
        request.meta['keyword'] = keyword
        request.meta['url'] = url
        return request

    def parse(self, response):
        self.num += 1
        if response.status == 200:
            results = response.xpath("//div[@id='main']/div/div[@class='results']/div")
            for result in results:
                item = SearchspiderItem()
                item['platform'] = u"搜狗搜索"
                item['keyword'] = response.meta['keyword']
                item['resultUrl'] = response.meta['url']
                item['targetUrl'] = self.getUnicode(''.join(result.xpath(".//h3/a[@href]/@href").extract()))
                item['targetTitle'] = self.getUnicode(''.join(result.xpath(".//h3/a[@href]//text()").extract()))
                item['createDate'] = datetime.datetime.now()
                item['status'] = 0
                item['processDate'] = datetime.datetime.now()
                item['checkStatus'] = 0
                item['searchTask'] = 0
                item['searchTask'] = None if self.searchTaskId == -1 else self.searchTaskId
                item['project'] = self.projectId
                if self.filter(targetTitle=item['targetTitle']):
                    logging.info(u"===开始检测url===")
                    if not item['targetUrl'] in self.faceURLs:  # 去重操作
                        self.faceURLs.add(item['targetUrl'])
                        yield self.checkURLis200(url=item['targetUrl'], item=item)
            keyword = response.meta['keyword']
            self.keywordsAndPages[keyword] += 1
            pageNum = self.keywordsAndPages[keyword]
            logging.info(u"num 是 %s" % pageNum)
            logging.info(u"limit 是 %s" % self.limit)
            if pageNum <= self.limit:
                logging.info(u'==发出下一页请求==')
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

    def checkURLis200(self, url, item):
        """
        名字起的不太好，这儿其实是一个调用getRealURL的中转站而已。
        :param url:
        :param item:
        :return:
        """
        if url != "":
            logging.info('Check url is 200: %s' % url)
            request = Request(url=url, callback=self.getRealURLAndDoFilter)
            request.meta['item'] = item
            request.meta['dont_redirect'] = True
            return request
        else:
            return None

    def getRealURLAndDoFilter(self, response):
        """
        得到真实的（重定向之后的）url
        同时负责大部分过滤操作！！！
        当然，这儿还有一步去重的操作，把真实url相同的去除
        :param response:
        :return:
        """
        logging.info(u"======调用getRealURLAndDoFilter======")
        # response.xpath("//script").re(r'\"(.*?)\"')[0]
        item = response.meta['item']
        if u'www.sogou.com/link?' in self.getUnicode(response.url):
            item['targetUrl'] = ''.join(response.xpath("//script").re(r'\"(.*?)\"'))
        elif "Location" in response.headers:
            item['targetUrl'] = response.headers["Location"]
        else :
            item['targetUrl'] = response.url

        if self.whiteURLs and self.blackURLs and self.whiteWords:  # 只有这三个参数同时有效才调用下面的判断过滤逻辑
            logging.info(u'===调用高级过滤方式===')
            if not [i for i in self.whiteURLs if i in item['targetUrl']]:  # 只要不是在url白名单内的数据，才进行下面的判断
                if [i for i in self.blackURLs if i in item['targetUrl']]:  # 在url内的黑名单，一定是侵权
                    if not response.url in self.realURLs:
                        self.realURLs.add(response.url)
                        logging.info(u"找到一个侵权链接（url黑名单）：%s" % item['targetUrl'])
                        return item
                else:  # 不在url黑名单，需要判断是否有恶搞倾向
                    if not [i for i in self.whiteWords if i in item['targetTitle']]:  # 如果白名单关键字的里面没有，也就是，没有恶搞倾向
                        if not response.url in self.realURLs:
                            self.realURLs.add(response.url)
                            logging.info(u"找到一个侵权链接（url白名单没有）：%s" % item['targetUrl'])
                            return item
                        else:
                            logging.info(u"url白名单拦截：%s" % item['targetUrl'])

        else:  # 上面三个参数无效，这儿就直接进行简单的item收集
            logging.info(u'===调用普通过滤方式===')
            if not response.url in self.realURLs:
                self.realURLs.add(response.url)
                logging.info(u"找到一个侵权链接：%s" % item['targetUrl'])
                return item

    def filter(self, targetTitle):
        """
         使用简单的关键词过滤，如果存在关键字，就返回True，否则，返回false
        :param targetTitle: 需要顾虑的部分，这儿选用标题
        :return:
        """
        count = 0
        for filter in self.filters:
            if self.getUnicode(filter) in targetTitle:
                logging.info(u'===过滤关键字filter is===%s' % self.getUnicode(filter))
                count += 1  # 考虑可能需要分级，命中关键字多的，嫌疑也比较大，这儿暂时不加处理
                logging.info(str(count))
        if count >= 1:
            return True
        else:
            return False

    def closed(self, reason):
        if reason:
            logging.warning(u"搜狗爬虫运行结束： %s" % reason)
        logging.info(u"现在有多少self.realURLs： %s" % len(self.realURLs))
        logging.info(u"现在有多少self.faceURLs： %s" % len(self.faceURLs))
        logging.info(u'现在解析了多少页面： %s' % self.num)
        logging.info(u'limit是： %s' % self.limit)
        logging.info(u'sogouSearchSpider 爬了这么长时间： %s' % (datetime.datetime.now() - self.startTime))
