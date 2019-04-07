#!/usr/bin/env python3
# -*-coding:utf-8 -*-
from flask_sqlalchemy import SQLAlchemy
from flask import Flask

app = Flask(__name__)

# 用于连接数据的数据库。
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:hang1234@localhost/shop"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config["SQLALCHEMY_ECHO"] = True  # 打印sql语句

db = SQLAlchemy(app)


