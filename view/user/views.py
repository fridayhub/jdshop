#!/usr/bin/env python3
# -*-coding:utf-8 -*-
from . import user
from flask import render_template, redirect, session, url_for, flash, request
from view.user.forms import AddTaskForm, LoginForm, RegisterForm, PwdForm, UserInfoForm
from view.models import Torder, Tuser, Tpassword, TuserLoginLog, Tprovince, Tcity, Tarea, Ttown
import time
from werkzeug.security import generate_password_hash
from functools import wraps
from view import db, app
from view import hlog
import random
import requests
import json
import pickle

logger = hlog.get_hlog(__name__, app.config["LOG_DIR"], 'web')


# 登录装饰器
def user_login_req(func):
    logger.debug("start.....")

    @wraps(func)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('user.login', next=request.url))
        logger.debug("end.....")
        return func(*args, **kwargs)

    logger.debug("end.....")
    return decorated_function


# login
@user.route('/login/', methods=['GET', 'POST'])
def login():
    logger.debug("start.....")
    form = LoginForm()
    if form.validate_on_submit():
        data = form.data
        user = Tuser.query.filter_by(Huser_name=data['name']).first()
        logger.debug('quer user result:{}'.format(user))
        if user:
            passwd = Tpassword.query.filter_by(Huser_id=user.Huser_id).first()
            if not passwd.check_pwd(data['pwd']):
                flash('密码错误！', 'err')
                return redirect(url_for('user.login'))
        else:
            flash('账户不存在!', 'err')
            return redirect(url_for('user.login'))
        # save session
        session['user'] = user.Huser_name
        session['user_id'] = user.Huser_id

        userlog = TuserLoginLog(
            Huser_id=user.Huser_id,
            Hlogin_ip=request.remote_addr
        )
        db.session.add(userlog)
        db.session.commit()
        logger.debug("end.....")
        return redirect(url_for('user.task_list', page=1))
    logger.debug("end.....")
    return render_template('user/login.html', form=form)


@user.route('/logout/')
def logout():
    logger.debug("start.....")
    session.pop('user', None)
    session.pop('user_id', None)
    logger.debug("end.....")
    return redirect(url_for('user.login'))


# user regist
@user.route('/regist/', methods=['GET', 'POST'])
def regist():
    logger.debug("start.....")
    form = RegisterForm()
    if form.validate_on_submit():
        data = form.data
        user_count = Tuser.query.count()
        user_id = user_count + 1
        user = Tuser(
            Huser_id=user_id,
            Huser_name=data['name'],
            Hstate=1,
            Hemail=data['email'],
            Hmobile=data['phone']
        )
        db.session.add(user)
        passwd = Tpassword(
            Huser_id=user_id,
            Hpassword=generate_password_hash(data['pwd'])
        )
        db.session.add(passwd)

        db.session.commit()
        flash('注册成功 请登录', 'ok')
        logger.debug("end.....")
        return redirect(url_for('user.login'))
    logger.debug("end.....")
    return render_template('user/regist.html', form=form)


@user.route('/')
@user_login_req
def index():
    logger.debug("start.....")
    return render_template('user/index.html')


