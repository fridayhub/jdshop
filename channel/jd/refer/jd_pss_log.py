# -*- coding: UTF-8 -*-
import json
import requests
import sys
import os
import pickle
from selenium import webdriver

from bs4 import BeautifulSoup

#other on:
    def _need_auth_code(self, usr_name):
        print(FuncName(), LineNum())
        # check if need auth code
        #
        auth_dat = {
            'loginName': usr_name,
        }
        payload = {
            'r' : random.random(),
            'version' : 2015
        }

        resp = self.sess.post(self.auth, data=auth_dat, params=payload)
        if self.response_status(resp) :
            js = json.loads(resp.text[1:-1])
            return js['verifycode']

        print ('获取是否需要验证码失败')
        return False

    def _get_auth_code(self, uuid):
        print(FuncName(), LineNum())
        # image save path
        image_file = os.path.join(os.getcwd(), 'authcode.jfif')

        payload = {
            'a' : 1,
            'acid' : uuid,
            'uid' : uuid,
            'yys' : str(int(time.time() * 1000)),
        }

        # get auth code
        r = self.sess.get(self.imag, params=payload)
        if not self.response_status(r):
            print ('获取验证码失败')
            return False

        with open (image_file, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                f.write(chunk)

            f.close()

        os.system('start ' + image_file)
        return str(raw_input('Auth Code: '))

    def _login_once(self, login_data):
        print(FuncName(), LineNum())
        # url parameter
        payload = {
            'r': random.random(),
            'uuid' : login_data['uuid'],
            'version' : 2015,
        }

        resp = self.sess.post(self.login, data=login_data, params=payload)
        if self.response_status(resp):
            js = json.loads(resp.text[1:-1])
            #self.print_json(resp.text)

            if not js.get('success') :
                print (js.get('emptyAuthcode'))
                return False
            else:
                return True

        return False

    def _login_try(self):
        print(FuncName(), LineNum())
        """ login by username and password, but not working now.
        
        .. deprecated::
            Use `login_by_QR`
        """
        # get login page
        #resp = self.sess.get(self.home)
        print ('++++++++++++++++++++++{},{}+++++++++++++++++++++++++++++++++'.format(FuncName(), LineNum()))
        print ('{0} > 登陆'.format(time.ctime()))

        try:
            # 2016/09/17 PhantomJS can't login anymore
            self.browser.get(self.home)
            soup = bs4.BeautifulSoup(self.browser.page_source, "html.parser")

            # set cookies from PhantomJS
            for cookie in self.browser.get_cookies():
                self.sess.cookies[cookie['name']] = str(cookie['value'])

            #for (k, v) in self.sess.cookies.items():
            #    print '%s: %s' % (k, v)

            # response data hidden input == 9 ??. Changed
            inputs = soup.select('form#formlogin input[type=hidden]')
            rand_name = inputs[-1]['name']
            rand_data = inputs[-1]['value']
            token = ''

            for idx in range(len(inputs) - 1):
                id = inputs[idx]['id']
                va = inputs[idx]['value']
                if   id == 'token':
                    token = va
                elif id == 'uuid':
                    self.uuid = va
                elif id == 'eid':
                    self.eid = va
                elif id == 'sessionId':
                    self.fp = va

            auth_code = ''
            if self.need_auth_code(self.usr_name):
                auth_code = self.get_auth_code(self.uuid)
            else:
                print ('无验证码登陆')

            login_data = {
                '_t': token,
                'authcode': auth_code,
                'chkRememberMe': 'on',
                'loginType': 'f',
                'uuid': self.uuid,
                'eid': self.eid,
                'fp': self.fp,
                'nloginpwd': self.usr_pwd,
                'loginname': self.usr_name,
                'loginpwd': self.usr_pwd,
                rand_name : rand_data,
            }

            login_succeed = self.login_once(login_data)
            if login_succeed:
                self.trackid = self.sess.cookies['TrackID']
                print ('登陆成功 {}'.format(self.usr_name))
            else:
                print ('登陆失败 {}'.format(self.usr_name))

            return login_succeed

        except Exception as e:
            print ('Exception:{}'.format(e.message))
            raise
        finally:
            self.browser.quit()

        return False
#=======================================================================

class JD:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:56.0) Gecko/20100101 Firefox/56.0',
            'Referer': 'https://www.jd.com/'
        }
        self.sess = requests.Session()
        self.cookies = {

        }

    def get_login_data(self):
        url = 'https://passport.jd.com/new/login.aspx'
        resp = self.sess.get(url, headers=self.headers)
        driver = webdriver.PhantomJS()
        driver.get('url')
        html =  driver.page_source
        soup = BeautifulSoup(html, 'lxml')
        display = soup.select('#o-authcode')[0].get('style')
        auth_code = ''
        if not display:
            print('需要验证码。。。')
            auth_code_url = soup.select('#JD_Verification1')[0].get('src2')
            print(auth_code_url)
            auth_code = self.get_auth_img(auth_code_url)
        uuid = soup.select('#uuid')[0].get('value')
        eid = soup.select('#eid')[0].get('value')
        fp = soup.select('input[name="fp"]')[0].get('value')  # session id
        _t = soup.select('input[name="_t"]')[0].get('value')  # token
        login_type = soup.select('input[name="loginType"]')[0].get('value')
        pub_key = soup.select('input[name="pubKey"]')[0].get('value')
        sa_token = soup.select('input[name="sa_token"]')[0].get('value')

        data = {
            'uuid': uuid,
            'eid': eid,
            'fp': fp,
            '_t': _t,
            'loginType': login_type,
            'loginname': self.username,
            'nloginpwd': self.password,
            'chkRememberMe': True,
            #'authcode': '',
            'pubKey': pub_key,
            'sa_token': sa_token,
            'authCode': auth_code
        }
        for k,v in data.items():
            print(k,v)
        ## save cookies
        for k, v in resp.cookies.items():
            print(k,v)
            self.cookies[k] = v
        return data

    def get_auth_img(self, url):
        auth_code_url = 'http:' + url
        auth_img = self.sess.get(auth_code_url, headers=self.headers)
        with open(sys.path[0] + '/auth.jpg', 'wb') as f:
            f.write(auth_img.content)
        os.system("eog auth.jpg")
        code = input('请输入验证码：')
        ## save cookies
        for k, v in auth_img.cookies.items():
            self.cookies[k] = v
        return code

    def login(self):
        """
        登录
        :return:
        """
        url = 'https://passport.jd.com/uc/loginService'
        data = self.get_login_data()
        headers = {
            'Referer': 'https://passport.jd.com/uc/login?ltype=logout',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:56.0) Gecko/20100101 Firefox/56.0',
            'X-Requested-With': 'XMLHttpRequest'
        }
        resp= self.sess.post(url, data=data, headers=headers)
        content = resp.text
        print(content)
        result = json.loads(content[1: -1])
        if result.get('success'):
            resp = self.sess.get("https://home.jd.com/", headers=headers)
            for k, v in resp.cookies.items():
                print(k,v)
                self.cookies[k] = v

            with open('cookies', 'wb') as f:
                pickle.dump(self.cookies, f)
            return True
        else:
            return False

    def rush(self):
        print('功能正在赶来的路上，敬请期待。。。')
        pass


def handle():
    print("*************** 菜单列表 **************")
    print('1、抢购')
    print('2、加入购物车')
    num = input('请输入功能编号：')
    if num == '1':
        print('抢购功能正在赶来的路上，敬请期待。。。')
    else:
        print('加入购物车功能正在赶来的路上，敬请期待。。。')
        # print('加入购物车成功！！！')
    pass


username = input('请输入京东账号：')
password = input('请输入京东密码：')
jd = JD(username, password)
if jd.login():
    print('登录成功')
    handle()
else:
    print('登录失败')
