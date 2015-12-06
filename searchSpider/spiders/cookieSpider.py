#coding=utf-8
from scrapy.http.cookies import CookieJar
import scrapy
import sqlite3
from scrapy import Request
import logging

class CookieSpider(scrapy.Spider):

	name='cookie'
	download_delay =2 

	def __init__(self,times=5):
		self.baseURL="http://www.xiami.com/search?key="
		logging.debug("=====")
		self.counts=0
		self.connection = sqlite3.connect("cookies.db")
		self.times=times
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
		self.init_db()
		logging.debug("cookies爬虫初始化成功")
	

	def init_db(self):
		self.conn = sqlite3.connect("cookies.db")
		self.cursor=self.conn.cursor()
		create="""
		create table if not exists xiami(id int,_unsign_token text,bdshare_firstime text,user text,CNZZDATA921634 text,member_auth text,user_from text,join_from text,
		ahtena_is_show text,_xiamitoken text,promotion_opened text,promotion_opened_toggler text,l text,isg text,CNZZDATA2629111 text)
		"""
		delete="""
		delete from xiami
		"""
		insert="""
	    insert into xiami values(99," "," "," "," "," "," "," ", " "," "," "," "," "," "," ")
		"""
		self.cursor.execute(create)
		self.cursor.execute(delete)
		self.cursor.execute(insert)
		self.conn.commit()
		logging.debug("数据库准备完毕")

	def start_requests(self):
		yield Request(url=self.baseURL+str(self.counts),cookies=self.xiami_cookies)

	def map_cookie(self,cookie=""):
		ck={}
		big_ck=cookie.split(";")
		for i in big_ck:
			a=i.split("=")
			ck[a[0]]=a[1]
		return ck
	
	def parse(self,response):
		if response.status==200:
			cookies=self.map_cookie(''.join(response.request.headers.getlist('Cookie')))
			for i in cookies:
				update='update xiami set '+i+"=? where id = ?"
				self.cursor.execute(update,(cookies[i],99))
			logging.debug("接受一次cookie更新")
			self.conn.commit()
			if self.counts<self.times:
				self.counts+=1
				yield Request(url=self.baseURL+str(self.counts))
		else :
			logging.debug("返回错误%s"%response.code)
