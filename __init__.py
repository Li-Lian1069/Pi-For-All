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
    flask
    
    toml - 储存配置
'''
DEBUG = False

import os,sys,flask,toml
from appApi import APPSDK
APP = APPSDK ('main')
os.chdir(APP.getFileDir(__file__)) # 工作目录更改目录至脚本所在路径
_SEP = os.sep
 
loger = APP.create_loger ()
loger.info ('The program is now running.')
cfg = APP.get_cfg_file ('config.toml')
# 主程序注册

# =======载入插件=======
import webService # Web 服务必须最高优先级
@webService.app.route ('/pulgMg/check_app_statu/name=<name>')
def check_app_statu (name):
    try:
        return 'Hi'
    except Exception as e :
        loger.error (f'pulgMg check app status fiald : {repr (e)}')

# ↑ web 服务器
loger.info ('The webService is already imported.')


import plugManger
plugManger.load_apps ()
# ↑ 加载完毕


webService.run (host=cfg.get('host',default='localhost'),
port=cfg.get('port',default='80'),
debug=True)
