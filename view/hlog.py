#!/usr/bin/env python3
# -*-coding:utf-8 -*-

import logging
import time
import os
from view import app


def get_hlog(name, log_dir, prefix):
    # 第一步，创建一个logger
    logger = logging.getLogger(name)
    if os.path.exists(log_dir):
        pass
    else:
        os.mkdir(log_dir)
    logger.setLevel(logging.DEBUG)  # Log等级总开关
    # 第二步，创建一个handler，用于写入日志文件
    rq = time.strftime('%Y%m%d', time.localtime(time.time()))
    log_path = os.path.dirname(log_dir)
    log_name = log_path + '/' + prefix + rq + '.log'
    file_handler = logging.FileHandler(log_name, mode='a')  ##模式，有w和a，w就是写模式，每次都会重新写日志，覆盖之前的日志
    # a是追加模式，默认如果不写的话，就是追加模式
    file_handler.setLevel(logging.DEBUG)  # 输出到file的log等级的开关
    # 第三步，定义handler的输出格式
    formatter = logging.Formatter(
        "[%(asctime)s]-[%(process)d]-[%(filename)s:%(lineno)d]-[%(funcName)s]-%(levelname)s:%(message)s",
        "%Y%m%d-%H:%M:%S")
    file_handler.setFormatter(formatter)
    # 第四步，将logger添加到handler里面
    logger.addHandler(file_handler)
    return logger
