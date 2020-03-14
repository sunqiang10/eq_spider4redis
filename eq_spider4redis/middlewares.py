# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware
import random
import os
import redis

class MyUserAgentMiddleware(UserAgentMiddleware):
    def __init__(self, user_agent):
        self.user_agent = user_agent
 
    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            user_agent=crawler.settings.get('MY_USER_AGENT')
        )
    def process_request(self,request,spider):
        referer=request.url
        if referer:
            request.headers["referer"] = referer
        agent=random.choice(self.user_agent)
        request.headers['User-Agent'] = agent

class ProxyMiddleware(object):
    #"""docstring for ProxyMiddleWare"""  
    def process_request(self,request, spider):  
        #'''对request对象加上proxy'''  
        self.scrapy_proxy = self.get_random_proxy(spider)  
        print("this is request ip:"+self.scrapy_proxy)
        if self.scrapy_proxy == '':
            # 将IP从当前的request对象中删除
            pass
        else:
            request.meta['proxy'] = self.scrapy_proxy   
  
  
    def process_response(self, request, response, spider):  
        #'''对返回的response处理'''         
        print(response.status)
         # 如果返回的response状态不是200，重新生成当前request对象  
        if (response.status != 200):  
            self.scrapy_proxy = self.get_random_proxy(spider)  
            print("this is response ip:"+self.scrapy_proxy)
            if self.scrapy_proxy == '':
                pass
            else:
                request.meta['proxy'] = self.scrapy_proxy   
            return request
        if (response.status == 200 and self.scrapy_proxy != ''):  
            redis_password = spider.settings.get('REDIS_PARAMS')['password']
            pool = redis.ConnectionPool(host='127.0.0.1', port=6379, password=redis_password)
            r = redis.Redis(connection_pool=pool) 
            ip = r.sadd('proxy_set',self.scrapy_proxy)
        return response  
  
    def get_random_proxy(self, spider):  
        redis_password = spider.settings.get('REDIS_PARAMS')['password']
        pool = redis.ConnectionPool(host='127.0.0.1', port=6379, password=redis_password)
        ip=''
        r = redis.Redis(connection_pool=pool) 
        if r.scard('proxy_set')>0:
            ip =  str(r.spop('proxy_set'), "utf-8")     
            print("ip:"+ip)
        return ip
class EqSpider4RedisSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class EqSpider4RedisDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
