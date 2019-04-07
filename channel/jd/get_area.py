#!/usr/bin/env python3
# -*-coding:utf-8 -*-

import requests
import time
import json
import pymysql

'''
provinces = [{'data-id': '1'}, {'area_name': '北京'}], \
            [{'data-id': '2'}, {'area_name': '上海'}], \
            [{'data-id': '3'}, {'area_name': '天津'}], \
            [{'data-id': '4'}, {'area_name': '重庆'}], \
            [{'data-id': '5'}, {'area_name': '河北'}], \
            [{'data-id': '6'}, {'area_name': '山西'}], \
            [{'data-id': '7'}, {'area_name': '河南'}], \
            [{'data-id': '8'}, {'area_name': '辽宁'}], \
            [{'data-id': '9'}, {'area_name': '吉林'}], \
            [{'data-id': '10'}, {'area_name': '黑龙江'}], \
            [{'data-id': '11'}, {'area_name': '内蒙古'}], \
            [{'data-id': '12'}, {'area_name': '江苏'}], \
            [{'data-id': '13'}, {'area_name': '山东'}], \
            [{'data-id': '14'}, {'area_name': '安徽'}], \
            [{'data-id': '15'}, {'area_name': '浙江'}], \
            [{'data-id': '16'}, {'area_name': '福建'}], \
            [{'data-id': '17'}, {'area_name': '湖北'}], \
            [{'data-id': '18'}, {'area_name': '湖南'}], \
            [{'data-id': '19'}, {'area_name': '广东'}], \
            [{'data-id': '20'}, {'area_name': '广西'}], \
            [{'data-id': '21'}, {'area_name': '江西'}], \
            [{'data-id': '22'}, {'area_name': '四川'}], \
            [{'data-id': '23'}, {'area_name': '海南'}], \
            [{'data-id': '24'}, {'area_name': '贵州'}], \
            [{'data-id': '25'}, {'area_name': '云南'}], \
            [{'data-id': '26'}, {'area_name': '西藏'}], \
            [{'data-id': '27'}, {'area_name': '陕西'}], \
            [{'data-id': '28'}, {'area_name': '甘肃'}], \
            [{'data-id': '29'}, {'area_name': '青海'}], \
            [{'data-id': '30'}, {'area_name': '宁夏'}], \
            [{'data-id': '31'}, {'area_name': '新疆'}], \
            [{'data-id': '52993'}, {'area_name': '港澳'}], \
            [{'data-id': '32'}, {'area_name': '台湾'}], \
            [{'data-id': '84'}, {'area_name': '钓鱼岛'}], \
            [{'data-id': '53283'}, {'area_name': '海外'}]
'''
provinces = [{'data-id': '24'}, {'area_name': '贵州'}], [{'data-id': '31'}, {'area_name': '新疆'}]

header = {
    'Accept': '* / *',
    'Accept - Encoding': 'gzip, deflate, br',
    'Accept - Language': 'en - US, en;q = 0.9, zh - CN;q = 0.8, zh;q = 0.7',
    'Connection': 'keep - alive',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) \
            Chrome/64.0.3282.186 Safari/537.36'
}

class mysql(object):
    def __init__(self):
        self.connect = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='hang1234', db='shop',
                                       charset='utf8mb4')
        self.cursor = self.connect.cursor()

    def sql_insert(self, sql):
        self.cursor.execute(sql)
        self.connect.commit()



def get_addr():
    db = mysql()
    for province in provinces:
        # print('id:{0},name:{1}'.format(province[0]['data-id'], province[1]['area_name']))
        url = 'https://fts.jd.com/area/get?fid={0}&_={1}'.format(province[0]['data-id'], str(int(time.time())))
        time.sleep(1)
        ret = requests.get(url, headers=header)
        try:
            cities = json.loads(ret.text.encode('utf-8'))
        except Exception as e:
            print(e)
            continue

        if cities:
            for city in cities:
                # print('id:{0},name:{1}'.format(city['id'], city['name']))

                sql = 'insert into t_city (Hcity_id, Hcity_name, Hprovince_id) values ("{0}", "{1}", "{2}");' \
                    .format(city['id'], city['name'], province[0]['data-id'])
                print('city sql:{}'.format(sql))
                db.sql_insert(sql)

                url = 'https://fts.jd.com/area/get?fid={0}&_={1}'.format(city['id'], str(int(time.time())))
                time.sleep(1)
                ret = requests.get(url, headers=header)
                try:
                    areas = json.loads(ret.text.encode('utf-8'))
                except Exception as e:
                    print(e)
                    continue

                if areas:
                    for area in areas:
                        # print('id:{0},name:{1}'.format(area['id'], area['name']))

                        sql = 'insert into t_area (Harea_id, Harea_name, Hcity_id) values ("{0}", "{1}", "{2}");' \
                            .format(area['id'], area['name'], city['id'])
                        print('area sql:{}'.format(sql))
                        db.sql_insert(sql)

                        url = 'https://fts.jd.com/area/get?fid={0}&_={1}'.format(area['id'], str(int(time.time())))
                        try:
                            ret = requests.get(url, headers=header)
                        except Exception as e:
                            print(e)
                            continue

                        towns = json.loads(ret.text.encode('utf-8'))
                        if towns:
                            for town in towns:
                                # print('id:{0},name:{1}'.format(town['id'], town['name']))

                                sql = 'insert into t_town (Htown_id, Htown_name, Harea_id) values  \
                                      ("{0}", "{1}", "{2}");'.format(town['id'], town['name'], area['id'])
                                print('town sql:{}'.format(sql))
                                db.sql_insert(sql)
'''
                                addr = '{0}{1}{2}{3}'.format(province[1]['area_name'], city['name'], area['name'],
                                                             town['name'])
                                code = '{0}_{1}_{2}_{3}'.format(province[0]['data-id'], city['id'], area['id'],
                                                                town['id'])
                                print(addr, code)

                        else:
                            addr = '{0}{1}{2}'.format(province[1]['area_name'], city['name'], area['name'])
                            code = '{0}_{1}_{2}_0'.format(province[0]['data-id'], city['id'], area['id'])
                            print(addr, code)
                else:
                    addr = '{0}{1}'.format(province[1]['area_name'], city['name'])
                    code = '{0}_{1}_0_0)'.format(province[0]['data-id'], city['id'])
                    print(addr, code)
        else:
            addr = province[1]['area_name']
            code = '{0}_0_0_0'.format(province[0]['data-id'])
            print(addr, code)
'''

if __name__ == '__main__':
    get_addr()
