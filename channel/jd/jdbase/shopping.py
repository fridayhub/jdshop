#!/usr/bin/env python3
# -*-coding:utf-8 -*-

import requests
import pickle
import json
import sys
import time
import bs4
import random
import re

sys.path.append('../../')
from view.models import Tpassword, Torder
from channel import db
from channel.jd.jd import logger

from view import hlog

# get function name
FileName = lambda n=0: sys._getframe(n + 1).f_code.co_filename
FuncName = lambda n=0: sys._getframe(n + 1).f_code.co_name
LineNum = lambda n=0: sys._getframe(n + 1).f_lineno


# logger = hlog.get_hlog(__name__, '../../../log/', 'jd')

def tags_val(tag, key='', index=0):
    '''
    return html tag list attribute @key @index
    if @key is empty, return tag content
    '''
    if len(tag) == 0 or len(tag) <= index:
        return ''
    elif key:
        txt = tag[index].get(key)
        return txt.strip(' \t\r\n') if txt else ''
    else:
        txt = tag[index].text
        return txt.strip(' \t\r\n') if txt else ''


def tag_val(tag, key=''):
    '''
    return html tag attribute @key
    if @key is empty, return tag content
    '''
    if tag is None:
        return ''
    elif key:
        txt = tag.get(key)
        return txt.strip(' \t\r\n') if txt else ''
    else:
        txt = tag.text
        return txt.strip(' \t\r\n') if txt else ''


def letter_number(flag, n):
    a = []
    for x in range(97, 123):
        a.append(chr(x))

    b = []
    for x in range(65, 91):
        b.append(chr(x))

    c = []
    for x in range(48, 58):
        c.append(chr(x))

    ret = []
    if flag:
        # catital & number
        for i in range(n):
            ret.append(random.choice(b + c))
    else:
        # lower & number
        for i in range(n):
            ret.append(random.choice(a + c))

    return ''.join(ret)


