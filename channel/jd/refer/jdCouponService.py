# -*- coding: utf-8 -*-
'''
Created on Oct 16, 2017

@author: 500654
'''

import requests
import json
import random
import logging
from datetime import datetime
import time
import sys
import os
import pickle
import traceback
from pathlib import Path
from config import config
import http
import jdLoginService

FuncName = lambda n=0: sys._getframe(n + 1).f_code.co_name

class JDCouponService():
    def __init__(self):
#         self.headers = {
#                 "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:55.0) Gecko/20100101 Firefox/55.0",
#               "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#               "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
#               "Accept-Encoding": "gzip, deflate",
#               #"Referer": "https://a.jd.com/?cateId=19",  # 防盗链
#               "Referer": "https://a.jd.com/?cateId=0",
#               "Connection": "keep-alive",
#               "Upgrade-Insecure-Requests": "1"        
#         }

        self.valid_coupon_list = {
            0:'精选',
            19:'手机数码',
            16:'家用电器',
            15:'食品饮料',
            11:'电脑办公',
            14:'母婴用品',
            13:'运动户外',
            20:'家居家纺',
            84:'汽车用品',
            105:'生鲜'
        }
#         
#         self.valid_coupon_list = {
#             105:'生鲜'
#         }
        
        self.sess = requests.Session()  
        self.sess.cookies = jdLoginService.jdLogin()
            
    def make_session(self):
        self.sess = requests.Session()

        self.sess.headers.update({
            'User-Agent': config.ua,
            'Referer' : config.referer
        })
        
        self.sess.headers.update()

        data_file = Path(__file__).parent.joinpath('cookie')

        if data_file.exists():
            try:
                bytes = data_file.read_bytes()
                cookies = pickle.loads(bytes)
                self.sess.cookies = cookies
                logging.info('# 从文件加载 cookies 成功.')
            except Exception as e:
                logging.info('# 未能成功载入 cookies, 从头开始~')

        return self.sess

    def save_session(self, session):
        data = pickle.dumps(session.cookies)

        data_dir = Path(__file__).parent.joinpath('../data/')
        data_dir.mkdir(exist_ok=True)
        data_file = data_dir.joinpath('cookies')
        data_file.write_bytes(data)
        
    #this can be decomissioned, as we have will category id dict 
    def get_coupon_category_list(self):
        url = 'https://a.jd.com/indexAjax/getCatalogList.html'
        params = {
            'callback' : 'jQuery'#,
            #'_' : random.randint(1000000000000, 1999999999999)
            }
        resp = self.sess.get(url, params=params)
        try:
            resp_json = json.loads(resp.text[7:-1])
             
            resultCode = resp_json['resultCode'] #200 success
            for item in resp_json['catalogList']: 
                if item['categoryId'] in self.valid_coupon_list.keys():
                    category = {int(item['categoryId']): item['categoryName']}
                    self.get_coupon_list(category, False)
                
            return True
        except Exception as e:
            print( e)
            return False
    
    def get_coupon_list(self, category, post = False):  
        
        url = 'https://a.jd.com/indexAjax/getCouponListByCatalogId.html'
        
        for categoryId, categoryName in category.items():
            category[categoryId] = categoryName            
            params = {
                'callback': 'jQuery',
                'catalogId' : categoryId,
                'page'  : '1',
                'pageSize' : '100',
                '_' :   round(time.time()*1000)
                }
            resp = self.sess.get(url, params = params)
            resp.encoding = 'utf-8'
            resp_json = json.loads(resp.text[7:-1])
            resultCode = resp_json['resultCode']       
            
            for item in resp_json['couponList']:
                try:
                    discount_rate = str(round((float(item['quota']) - float(item['denomination'])) / float(item['quota']),2))
                except Exception as e:
                    discount_rate = '---'
                
#                 if item['receiveFlag'] == 0 and item['needBean'] == '' and float(item['rate']) < 100 and item['leftTime'] == 'null':
                if item['receiveFlag'] == 0 and float(item['rate']) < 100 and item['leftTime'] == None:                    
                    
                    if post:
                        print ('{0}\t{1}\t{2}\t{3}'.
                               format(categoryName, item['batchCount'], item['successLabel'], item['limitStr']))
                        try:
                            self.post_coupon(coupon_key = item['ruleKey'])
                            time.sleep(3)
                        except Exception as e:
                            print (e)
                            time.sleep(3)
                            continue      
                    else:
                        print ('{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\t{8}\t{9}\t{10}\t{11}\t{12}\t{13}\t{14}'
                           .format(categoryName, item['startTime'], 
                           item['endTime'], item['batchCount'], str(item['rate']) + '%',item['quota'], item['denomination'], 
                           discount_rate ,item['successLabel'], item['limitStr'], item['shopId'],item['dongOverlapText'],
                            item['receiveFlag'], item['receiveUrl'], item['leftTime']))                               
                                
            
    def post_coupon(self, coupon_key):
        logging.info('开始抢券')
        #coupon_key = 'ca1d8391c9f1e3298e190003b470645df7666e3a9feaa622ca6d8dc2adf21bb8a77ac014ff77069e81b5ed84dda895d3'
        url = 'https://a.jd.com/indexAjax/getCoupon.html'
        params = {
            'callback' : 'jQuery',
            'key'   : coupon_key,
            'type'  : '1',
            '_'     : round(time.time()*1000)
            }
        self.sess.headers.update(
            {'Referer' : 'https://a.jd.com/'
                })
        resp = self.sess.get(url, params = params)        
        resp_json = json.loads(resp.text[7:-1])
        result_message = resp_json['message']
        if result_message == '抢得太快了，臣妾做不到啊~':
            time.sleep(1)
            print('妈的，说我抢太快了，那就等1秒钟吧，然后我再继续，草！')
            self.post_coupon(coupon_key)
        elif result_message == "钱包都被挤爆了，明天再来吧~":
            print('我日，说我钱包都被挤爆了，明天再来吧~，噩噩噩噩，好吧！Bye')
            return
        elif u'火爆' in result_message:
            time.sleep(1)
            print(result_message)
            self.post_coupon(coupon_key)
        elif '很抱歉，没抢到' in  result_message:
            time.sleep(1)
            print(result_message)
            self.post_coupon(coupon_key) 
        else:
            print (result_message)
        
        
        logging.info('任务完成，ByeBye!')
        
    #this is most accurate method, but due to network latency, it should not be used...    
    def get_accurate_jd_time(self):
        url = 'https://a.jd.com/ajax/queryServerData.html'  
        params = {
            'r' : random.random()
            } 
        
        resp = requests.get(url, headers = self.headers, params=params )
        resp_json = json.loads(resp.text)
        readable_time = int(resp_json['serverTime'])/1000 
        return (datetime.fromtimestamp(readable_time))
    
#let's try it simple and ping jd to get time from header
def getJDServerTime():
    conn = http.client.HTTPConnection('a.jd.com')
    conn.request('GET', '/')
    response = conn.getresponse()
    ts = response.getheader('Date')     
    ltime = time.strptime(ts[5:25], '%d %b %Y %H:%M:%S')  
    
    serverTime =  time.strftime( '%H:%M:%S',
        time.localtime(time.mktime(ltime)+ 8*3600 )).split(':')    #将GMT时间转换为北京时间并以列表形式返回, -> [ hour, minute, second ]        
    return serverTime           

# if __name__ == '__main__':
#     jd = JDCouponService()
#     while True:
#         jd.get_coupon_list(jd.valid_coupon_list)        
#         logging.info('任务完成，ByeBye!')