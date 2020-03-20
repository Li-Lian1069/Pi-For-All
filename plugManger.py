import flask , sys , os , importlib
from appApi import APPSDK, getFileDir
_SEP = os.sep
_APP = APPSDK ('plugManger')
_loger = _APP.create_loger ()
_APPLIST = _APP.get_cfg_file ('appSettings')

class STATU ():
    DISABLE = 0 # 被禁用
    LOADED = 1 # 已加载且启用
    ERROR = 2 # 加载出错
    UNDEFINED = 3 # 不存在


#{  ↑
#    'appName' : {'isActive':True & False, 'statu' }
#}

# 更改加载路径
sys.path.append (getFileDir() + _SEP + 'apps')

def load_apps ():
    # 开始加载
    _loger.info ('now start to loading apps')
    for appName in os.listdir ('apps'):
        if os.path.isdir (f'apps{_SEP}{appName}'): # 过滤掉apps下的文件,并将新加入的APP添加至列表
            # 到这里的都是文件夹

            if not (appName in _APPLIST): # 如果不在APPLIST中,说明app是新加入的
                _APPLIST[appName] = 1 # 设置为已加载
                # 如果 APP 是新的 , 添加至列表

            if _APPLIST [appName]: # 为True说明是可加载的
                # 开始加载
                try:
                    importlib.import_module (appName)
                except Exception as e: 
                    _APPLIST [appName] = 2 # 加载出错
                    _loger.error (f'Load app {appName} faild : {repr (e)}')
                # 加载完毕
                _loger.info ('App loade already.')

@_APP.web_route ('/plugMg/check_app/name=<name>')
def _check_app (name): # 检查 APP 的状态 , app不存在返回 '3'
    if _APPLIST.get (name) == None:
        # 不存在 App
        return '3'
    else:
        return str(_APPLIST.get (name))

@_APP.web_route ('/plugMg/disable_app/name=<name>')
def _disable_app (name): # 关闭 APP
    # 关闭APP,返回执行后APP的开启状态 , app不存在返回 'undefined'
    if _APPLIST.get (name) == None:
        # 不存在 App
        return '3'
    else:
        _APPLIST [name] = 0
        return str(_APPLIST.get (name))

@_APP.web_route ('/plugMg/enable_app/name=<name>')
def _enable_app (name): # 开启 APP
    # 开启APP,返回执行后APP的开启状态 , app不存在返回 'undefined'
    if _APPLIST.get (name) == None:
        # 不存在 App
        return '3'
    else:
        _APPLIST [name] = 1
        return str(_APPLIST.get (name))