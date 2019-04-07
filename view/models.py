#!/usr/bin/env python3
# -*-coding:utf-8 -*-

from datetime import datetime
from sqlalchemy import Column, BigInteger, Integer, SmallInteger, String, DateTime, ForeignKey, PickleType
from sqlalchemy.orm import relationship
from view import db

'''
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
app = Flask(__name__)

# 用于连接数据的数据库。
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:passwd@localhost/shop"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config["SQLALCHEMY_ECHO"] = True  # 打印sql语句

db = SQLAlchemy(app)
'''


# order
class Torder(db.Model):
    __tablename__ = 't_order'
    Horder_number = Column(String(22), primary_key=True)  # 订单号
    Huser_id = Column(Integer, ForeignKey('t_password.Huser_id'), ForeignKey('t_user.Huser_id'))
    Hgoods_id = Column(Integer)
    Hgoods_name = Column(String(256))
    Hgoods_channel = Column(SmallInteger)
    Hbuy_type = Column(SmallInteger)
    Hbuy_time = Column(BigInteger)
    Horiginal_price = Column(BigInteger)
    Hbuy_price = Column(BigInteger)
    Horder_state = Column(SmallInteger)
    Hcreate_time = Column(DateTime, index=True, default=datetime.now)
    Hshopping_time = Column(DateTime)

    def __repr__(self):
        return '<Order %r>' % self.Horder_number


# user
class Tuser(db.Model):
    __tablename__ = 't_user'
    Huser_id = Column(Integer, primary_key=True)  # 用户id
    Huser_name = Column(String(100), unique=True)
    Hstate = Column(SmallInteger)
    Hemail = Column(String(100), unique=True)
    Hmobile = Column(String(11), unique=True)
    Hphoto = Column(String(255))
    Haddress = Column(String(32))
    Hcreate_time = Column(DateTime, index=True, default=datetime.now)
    Hmodify_time = Column(DateTime, default=datetime.now)
    Horder = relationship('Torder', backref='t_user')
    Huser_login_log = relationship('TuserLoginLog', backref='t_user')

    def __repr__(self):
        return '<User %r>' % self.Huser_id


class Tpassword(db.Model):
    __tablename__ = 't_password'
    Huser_id = Column(Integer, ForeignKey('t_user.Huser_id'), primary_key=True)
    Hcreate_time = Column(DateTime, index=True, default=datetime.now)
    Hmodify_time = Column(DateTime, default=datetime.now)
    Hpassword = Column(String(128))
    Hjdpassword = Column(String(2048))
    Herror_count = Column(SmallInteger, default=0)
    Hlast_error_time = Column(DateTime)
    t_order = relationship('Torder', backref='t_password')

    def __repr__(self):
        return '<Password %r>' % self.Huser_id

    def check_pwd(self, pwd):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.Hpassword, pwd)


# user login log
class TuserLoginLog(db.Model):
    __tablename__ = 't_user_login_log'
    Hid = Column(Integer, primary_key=True)
    Huser_id = Column(Integer, ForeignKey('t_user.Huser_id'))
    Hlogin_ip = Column(String(64))
    Hcreate_time = Column(DateTime, index=True, default=datetime.now)

    def __repr__(self):
        return '<UserLoginLog %r>' % self.Hid


# province
class Tprovince(db.Model):
    __tablename__ = 't_province'
    Hid = Column(Integer, primary_key=True)
    Hprovince_id = Column(String(8))
    Hprovince_name = Column(String(64))

    def __repr__(self):
        return '<province %r>' % self.Hid


# city
class Tcity(db.Model):
    __tablename__ = 't_city'
    Hid = Column(Integer, primary_key=True)
    Hcity_id = Column(String(8))
    Hcity_name = Column(String(64))
    Hprovince_id = Column(String(8))

    def __repr__(self):
        return '<city %r>' % self.Hid


# city
class Tarea(db.Model):
    __tablename__ = 't_area'
    Hid = Column(Integer, primary_key=True)
    Harea_id = Column(String(8))
    Harea_name = Column(String(64))
    Hcity_id = Column(String(8))

    def __repr__(self):
        return '<area %r>' % self.Hid


# city
class Ttown(db.Model):
    __tablename__ = 't_town'
    Hid = Column(Integer, primary_key=True)
    Htown_id = Column(String(8))
    Htown_name = Column(String(64))
    Harea_id = Column(String(8))

    def __repr__(self):
        return '<town %r>' % self.Hid



'''
if __name__ == '__main__':
    db.create_all()
'''
