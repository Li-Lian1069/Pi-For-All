import sys , os , importlib
from os import path
from flask import Flask , Blueprint
from appApi import APPSDK

SDK = APPSDK ('plugManger',__name__,False)
_loger = SDK.create_loger ()

_APPLIST:dict = SDK.get_cfg_file ('appSettings')
# 使用Config的方式记录 apps

class STATU ():
    UNDEFINED = -1 # 不存在
    DISABLE = 0 # 被禁用
    LOADED = 1 # 已加载且启用
    ERROR = 2 # 加载出错

#{  ↑
#    'appName' : {'isActive':True & False, 'statu' }
#}

app = Blueprint ('plugMg' , __name__)

def load_apps (flaskApp:Flask):
    """
        传入一个flask对象并开始加载插件,将插件中的蓝图注册到app中
    """

    flaskApp.register_blueprint (app) # 将自身注册到 app

    sys.path.append (
        os.path.join (
            os.path.split(os.path.realpath(__file__))[0],
            'apps'
        ))
    # 添加加载环境

    _loger.info ('now start to loading apps')
    for appName in os.listdir ('apps'):
        # 遍历 apps 目录
        if os.path.isdir (os.path.join ('apps',appName)): # 只导入文件夹,并将新加入的APP添加至列表
            if not (appName in _APPLIST): # 如果不在APPLIST中,说明app是新加入的
                _APPLIST[appName] = STATU.LOADED # 设置为已加载
                # 如果 APP 是新的 , 添加至列表

            if _APPLIST [appName] >= 1 : # 说明是可加载的
                # 开始加载
                try:
                    plug:APPSDK = importlib.import_module (appName)
                    if plug.SDK.webApp:
                        # 如果注册了 webApp , 则添加到主app的蓝图
                        flaskApp.register_blueprint (plug.SDK.webApp)
                except Exception as e:
                    _APPLIST [appName] = STATU.ERROR
                    _loger.error (f'Load app {appName} faild' , exc_info=e)
                # 加载完毕
    _loger.info ('App loade already.')

@app.route ('/plugMg/check_app/name=<name>')
def _check_app (name): # 检查 APP 的状态 , app不存在返回 '3'
    if _APPLIST.get (name) == None:
        # 不存在 App
        return '3'
    else:
        return str(_APPLIST.get (name))

@app.route ('/plugMg/disable_app/name=<name>')
def _disable_app (name): # 关闭 APP
    # 关闭APP,返回执行后APP的开启状态 , app不存在返回 'undefined'
    if _APPLIST.get (name) == None:
        # 不存在 App
        return '3'
    else:
        _APPLIST [name] = 0
        return str(_APPLIST.get (name))

@app.route ('/plugMg/enable_app/name=<name>')
def _enable_app (name): # 开启 APP
    # 开启APP,返回执行后APP的开启状态 , app不存在返回 'undefined'
    if _APPLIST.get (name) == None:
        # 不存在 App
        return '3'
    else:
        _APPLIST [name] = 1
        return str(_APPLIST.get (name))