from scrapy_redis.spiders import RedisSpider
import scrapy
from pyquery import PyQuery as pq 
import json
from urllib.parse import urlencode
#导入item包
from ..items import EqspiderItem
import re
import datetime
import time
#继承自：RedisSpider
# 启动爬虫：scrapy crawl 爬虫名称
# 现象:爬虫处于等待状态
# 需要设置起始任务：
# lpush mycrawler:start_urls 目标url
class CeicSpider(RedisSpider):
    """Spider that reads urls from redis queue (myspider:start_urls)."""
    name = 'crawler_ceic_redis'
    allowed_domains = ['e-te.cn']
    #缺少了start_url,多了redis_key:根据redis_key从redis
    #数据库中获取任务
    redis_key = 'ceic:start_urls'
    custom_settings = {
        'DOWNLOADER_MIDDLEWARES':{
           # 'eq_spider4redis.middlewares.EqSpider4RedisSpiderMiddleware': 543,
           'eq_spider4redis.middlewares.MyUserAgentMiddleware': 400,
           # 'scrapy.downloadmiddlewares.useragent.UserAgentMiddleware': None,
           'eq_spider4redis.middlewares.ProxyMiddleware': 543
        },
        # 'ITEM_PIPELINES' : {
        #     'eq_spider4redis.pipelines.DuplicatesPipeline': 400,
        # }
    }
    def make_requests_from_url(self, url):
        if url.find('ceic.ac.cn')>0:
            tt = int(time.time())
            u = 'http://news.ceic.ac.cn/index.html?time=' + str(tt)
            return scrapy.Request(u, callback=self.parse, dont_filter=True)
        if url.find('m.weibo.cn')>0:
            params = {
                'containerid':'231522type=1&t=10&q=#地震快讯#',
                'isnewpage':1,
                'luicode':'10000011',
                'lfid':'231522type=1&q=#地震快讯#',
                'sudaref':'login.sina.com.cn',
                'display':0,
                'retcode':6102,
                'page_type':'searchall'
            }
            u = 'https://m.weibo.cn/api/container/getIndex?'+ urlencode(params)
            return scrapy.Request(u, callback=self.parse, dont_filter=True)
    def parse(self, response):
        if response.url.find('ceic.ac.cn')>0:            
            for trText in response.xpath('//table[@ class="news-table"]/tr'): 
                text = trText.xpath('./td/text()').extract() 
                if(len(text)>0):
                    item = EqspiderItem()
                    dateTime_p=datetime.datetime.strptime(text[1],'%Y-%m-%d %H:%M:%S')
                    item['Cata_id'] ='CE'+ text[1][0:16].replace("-", " ").replace(":", " ").replace(" ", "")
                    item['Eq_type'] =0
                    item['M'] = text[0]
                    item['O_time'] = dateTime_p
                    item['Lat'] = text[2]
                    item['Lon'] = text[3]
                    item['Depth'] = text[4]
                    item['is_create_pic'] = 0
                    item['Location_cname'] =trText.xpath('./td/a/text()').get()
                    item['geom'] ='POINT('+text[3]+' '+text[2]+')'
                    yield item
        if response.url.find('m.weibo.cn')>0:            
            rs =  json.loads(response.text)
            cards = rs.get('data').get('cards')
            for card in cards:
                mblog = card.get('mblog')            
                if mblog:               
                    item = EqspiderItem()
                    text = mblog.get('text')
                    #print(text)
                    pattern = re.compile(r'^.*?(中国地震台网正式测定).*(\d{1,2})月(\d{1,2})日(\d{1,2})时(\d{1,2})分在(.*)\S{2}纬(\d*\.\d{2})度，.*经(\d*\.\d{2})度.*发生(\d*\.\d{1}).*震源深度(\d*).*$')
                    match = pattern.match(text)
                    if match:
                        dateTime_p = datetime.datetime.strptime(str(datetime.datetime.now().year)+"-"
                            + str(match.group(2)) +"-"
                            + str(match.group(3)) +" "
                            + str(match.group(4)) +":"
                            + str(match.group(5)),'%Y-%m-%d %H:%M')
                  
                        tt = int(time.time())

                        item['O_time'] = dateTime_p
                        dateText = datetime.datetime.strftime(dateTime_p, '%Y%m%d%H%M')
                        item['Cata_id'] = 'CE'+ dateText
                        item['Eq_type'] =0
                        item['Location_cname'] =match.group(6)
                        item['Lat'] = match.group(7)
                        item['Lon'] = match.group(8)
                        item['M'] = match.group(9)                   
                        item['Depth'] = match.group(10)
                        item['is_create_pic'] = 0
                        item['geom'] ='POINT('+match.group(8)+' '+match.group(7)+')'
                        yield item