# -*- coding: utf-8 -*-
import requests
import json
import re
import csv, time, sys, os
from threading import _main_thread
from datetime import datetime
import codecs

FuncName = lambda n=0: sys._getframe(n + 1).f_code.co_name

class jdSecKiller(object):
    def __init__(self):
        self.urls = [
            'http://ai.jd.com/index_new?app=Seckill&action=pcSeckillCategoryGoods&callback=pcSeckillCategoryGoods&id=29&_=1495211171059',
            # 电脑办公
            'http://ai.jd.com/index_new?app=Seckill&action=pcSeckillCategoryGoods&callback=pcSeckillCategoryGoods&id=19&_=1495250002658',
            # 生活电器
            'http://ai.jd.com/index_new?app=Seckill&action=pcSeckillCategoryGoods&callback=pcSeckillCategoryGoods&id=30&_=1495251020781',
            # 手机通讯
            'http://ai.jd.com/index_new?app=Seckill&action=pcSeckillCategoryGoods&callback=pcSeckillCategoryGoods&id=25&_=1495251044176',
            # 大家电
            'http://ai.jd.com/index_new?app=Seckill&action=pcSeckillCategoryGoods&callback=pcSeckillCategoryGoods&id=31&_=1495251057993',
            # 智能数码
            'http://ai.jd.com/index_new?app=Seckill&action=pcSeckillCategoryGoods&callback=pcSeckillCategoryGoods&id=45&_=1495251084828',
            # 饮料酒水
            'http://ai.jd.com/index_new?app=Seckill&action=pcSeckillCategoryGoods&callback=pcSeckillCategoryGoods&id=37&_=1495251148047',
            # 家具家装
            'http://ai.jd.com/index_new?app=Seckill&action=pcSeckillCategoryGoods&callback=pcSeckillCategoryGoods&id=43&_=1495251122767',
            # 母婴童装
            'http://ai.jd.com/index_new?app=Seckill&action=pcSeckillCategoryGoods&callback=pcSeckillCategoryGoods&id=44&_=1495250603966',
            # 食品生鲜
            'http://ai.jd.com/index_new?app=Seckill&action=pcSeckillCategoryGoods&callback=pcSeckillCategoryGoods&id=32&_=1495251170952'
            # 个护家清
        ]

        self.buffer_list = []
        self.category = [29, 19, 30, 25, 31, 45, 37, 43, 44, 32, 46, 36, 34, 33, 35, 38, 42, 40, 41, 39]
        self.category_dict = {
            '29' : '电脑办公',
            '19' : '生活电器',
            '30' : '手机通讯',
            '25' : '大家电',
            '31' : '智能数码',
            '45' : '饮料酒水',
            '37' : '家居家装',
            '43' : '母婴童装',
            '44' : '食品生鲜',
            '32' : '个护家清',
            '46' : '美肤',
            '36' : '运动户外',
            '34' : '潮流鞋靴',
            '33' : '流行服装',
            '35' : '内衣',
            '38' : '钟表珠宝',
            '42' : '居家百货',
            '40' : '医药保健',
            '41' : '箱包服配',
            '39' : '汽车用品'
        }

    def get_price(self, ware_id):
        # get good price
        url = 'http://p.3.cn/prices/mgets'
        payload = {
            'type': 1,
            'pduid': int(time.time() * 1000),
            'skuIds': 'J_' + ware_id,
        }

        price = '?'
        try:
            resp = requests.get(url, params=payload)
            resp_txt = resp.text.strip()
            js = json.loads(resp_txt[1:-1])
            price = js.get('p')

        except Exception as e:
            print('Exp {0} : {1}'.format(FuncName(), e))

        return price

    def secKiller(self, url, category_id=29):

        resp = requests.get(url)
        resp_text = re.findall(r'\((.+)\)', resp.text)[0]
        s = json.loads(resp_text)

        category_name = ''
        for (k, v) in self.category_dict.items():
            if int(k) == category_id:
                category_name = self.category_dict[k]
                break

        for i in s['goodsList']:
            good_id = i['wareId']
            good_name = i['wname']
            startRemainTime = i['startRemainTime']
            seckillNum = i['seckillNum']
            jdPrice = i['jdPrice']
            startTimeShow = i['startTimeShow']
            startTime = i['startTime']
            endTime = i['endTime']
            miaoShaPrice = i['miaoShaPrice']
            item_url = "http://item.jd.com/" + str(good_id) + ".html"
            promotion_rate = round((float(miaoShaPrice) / float(jdPrice)), 2)

            if 'soldRate' in i.keys():
                sales_status = str(i['soldRate']) + "%"
            else:
                if 'startTimeContent' in i.keys():
                    if not i['startTimeContent']:
                        sales_status = "---"
                    else:
                        sales_status = i['startTimeContent']
                else:
                    sales_status = "---"

            if float(startRemainTime) >= 0 and (promotion_rate < 0.2 or float(miaoShaPrice) < 10):
                dynamic_price = self.get_price(good_id)
                self.buffer_list.append([category_name, good_name[:40], seckillNum, miaoShaPrice, dynamic_price, jdPrice, promotion_rate, sales_status,
                              item_url])
                print ([category_name, good_name[:40], seckillNum, miaoShaPrice, dynamic_price, jdPrice, promotion_rate, sales_status,
                              item_url])

if __name__ == '__main__':
    jd = jdSecKiller()
    #f = os.path.dirname(os.getcwd()) + '\\Files\\'
    file_name_suffix = str(datetime.now()).replace(':',',')
    #file_name = os.path.join(f, 'jd_'+file_name_suffix+'.csv')
    file_name = 'jd_'+file_name_suffix+'.csv'

    for url_cnt in range(0, len(jd.category) ):
        rid = str(int(time.time() * 1000))
        url_tmp = 'http://ai.jd.com/index_new?app=Seckill&action=pcSeckillCategoryGoods&callback=pcSeckillCategoryGoods&id=' + str(
            jd.category[url_cnt]) + '&_=' + rid
        jd.secKiller(url_tmp, jd.category[url_cnt])

    with open(file_name, "w", newline="") as datacsv:
        csvwriter = csv.writer(datacsv, dialect="excel")
        csvwriter.writerow(["商品分类", "商品名称", "秒杀数量", "秒杀价格", "现价", "原价", "折扣率", "秒杀时间", "链接地址"])
        datacsv.close
# 
#     #先时间排序，再按折扣排序，接着按秒杀价格排序
    sorted_list = sorted(jd.buffer_list, key = lambda x : (x[7], float(x[6]) , float(x[3])))
 
    with open(file_name, "a+", newline="") as datacsv:
        csvwriter = csv.writer(datacsv, dialect=("excel"))
        for i in range(0, len(sorted_list)):
            csvwriter.writerow(sorted_list[i])
    datacsv.close