@user.route('/user_info/', methods=['GET', 'POST'])
@user_login_req
def user_info():
    form = UserInfoForm()
    user = Tuser.query.get(session['user_id'])
    if request.method == 'GET':  # 自动填入注册时，保存到数据库中数据
        form.name.data = user.Huser_name
        form.email.data = user.Hemail
        form.phone.data = user.Hmobile
        address = ''
        if user.Haddress:
            addr = user.Haddress.split('_')
            if addr[0]:
                province = db.session.query(Tprovince.Hprovince_name).filter(
                    Tprovince.Hprovince_id == addr[0]
                ).one()
                address = province[0]
            if addr[1]:
                city = db.session.query(Tcity.Hcity_name).filter(
                    Tcity.Hcity_id == addr[1]
                ).one()
                address += ' ' + city[0]
            if int(addr[2]) > 0:
                area = db.session.query(Tarea.Harea_name).filter(
                    Tarea.Harea_id == addr[2]
                ).one()
                address += ' ' + area[0]
            if int(addr[3]) > 0:
                town = db.session.query(Ttown.Htown_name).filter(
                    Ttown.Htown_id == addr[3]
                ).one()
                address += ' ' + town[0]
            form.show_area.data = address
    if form.validate_on_submit():
        data = form.data
        name_count = Tuser.query.filter_by(Huser_name=data['name']).count()
        if data['name'] != user.Huser_name and name_count == 1:
            flash("昵称已经存在!", "err")
            return redirect(url_for("user.user_info"))

        email_count = Tuser.query.filter_by(Hemail=data["email"]).count()
        if data["email"] != user.Hemail and email_count == 1:
            flash("邮箱已经存在!", "err")
            return redirect(url_for("user.user_info"))

        phone_count = Tuser.query.filter_by(Hmobile=data["phone"]).count()
        if data["phone"] != user.Hmobile and phone_count == 1:
            flash("手机已经存在!", "err")
            return redirect(url_for("user.user_info"))

        # 保存
        user.Huser_name = data["name"]
        user.Hemail = data["email"]
        user.Hmobile = data["phone"]
        user.Haddress = data["area"]
        db.session.add(user)
        db.session.commit()

        flash("修改成功!", "ok")
        return redirect(url_for("user.user_info"))
    return render_template('user/user.html', form=form, user=user)


@user.route('/area_get/', methods=['GET'])
@user_login_req
def area_get():
    req_type = request.args.get('req_type', '')
    req_code = request.args.get('req_code', '')
    if req_type == '1':  # province
        ret_data = db.session.query(Tprovince.Hprovince_id, Tprovince.Hprovince_name).all()
    elif req_type == '2':  # city
        ret_data = db.session.query(Tcity.Hcity_id, Tcity.Hcity_name).filter(
            Tcity.Hprovince_id == req_code
        ).all()
    elif req_type == '3':  # area
        ret_data = db.session.query(Tarea.Harea_id, Tarea.Harea_name).filter(
            Tarea.Hcity_id == req_code
        ).all()
    elif req_type == '4':  # town
        ret_data = db.session.query(Ttown.Htown_id, Ttown.Htown_name).filter(
            Ttown.Harea_id == req_code
        ).all()
    else:
        ret_data = ''

    return json.dumps(ret_data)


@user.route('/task/add', methods=['GET', 'POST'])
@user_login_req
def task_add():
    logger.debug("start.....")
    form = AddTaskForm()
    if form.validate_on_submit():
        data = form.data
        userid = str(session['user_id']).zfill(4)
        order_number = "{0}{1}{2}".format(time.strftime('%Y%m%d%H%M%S', time.localtime(time.time())), userid,
                                          ''.join(str(random.choice(range(10))) for _ in range(4)))
        order = Torder(
            Horder_number=order_number,
            Huser_id=session['user_id'],
            Hgoods_id=data['goods_id'],
            Hgoods_name=data['goods_name'],
            Hgoods_channel=int(data['goods_channel']),
            Hbuy_type=int(data['buy_type']),
            Hbuy_time=int(time.mktime(time.strptime(data['buy_time'], '%Y-%m-%d %H:%M:%S'))),
            Horiginal_price=float(data['original_price']) * 100,
            Hbuy_price=float(data['buy_price']) * 100,
            Horder_state=1
        )
        db.session.add(order)
        db.session.commit()
        flash("订单添加成功", "ok")
        logger.debug("end.....")
        return redirect(url_for("user.task_add"))
    logger.debug("end.....")
    return render_template('user/task_add.html', form=form)


