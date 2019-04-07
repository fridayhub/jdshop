#!/usr/bin/env python3
# -*-coding:utf-8 -*-
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import os
app = Flask(__name__)

# 用于连接数据的数据库。
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:passwd@localhost/shop"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config["SQLALCHEMY_ECHO"] = True  # 打印sql语句

app.config["SECRET_KEY"] = "83323a84cf02478ea7f7b6cb29c2bd4c"
app.config["QR_DIR"] = os.path.join(os.path.abspath(os.path.dirname(__file__)), "static/qr_code/")
app.config["LOG_DIR"] = os.path.join(os.path.abspath(os.path.dirname(__file__)), "log/")

db = SQLAlchemy(app)

from view.user import user as user_blueprint
from view.admin import admin as admin_blueprint

app.register_blueprint(user_blueprint)
app.register_blueprint(admin_blueprint, url_prefix="/admin")


# 404
@app.errorhandler(404)
def page_not_found(error):
    return render_template('user/404.html'), 404
