#!/usr/bin/python3
# -*- coding: utf-8 -*-
'''
Pi For All 程序入口
变量命名规则:
|   常量 : 大写_大写
|   变量 : 大驼峰
|   函数 : 小写_小写
|     |  类名 : c_小写_小写

需要的库:
    flask            - web框架
    psutil           - 获取系统资源状态
    toml             - 储存配置
    pywifi           - wifi操作
    comtypes         - pywifi 依赖
'''
DEBUG = False

# =======================
from flask import Flask , redirect , url_for
import os,sys,toml
from appApi import APPSDK
os.chdir (os.path.split(os.path.realpath(__file__))[0]) # 工作目录更改目录至脚本所在路径

SDK = APPSDK ('main',__name__)

loger = SDK.create_loger ()
loger.info ('The program is now running.')
config = SDK.get_cfg_file ('config.toml')
# 主程序注册

# =======载入插件=======

app = Flask (__name__,'')

@app.route ('/')
def index ():
    return redirect ( url_for ('WebPi.index') )

import plugManger
plugManger.load_apps (app)
# ↑ 加载完毕

if __name__ == "__main__":
    # 直接启动脚本时有效
    SERVER_HOST = config.get ('SERVER_HOST',default='localhost')
    SERVER_PORT = config.get ('SERVER_PORT',default='2020')
    DEBUG = config.get ('DEBUG',default=True)
    # 以上参数在反向代理中无效

    app.run (
        SERVER_HOST,
        SERVER_PORT,
        DEBUG
    )