@user.route('/task/edit/<order_number>', methods=['GET', 'POST'])
@user_login_req
def task_edit(order_number):
    logger.debug("start.....")
    order = Torder.query.filter_by(
        Horder_number=order_number
    ).first_or_404()
    form = AddTaskForm()
    if request.method == 'GET':  # 自动填入注册时，保存到数据库中数据
        form.goods_id.data = order.Hgoods_id
        form.goods_name.data = order.Hgoods_name
        form.goods_channel.data = order.Hgoods_channel
        form.buy_type.data = order.Hbuy_type
        form.original_price.data = round(order.Horiginal_price/100, 2)
        form.buy_price.data = round(order.Hbuy_price/100, 2)
        temp_time = time.localtime(order.Hbuy_time)
        form.buy_time.data = time.strftime("%Y-%m-%d %H:%M:%S", temp_time)
    if form.validate_on_submit():
        data = form.data

        order.Horder_number=order_number,
        order.Huser_id=session['user_id'],
        order.Hgoods_id=data['goods_id'],
        order.Hgoods_name=data['goods_name'],
        order.Hgoods_channel=int(data['goods_channel']),
        order.Hbuy_type=int(data['buy_type']),
        order.Hbuy_time=int(time.mktime(time.strptime(data['buy_time'], '%Y-%m-%d %H:%M:%S'))),
        order.Horiginal_price=float(data['original_price']) * 100,
        order.Hbuy_price=float(data['buy_price']) * 100,
        order.Horder_state=1
        db.session.add(order)
        db.session.commit()
        flash("订单修改成功", "ok")
        logger.debug("end.....")
        return redirect(url_for("user.task_list", page=1))

    logger.debug("end.....")
    return render_template('user/task_edit.html', form=form)


@user.route('/task/list/<int:page>', methods=['GET'])
@user_login_req
def task_list(page=None):
    logger.debug("start.....")
    if page is None:
        page = 1
    page_data = Torder.query.filter_by(
        Huser_id=int(session['user_id'])
    ).order_by(
        Torder.Hcreate_time.desc()
    ).paginate(page=page, per_page=10)
    logger.debug("end.....")
    return render_template('user/task_list.html', page_data=page_data)

@user.route('/task/del/<order_number>', methods=['GET'])
@user_login_req
def task_del(order_number):
    logger.debug("start.....")
    if order_number:
        order = Torder.query.filter_by(
            Horder_number=order_number
        ).first_or_404()
        db.session.delete(order)
        db.session.commit()
        flash("订单删除成功", "ok")
    logger.debug("end.....")
    return render_template(url_for("user.task_list", page=1))

# pwd change
@user.route('/pwd/', methods=['GET', 'POST'])
@user_login_req
def pwd():
    logger.debug("start.....")
    form = PwdForm()
    if form.validate_on_submit():
        data = form.data
        user = Tpassword.query.filter_by(name=session["user"]).first()
        if not user.check_pwd(data['old_pwd']):
            flash('旧密码错误!', 'err')
            return redirect(url_for('home.pwd'))

        user.pwd = generate_password_hash(data["new_pwd"])
        db.session.add(user)
        db.session.commit()
        flash("密码修改成功,请重新登录", "ok")
        logger.debug("end.....")
        return redirect(url_for("user.logout"))
    logger.debug("end.....")
    return render_template("user/pwd.html", form=form)


# jd taobao login
@user.route('/shoppingLogin/', methods=['GET'])
@user_login_req
def shopping_login():
    logger.debug("start.....")
    qr_code_pic = 'qr_code_{}.png'.format(session['user_id'])
    cmd = 'rm -f {}'.format(app.config["QR_DIR"] + qr_code_pic)
    import os
    os.system(cmd)
    logger.debug("end.....")
    return render_template('user/shopping_login.html', qr_code_pic=qr_code_pic)


