#!/usr/bin/env python3
#-*-coding:utf-8 -*-
from selenium import webdriver
import time
import pickle
import configparser
import requests
import json
import sys
import os
import random

# get function name
FileName = lambda n=0: sys._getframe(n + 1).f_code.co_filename
FuncName = lambda n=0: sys._getframe(n + 1).f_code.co_name
LineNum  = lambda n=0: sys._getframe(n + 1).f_lineno

'''
jdLogin class support qr login or username&password,
if login successful save cookies and return True
'''

class jdLogin(object):
    def __init__(self):

        self.sess = requests.Session()

        self.cookies = {

        }

        self.headers = {
            'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36',
            'ContentType': 'text/html; charset=utf-8',
            'Accept-Encoding':'gzip, deflate, sdch',
            'Accept-Language':'zh-CN,zh;q=0.8',
            'Connection' : 'keep-alive',
        }

    def passwdLogin(self):
        conInfo = configparser.ConfigParser()
        try:
            conInfo.read('config.ini',encoding='utf-8')
        except IOError as e:
            print('打开配置文件"%s"失败啦, 请先创建或者拷贝一份配置文件config.ini')
            return

        self.username = conInfo.get('login', 'username')
        self.password = conInfo.get('login', 'password')

        self.driver = webdriver.Chrome()
        self.driver.get('https://passport.jd.com/uc/login?ltype=logout')
        #切换到frame里面 负责找不到CheckBox元素
        #driver.switch_to.frame("loginMain")

        self.driver.find_element_by_link_text("账户登录").click()
        self.driver.find_element_by_name("loginname").send_keys(self.username)
        self.driver.find_element_by_name("nloginpwd").send_keys(self.password)
        self.driver.find_element_by_id("loginsubmit").click()
        time.sleep(1)
        authcodeFlag = self.driver.find_element_by_id("o-authcode").get_attribute('style')
        print(authcodeFlag)
        if 'block' in authcodeFlag:
            print("find authcode")
            while True:
                authcode = input('input authcode:')
                self.driver.find_element_by_name("authcode").send_keys(authcode)
                self.driver.find_element_by_id("loginsubmit").click()
                time.sleep(1)
                print(self.driver.current_url)
                if self.driver.current_url == 'https://www.jd.com/':
                    break


        #login success, save cookies

        for item in self.driver.get_cookies():
            print(item['name'], item['value'])
            self.cookies[item['name']] = item['value']
        with open('cookies', 'wb') as f:
            pickle.dump(self.cookies, f)

        return True

    def login_by_QR(self):
        print(FuncName(), LineNum())
        # jd login by QR code
        try:
            print ('++++++++++++++++++++++{},{}+++++++++++++++++++++++++++++++++'.format(FuncName(), LineNum()))
            print (u'{0} > 请打开京东手机客户端，准备扫码登陆:'.format(time.ctime()))

            urls = (
                'https://passport.jd.com/new/login.aspx',
                'https://qr.m.jd.com/show',
                'https://qr.m.jd.com/check',
                'https://passport.jd.com/uc/qrCodeTicketValidation'
            )

            # step 1: open login page
            resp = self.sess.get(
                urls[0],
                headers = self.headers
            )
            if resp.status_code != requests.codes.OK:
                print ('获取登录页失败: {}'.format(resp.status_code))
                return False

            ## save cookies
            for k, v in resp.cookies.items():
                self.cookies[k] = v


            # step 2: get QR image
            resp = self.sess.get(
                urls[1],
                headers = self.headers,
                cookies = self.cookies,
                params = {
                    'appid': 133,
                    'size': 147,
                    't': (int)(time.time() * 1000)
                }
            )
            if resp.status_code != requests.codes.OK:
                print ('获取二维码失败: {}'.format(resp.status_code))
                return False

            ## save cookies
            for k, v in resp.cookies.items():
                self.cookies[k] = v

            ## save QR code
            image_file = 'qr.png'
            with open (image_file, 'wb') as f:
                for chunk in resp.iter_content(chunk_size=1024):
                    f.write(chunk)

            ## scan QR code with phone
            if os.name == "nt":
                # for windows
                os.system('start ' + image_file)
            else:
                if os.uname()[0] == "Linux":
                    # for linux platform
                    os.system("eog " + image_file + "&")
                else:
                    # for Mac platform
                    os.system("open " + image_file)

            # step 3: check scan result
            ## mush have
            self.headers['Host'] = 'qr.m.jd.com'
            self.headers['Referer'] = 'https://passport.jd.com/new/login.aspx'

            # check if QR code scanned
            qr_ticket = None
            retry_times = 62
            while retry_times:
                retry_times -= 1
                resp = self.sess.get(
                    urls[2],
                    headers = self.headers,
                    cookies = self.cookies,
                    params = {
                        'callback': 'jQuery%u' % random.randint(1000000, 9999999),
                        'appid': 133,
                        'token': self.cookies['wlfstk_smdl'],
                        '_': (int)(time.time() * 1000)
                    }
                )
                print ('checking...')
                print('QRCodeKey:{},wlfstk_smdl:{}'.format(self.cookies['QRCodeKey'],self.cookies['wlfstk_smdl']))
                time.sleep(3)

                if resp.status_code != requests.codes.OK:
                    continue

                n1 = resp.text.find('(')
                n2 = resp.text.find(')')
                rs = json.loads(resp.text[n1+1:n2])

                if rs['code'] == 200:
                    print ('{} : {}'.format(rs['code'], rs['ticket']))
                    qr_ticket = rs['ticket']
                    break
                else:
                    print ('{} : {}'.format(rs['code'], rs['msg']))
                    time.sleep(3)

            if not qr_ticket:
                print ('二维码登陆失败')
                return False

            # step 4: validate scan result
            ## must have
            self.headers['Host'] = 'passport.jd.com'
            self.headers['Referer'] = 'https://passport.jd.com/uc/login?ltype=logout'
            resp = self.sess.get(
                urls[3],
                headers = self.headers,
                cookies = self.cookies,
                params = {'t' : qr_ticket },
            )
            if resp.status_code != requests.codes.OK:
                print ('二维码登陆校验失败: {}'.format(resp.status_code))
                return False

            ## 京东有时候会认为当前登录有危险，需要手动验证
            ## url: https://safe.jd.com/dangerousVerify/index.action?username=...
            res = json.loads(resp.text)
            if not resp.headers.get('P3P'):
                if res.has_key('url'):
                    print ('需要手动安全验证: {0}'.format(res['url']))
                    return False
                else:
                    print_json(res)
                    print ('登陆失败!!')
                    return False

            ## login succeed
            self.headers['P3P'] = resp.headers.get('P3P')
            for k, v in resp.cookies.items():
                self.cookies[k] = v

            with open('cookie', 'wb') as f:
                pickle.dump(self.cookies, f)

            print ('登陆成功')
            return True

        except Exception as e:
            print ('Exp:{}'.format(e))
            raise

        return False

