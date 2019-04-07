#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import time
import json
from multiprocessing import Pool
from jdbase import shopping
import sys

sys.path.append('../..')
from view.models import Tpassword, Torder, Tuser
from channel import db

from view import hlog

logger = hlog.get_hlog(__name__, '../../log/', 'jd')


class JDWrapper(object):
    '''
    This class used to simulate login JD
    '''

    def __init__(self, usr_name=None, usr_pwd=None):
        # cookie info
        self.trackid = ''
        self.uuid = ''
        self.eid = ''
        self.fp = ''

        self.usr_name = usr_name
        self.usr_pwd = usr_pwd

        self.interval = 0

        # init url related
        self.home = 'https://passport.jd.com/new/login.aspx'
        self.login = 'https://passport.jd.com/uc/loginService'
        self.imag = 'https://authcode.jd.com/verify/image'
        self.auth = 'https://passport.jd.com/uc/showAuthCode'

        self.sess = requests.Session()

        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36',
            'ContentType': 'text/html; charset=utf-8',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Connection': 'keep-alive',
        }

        self.cookies = {

        }

    @staticmethod
    def print_json(resp_text):
        '''
        format the response content
        '''
        if resp_text[0] == '(':
            resp_text = resp_text[1:-1]

        for k, v in json.loads(resp_text).items():
            logger.debug('%s : %s' % (k, v))


def worker(order_info):
    for d in order_info:
        logger.debug(d)
    area = db.session.query(Tuser.Haddress).filter(
        Tuser.Huser_id == order_info[4]
    ).first()

    logger.debug('get areas:{}'.format(area[0]))

    jdsp = shopping.jdShopping(order_info, area[0])
    if not jdsp.check_login():
        # 登录失败 cookie 已经过期
        logger.error('login Failed, retry!')
        return False
    # load good information
    logger.debug('login successful')

    # check time
    start_time = order_info[0] * 1000
    good_name = order_info[2]
    while True:
        value = start_time - int(round(time.time() * 1000))
        '''
        logger.debug(value)
        if value < 0:
            logger.debug('expired goods:{}'.format(good_name))
            # break ######comment just for test!!!!!
        elif value <= 10000:
        '''
        logger.debug('{} will start shopping in 10s, now {}'.format(good_name, round(time.time() * 1000)))
        jdsp.buy()
        #jdsp.cart_detail()
        #jdsp.get_user_info()
        break

if __name__ == '__main__':
    count = Torder.query.filter_by(
        Horder_state=1,  # 状态为新建的单
        # Torder.Hbuy_time > int(time.time()), #大于当前时间
        # Torder.Hbuy_time - int(time.time()) < 10 #10秒以内的单
    ).count()

    logger.debug('get order number:{}'.format(count))

    orders = db.session.query(Torder.Hbuy_time, Torder.Hgoods_id, Torder.Hgoods_name, Tpassword.Hjdpassword, Torder.Huser_id).filter(
        Torder.Horder_state == 1  # 状态为新建的单
        # Torder.Hbuy_time > int(time.time()), #大于当前时间
        # Torder.Hbuy_time - int(time.time()) < 10 #10秒以内的单
    ).all()
    logger.debug('.....................')

    if count <= 0:
        exit()
    elif 0 < count < 200:
        p = Pool(processes=count)
    elif count > 200:
        p = Pool(processes=100)

    for order in orders:
        p.apply_async(worker, (order,))

    logger.debug('process start done')
    p.close()
    p.join()
    logger.debug('process done')