# jd taobao login
@user.route('/jdLogin/', methods=['GET'])
@user_login_req
def jd_login():
    logger.debug("start.....")
    sess = requests.Session()
    data = dict(ok=0)
    cookies = {

    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36',
        'ContentType': 'text/html; charset=utf-8',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Connection': 'keep-alive',
    }

    print(u'{0} > 请打开京东手机客户端，准备扫码登陆:'.format(time.ctime()))

    urls = (
        'https://passport.jd.com/new/login.aspx',
        'https://qr.m.jd.com/show',
        'https://qr.m.jd.com/check',
        'https://passport.jd.com/uc/qrCodeTicketValidation'
    )

    # step 1: open login page
    resp = sess.get(
        urls[0],
        headers=headers
    )
    if resp.status_code != requests.codes.OK:
        # print('获取登录页失败: {}'.format(resp.status_code))
        flash("获取登录页失败", "err")
        return json.dumps(data)

    ## save cookies
    for k, v in resp.cookies.items():
        cookies[k] = v

    # step 2: get QR image
    resp = sess.get(
        urls[1],
        headers=headers,
        cookies=cookies,
        params={
            'appid': 133,
            'size': 147,
            't': (int)(time.time() * 1000)
        }
    )
    if resp.status_code != requests.codes.OK:
        # print('获取二维码失败: {}'.format(resp.status_code))
        flash("获取二维码失败", "err")
        return json.dumps(data)

    ## save cookies
    for k, v in resp.cookies.items():
        cookies[k] = v

    ## save QR code
    image_file = 'qr_code_{}.png'.format(session['user_id'])
    with open(app.config["QR_DIR"] + image_file, 'wb') as f:
        for chunk in resp.iter_content(chunk_size=1024):
            f.write(chunk)

    # step 3: check scan result
    ## mush have
    headers['Host'] = 'qr.m.jd.com'
    headers['Referer'] = 'https://passport.jd.com/new/login.aspx'

    # check if QR code scanned
    qr_ticket = None
    retry_times = 60
    while retry_times:
        retry_times -= 1
        resp = sess.get(
            urls[2],
            headers=headers,
            cookies=cookies,
            params={
                'callback': 'jQuery%u' % random.randint(1000000, 9999999),
                'appid': 133,
                'token': cookies['wlfstk_smdl'],
                '_': (int)(time.time() * 1000)
            }
        )
        print('checking...')
        print('QRCodeKey:{},wlfstk_smdl:{}'.format(cookies['QRCodeKey'], cookies['wlfstk_smdl']))
        time.sleep(3)

        if resp.status_code != requests.codes.OK:
            continue

        n1 = resp.text.find('(')
        n2 = resp.text.find(')')
        rs = json.loads(resp.text[n1 + 1:n2])

        if rs['code'] == 200:
            print('{} : {}'.format(rs['code'], rs['ticket']))
            qr_ticket = rs['ticket']
            break
        else:
            print('{} : {}'.format(rs['code'], rs['msg']))
            time.sleep(3)

    if not qr_ticket:
        return json.dumps(data)

    # step 4: validate scan result
    ## must have
    headers['Host'] = 'passport.jd.com'
    headers['Referer'] = 'https://passport.jd.com/uc/login?ltype=logout'
    resp = sess.get(
        urls[3],
        headers=headers,
        cookies=cookies,
        params={'t': qr_ticket},
    )
    if resp.status_code != requests.codes.OK:
        # print('二维码登陆校验失败: {}'.format(resp.status_code))
        return json.dumps(data)

    ## 京东有时候会认为当前登录有危险，需要手动验证
    ## url: https://safe.jd.com/dangerousVerify/index.action?username=...
    res = json.loads(resp.text)
    if not resp.headers.get('P3P'):
        if 'url' in resp:
            # print('需要手动安全验证: {0}'.format(res['url']))
            return json.dumps(data)
        else:
            # print_json(res)
            return json.dumps(data)

    ## login succeed
    headers['P3P'] = resp.headers.get('P3P')
    for k, v in resp.cookies.items():
        cookies[k] = v

    save_cookie = Tpassword.query.filter_by(Huser_id=session['user_id']).first_or_404()
    cookies = pickle.dumps(cookies)
    from base64 import b64encode
    b64_data = b64encode(cookies)
    save_cookie.Hjdpassword = str(b64_data, 'utf-8')
    db.session.add(save_cookie)
    db.session.commit()

    print('登陆成功')
    data = dict(ok=1)
    logger.debug("end.....")
    return json.dumps(data)