class jdShopping(object):
    def __init__(self, good=None, area='19_1607_47388_0'):

        logger.debug('login.................')
        from base64 import b64decode
        b64_data = b64decode(good[3])
        cookie = pickle.loads(b64_data)
        # logger.debug('cookie:[{}]'.format(cookie))

        self.sess = requests.session()

        self.cookies = requests.utils.cookiejar_from_dict(cookie)
        self.sess.cookies = self.cookies

        # self.cookies = ', '.join([': '.join((k, str(cookie[k]))) for k in sorted(cookie, key=cookie.get)])
        # logger.debug('cookie:[{}]'.format(self.cookies))

        self.header = {
            'Accept': '* / *',
            'Accept - Encoding': 'gzip, deflate, br',
            'Accept - Language': 'en - US, en;q = 0.9, zh - CN;q = 0.8, zh;q = 0.7',
            'Connection': 'keep - alive',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) \
            Chrome/64.0.3282.186 Safari/537.36',
            'Referer': 'https://www.jd.com/',
            'Host': 'passport.jd.com'
        }
        logger.debug(self.header)

        self.sess.headers = self.header

        self.good_id = good[1]
        self.area_id = area
        self.count = '1'
        self.wait = 500  # ms
        self.flush = 1
        self.submit = True
        self.cat = ''
        self.trackid = ''

    @staticmethod
    def response_status(resp):
        logger.debug('star...')
        if resp.status_code != requests.codes.OK:
            logger.debug('Status: {}, Url: {}'.format(resp.status_code, resp.url))
            return False
        return True

    def get_user_info(self):
        # check user info
        url = 'https://passport.jd.com/user/petName/getUserInfoForMiniJd.action?callback=' \
              'jQuery3518704&_=1532055599882&_=' + str(int(time.time()))

        temp_header = {'Host': 'passport.jd.com', 'Referer': 'https://www.jd.com/'}
        self.sess.headers.update(temp_header)

        ret = self.sess.get(url)
        self.sess.headers.pop('Host')
        self.sess.headers.pop('Referer')
        ret.encoding = 'gbk'
        print(ret.text)

    def check_login(self):
        logger.debug('star...')
        logger.debug('fucking headers:{}'.format(self.sess.headers))
        # checkUrl = 'https://passport.jd.com/uc/qrCodeTicketValidation'
        # check_url = 'https://passport.jd.com/loginservice.aspx'
        check_url = 'https://passport.jd.com/loginservice.aspx?callback=jQuery3781961&' \
                    'method=Login&_=' + str(int(time.time()))
        payloads = {
            'method': 'Login',
            'callback': 'jsonpLogin',
            '_:': (int)(time.time() * 1000)
        }
        try:
            logger.debug('++++++++++++++++++++++{},{}+++++++++++++++++++++++++++++++++'.format(FuncName(), LineNum()))
            logger.debug('{0} > check login status... '.format(time.ctime()))

            resp = self.sess.get(check_url, params=payloads)

            text = resp.text
            text = text.split('(')[1][:-1]
            text = json.loads(text)
            logger.debug(text)
            self.sess.headers.pop('Host')
            self.sess.headers.pop('Referer')
            return text['Identity']['IsAuthenticated']
        except Exception as e:
            logger.error(e)
            return False

    # 商品库存
    def good_stock(self, stock_id, cat, area_id=None):
        logger.debug('star...stock_id:{}, cat:{}, area_id:{}'.format(stock_id, cat, area_id))
        '''
        33 : on sale, 
        34 : out of stock
        '''
        # http://ss.jd.com/ss/areaStockState/mget?app=cart_pc&ch=1&skuNum=3180350,1&area=1,72,2799,0
        #   response: {"3180350":{"a":"34","b":"1","c":"-1"}}
        # stock_url = 'http://ss.jd.com/ss/areaStockState/mget'

        # http://c0.3.cn/stocks?callback=jQuery2289454&type=getstocks&skuIds=3133811&area=1_72_2799_0&_=1490694504044
        #   jQuery2289454({"3133811":{"StockState":33,"freshEdi":null,"skuState":1,"PopType":0,"sidDely":"40","channel":1,"StockStateName":"现货","rid":null,"rfg":0,"ArrivalDate":"","IsPurchase":true,"rn":-1}})
        # jsonp or json both work
        try:
            if area_id is None:
                area_id = '1_72_2799_0'
            if not cat:
                temp_cat = random.randint(000, 999)
                cat = '{},{},{}'.format(temp_cat, temp_cat + 1, temp_cat + 2)

            stock_url = 'https://c0.3.cn/stock'
            payload = {
                # 'type': 'getstocks',
                'skuId': stock_id,
                'area': area_id,
                'cat': cat,
                'extraParam': '{"originid":"1"}'
            }
            self.get_user_info()

            logger.debug(stock_url, payload)

            # get stock state
            resp = self.sess.get(stock_url, params=payload)
            if not self.response_status(resp):
                logger.debug('获取商品库存失败')
                return (0, '')

            # return json
            resp.encoding = 'gbk'
            stock_info = json.loads(resp.text)
            stock_stat = int(stock_info['stock']['StockState'])  # 2018.7.19
            stock_stat_name = stock_info['stock']['StockStateName']  # 2018.7.19

            # 33 : on sale, 34 : out of stock, 36: presell
            return stock_stat, stock_stat_name

        except Exception as e:
            logger.error('Stocks Exception:{}'.format(e))
            time.sleep(5)

        return (0, '')

    def good_detail(self, stock_id, area_id=None):
        logger.debug('star...')
        # return good detail
        good_data = {
            'id': stock_id,
            'name': '',
            'link': '',
            'price': '',
            'stock': '',
            'stockName': '',
        }

        try:
            # shop page
            stock_link = 'http://item.jd.com/{0}.html'.format(stock_id)
            resp = self.sess.get(stock_link)
            logger.debug(resp.links)

            # logger.debug(resp.text)
            # good page
            soup = bs4.BeautifulSoup(resp.text, 'html.parser')

            # get cat  2018.7.19
            cat = re.findall(r'cat: \[\d*,\d*,\d*\]', resp.text)[0]
            self.cat = re.findall(r'[[](.*?)[]]', cat)[0]
            logger.debug('get cat:{}'.format(self.cat))

            # good name
            tags = soup.select('div#name h1')
            if len(tags) == 0:
                tags = soup.select('div.sku-name')
            good_data['name'] = tags_val(tags).strip(' \t\r\n')

            # cart link
            tags = soup.select('a#InitCartUrl')
            link = tags_val(tags, key='href')

            if link[:2] == '//':
                link = 'http:' + link
            logger.debug(link)
            good_data['link'] = link

            # good price
            good_data['price'] = self.good_price(self.good_id)

            # good stock 查库存
            good_data['stock'], good_data['stockName'] = self.good_stock(self.good_id, self.cat, self.area_id)
            # stock_str = u'有货' if good_data['stock'] == 33 else u'无货'

        except Exception as e:
            logger.error('Exp {0} : {1}'.format(FuncName(), e))

        logger.debug('++++++++++++++++++++++{},{}+++++++++++++++++++++++++++++++++'.format(FuncName(), LineNum()))
        logger.debug('{0} > 商品详情'.format(time.ctime()))
        logger.debug('编号：{0}'.format(good_data['id']))
        logger.debug('库存：{0}'.format(good_data['stockName']))
        logger.debug('价格：{0}'.format(good_data['price']))
        logger.debug('名称：{0}'.format(good_data['name']))
        logger.debug('购物车链接：{0}'.format(good_data['link']))

        return good_data

    def good_price(self, stock_id):
        logger.debug('star... good_id:{}'.format(stock_id))
        # get good price
        price = '?'
        try:
            url = 'http://p.3.cn/prices/mgets'
            logger.debug(url)
            payload = {
                'type': 1,
                'pduid': int(time.time() * 1000),
                'skuIds': 'J_' + str(stock_id),
                'area': self.area_id
            }
            logger.debug(payload)

            resp = self.sess.get(url, params=payload)
            logger.debug(resp.links)
            resp_txt = resp.text.strip()
            logger.debug(resp_txt)

            js = json.loads(resp_txt[1:-1])
            logger.debug('价格 P: {0}, M: {1}'.format(js['p'], js['m']))
            price = js.get('p')
            return price
        except Exception as e:
            logger.error('Exp {0} : {1}'.format(FuncName(), e))

    def buy(self):
        logger.debug('star...')
        # stock detail 编号 库存 价格  名称  购物车链接
        good_data = self.good_detail(self.good_id, self.area_id)

        # retry until stock not empty
        if good_data['stock'] != 33:
            # flush stock state
            while good_data['stock'] != 33 and self.flush:
                logger.debug('<%s> <%s>' % (good_data['stockName'], good_data['name']))
                time.sleep(self.wait / 1000.0)
                good_data['stock'], good_data['stockName'] = self.good_stock(self.good_id, self.cat, self.area_id)

            # retry detail
            # good_data = self.good_detail(options.good)

        # failed
        link = good_data['link']
        if good_data['stock'] != 33 or link == '':
            logger.error('stock {0}, link {1}'.format(good_data['stock'], link))
            return False

        try:
            # change buy count
            if self.count != 1:
                link = link.replace('pcount=1', 'pcount={0}'.format(self.count))

            # add to cart
            logger.debug(link)
            up_header = {'upgrade-insecure-requests': '1',
                         'referer': 'https://item.jd.com/' + str(self.good_id) + '.html'}
            self.sess.headers.update(up_header)
            resp = self.sess.get(link)
            self.sess.headers.pop('upgrade-insecure-requests')
            self.sess.headers.pop('referer')

            soup = bs4.BeautifulSoup(resp.text, "html.parser")

            # tag if add to cart succeed
            tag = soup.select('h3.ftx-02')
            if tag is None:
                tag = soup.select('div.p-name a')

            if tag is None or len(tag) == 0:
                logger.debug('添加到购物车失败')
                return False
            # addtocart = "https://cart.jd.com/addToCart.html?rcd=1&pid={}&pc=1&eb=1&rid=1519824303032&em=".format(options.good)
            # resp = self.sess.get(addtocart, cookies=self.cookies, headers=self.headers)
            # logger.debug(resp.text)
            logger.debug('+++++++++++++++++++++++++++++++++++++++++++++++++++++++')
            logger.debug('{0} > 购买详情'.format(time.ctime()))
            logger.debug('链接：{0}'.format(link))
            logger.debug('结果：{0}'.format(tags_val(tag)))

            # change count after add to shopping cart
            # self.buy_good_count(options.good, options.count)

        except Exception as e:
            logger.error('Exp {0} : {1}'.format(FuncName(), e))
        else:
            self.cart_detail()
            return self.order_info(self.submit)

        return False

    def buy_good_count(self, good_id, count):
        logger.debug('star...')
        url = 'http://cart.jd.com/changeNum.action'

        payload = {
            'venderId': '8888',
            'pid': good_id,
            'pcount': count,
            'ptype': '1',
            'targetId': '0',
            'promoID': '0',
            'outSkus': '',
            'random': random.random(),
            'locationId': '19_1607_3155_0',  # need changed to your area location id
        }

        try:
            rs = self.sess.post(url, params=payload)
            if rs.status_code == 200:
                js = json.loads(rs.text)
                if js.get('pcount'):
                    logger.debug('数量：%s @ %s' % (js['pcount'], js['pid']))
                    return True
            else:
                logger.error('购买 %d 失败' % count)

        except Exception as e:
            logger.error('Exp {0} : {1}'.format(FuncName(), e))

        return False

    def cart_detail(self):
        logger.debug('star...')
        # list all goods detail in cart
        cart_url = 'https://cart.jd.com/cart.action'
        cart_header = u'购买    数量    价格        总价        商品'
        cart_format = u'{0:8}{1:8}{2:12}{3:12}{4}'

        try:
            resp = self.sess.get(cart_url)
            resp.encoding = 'utf-8'
            soup = bs4.BeautifulSoup(resp.text, "html.parser")

            logger.debug('++++++++++++++++++++++{},{}+++++++++++++++++++++++++++++++++'.format(FuncName(), LineNum()))
            logger.debug('{0} > 购物车明细'.format(time.ctime()))
            logger.debug(cart_header)

            for item in soup.select('div.item-form'):
                check = tags_val(item.select('div.cart-checkbox input'), key='checked')
                check = ' + ' if check else ' - '
                count = tags_val(item.select('div.quantity-form input'), key='value')
                price = tags_val(item.select('div.p-price strong'))
                sums = tags_val(item.select('div.p-sum strong'))
                gname = tags_val(item.select('div.p-name a'))
                #: ￥字符解析出错, 输出忽略￥
                logger.debug(cart_format.format(check, count, price[1:], sums[1:], gname))

            t_count = tags_val(soup.select('div.amount-sum em'))
            t_value = tags_val(soup.select('span.sumPrice em'))
            logger.debug('总数: {0}'.format(t_count))
            logger.debug('总额: {0}'.format(t_value[1:]))

        except Exception as e:
            logger.error('Exp {0} : {1}'.format(FuncName(), e))

    def order_info(self, submit=False):
        logger.debug('star...')
        # get order info detail, and submit order
        logger.debug('++++++++++++++++++++++{},{}+++++++++++++++++++++++++++++++++'.format(FuncName(), LineNum()))
        logger.debug('{0} > 订单详情'.format(time.ctime()))

        try:
            order_url = 'http://trade.jd.com/shopping/order/getOrderInfo.action'
            payload = {
                'rid': str(int(time.time() * 1000)),
            }

            # get preorder page
            rs = self.sess.get(order_url, params=payload)
            soup = bs4.BeautifulSoup(rs.text, "html.parser")

            # order summary
            payment = tag_val(soup.find(id='sumPayPriceId'))
            detail = soup.find(class_='fc-consignee-info')

            if detail:
                snd_usr = tag_val(detail.find(id='sendMobile'))
                snd_add = tag_val(detail.find(id='sendAddr'))

                logger.debug('应付款：{0}'.format(payment))
                logger.debug(snd_usr)
                logger.debug(snd_add)

            # just test, not real order
            if not submit:
                return False
            logger.debug('submit order set payload begin')
            # order info
            skcontrol = letter_number(True, 80)
            trackid = letter_number(False, 32)
            payload = {
                'overseaPurchaseCookies': '',
                'vendorRemarks': '[{"venderId": "{' + str(self.good_id) + '}", "remark": ""}]',
                'submitOrderParam.btSupport': '1',
                'submitOrderParam.ignorePriceChange': '0',
                'submitOrderParam.sopNotPutInvoice': 'true',  # 发票
                'submitOrderParam.trackID': 'TestTrackId',
                'skControl': skcontrol,
                'submitOrderParam.jxj': '1',
                'submitOrderParam.trackId': trackid
            }

            order_url = 'http://trade.jd.com/shopping/order/submitOrder.action'
            logger.debug('send submit order begin')
            temp_header = {
                'Host': 'trade.jd.com',
                'Origin': 'https://trade.jd.com',
                'Referer': 'https://trade.jd.com/shopping/order/getOrderInfo.action?rid={}'.format(
                    str(int(time.time()) - 10)),
                'Content - Type': 'application / x - www - form - urlencoded',
                'X - Requested - With': 'XMLHttpRequest'
            }
            self.sess.headers.update(temp_header)
            rp = self.sess.post(order_url, params=payload)

            if rp.status_code == 200:
                logger.debug(rp.text)

                js = json.loads(rp.text)
                if js['success']:
                    logger.debug('下单成功！订单号：{0}'.format(js['orderId']))
                    logger.debug('请前往东京官方商城付款')
                    return True
                else:
                    logger.error('下单失败！<{0}: {1}>'.format(js['resultCode'], js['message']))
                    if js['resultCode'] == '60017':
                        # 60017: 您多次提交过快，请稍后再试
                        time.sleep(1)
            else:
                logger.error('请求失败. StatusCode:{}'.format(rp.status_code))

        except Exception as e:
            logger.error('Exp {0} : {1}'.format(FuncName(), e))

        return False
