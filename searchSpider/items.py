# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html
#coding=utf-8
import scrapy


class SearchspiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    platform = scrapy.Field()#平台
    keyword = scrapy.Field() #关键词
    resultUrl = scrapy.Field() #搜索结果页面
    targetUrl =  scrapy.Field() #链接网址
    targetTitle =scrapy.Field()  #标题关键字
    createDate =scrapy.Field()  #入库时间
    status = scrapy.Field() #状态
    processDate =scrapy.Field()  #处理时间
    checkStatus = scrapy.Field() #下线检查状态
    searchTask = scrapy.Field() #任务
    project = scrapy.Field() #项目
    program = scrapy.Field()#歌曲名字

class MusicSearchspiderItem(scrapy.Item):
    # define the fields for your item here like:
    program = scrapy.Field()#歌曲名字
    author = scrapy.Field()#作者
    album = scrapy.Field()#专辑
    platform = scrapy.Field()#平台
    keyword = scrapy.Field() #关键词
    resultUrl = scrapy.Field() #搜索结果页面
    targetUrl =  scrapy.Field() #链接网址
    targetTitle =scrapy.Field()  #标题关键字
    createDate =scrapy.Field()  #入库时间
    status = scrapy.Field() #状态
    processDate =scrapy.Field()  #处理时间
    checkStatus = scrapy.Field() #下线检查状态
    searchTask = scrapy.Field() #任务
    project = scrapy.Field() #项目
    unique_code = scrapy.Field() #识别码，去重用的
