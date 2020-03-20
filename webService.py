import flask,os,appApi,logging,toml
# from appApi import regApp

app = flask.Flask ('webService')

_SEP = os.sep
appApi.mkdir (f'log{_SEP}webService')
appApi.mkdir (f'settings{_SEP}webService')

_HOST = 'localhost'
_PORT = 80


_loger = logging.getLogger ("webService")
_hanlder = logging.FileHandler (f'log{_SEP}webService{_SEP}{appApi.timeApi.getYMD ()}.log')
_hanlder.setLevel (logging.INFO)
_hanlder.setFormatter (logging.Formatter ("%(asctime)s %(levelname)s %(name)s-Line:%(lineno)d"))
_loger.addHandler (_hanlder)

_hanlder = logging.StreamHandler ()
_hanlder.setLevel (logging.WARN)
_loger.addHandler (_hanlder)

_FILE_PATH = os.path.split(os.path.realpath(__file__))[0]
_STAITC_PATH = _FILE_PATH + f'{_SEP}static'
_STIATC_CONTENTS = os.listdir (_STAITC_PATH)

APP_ROUTE = {}
# {
#     'appName' : [(url1,func,youNeed),(url2,func,youNeed)]
# }

def add_route (appName,path,func):
    '''
        申请一个路由,监测到时调用传入的 func 函数
         - AppName : 你的软件包名称
         - path : 路由器响应的地址,如果传入的 path 为 '/' , 那么实际响应的地址应该为 .../appName/path
         - func : 回调函数
        
        * 示例: add_route ('main','/',my_func,['request','redirect',...])
        
        * 当路由器匹配到响应的规则时候,将调用传入的 func 函数并传入 youNeed 中对应的项目 
        
        * func的原型应该如下:
            def func (path,**kwargs):
                do something

            - path: 响应路由的路径
            - **kwargs : 用于接收youNeed
    '''
    if not (appName in APP_ROUTE):
        APP_ROUTE[appName] = []
    if path [0] != '/':
        # 第一个路径应该为 '/'
        path = '/' + path

    APP_ROUTE[appName].append ((path,func))



def run (host="0.0.0.0",port=80,debug=False):
    global _HOST , _PORT
    _HOST = host
    _PORT = port
    app.logger = _loger
    app.debug = debug
    _loger.info (f'webService now is running. | host={host},port={port},debug={debug}.')
    app.run (host,port,debug,)

@app.route ('/')
def _index (): # 入口
    return flask.render_template ('index.html')

@app.route ('/<path:path>')
def _hanlder (path): # 响应APP的自定义路由
    # 一个PT 形如: /appName/page1/page2
    pt = flask.request.path
    ptSp = pt.split ('/')
    # ptSp = ['','appName','page1','page2']

    if ptSp [1] in APP_ROUTE: # APP_ROUTE中的每个Key都是appName
            # ptSp 的第二个成员是appName
            for i in APP_ROUTE[ptSp [1]]:
                # (url1,func,youNeed)
                if i [0] == pt [pt.find ('/',pt.find('/')+1):]:
                    # pt.find ('/',pt.find('/')) :  返回一个过滤掉第一层'/'的结果
                    if appApi.openurl (f'{_HOST}:{_PORT}/plugMg/check_app/name={ptSp [1]}'):
                        # 检查 app 是否开启,开启则转发
                        return i [1] () # 调用并传入 flask 对象
                    else: # 如果被禁用
                        return 'App is disable.'

@app.before_request
def _before_redirecter ():
    # 一个PT 形如: xxx/appName/page/page
    pt = flask.request.path
    ptSp = pt.split ('/')
    # ptSp = ['','appName','page1','page2']

    if ptSp [1] in _STIATC_CONTENTS:
        # 对 static 下的目录进行重定向
        return flask.redirect (f'/static{pt}')

    elif ptSp [1] in APP_ROUTE: # APP_ROUTE中的每个Key都是AppName
        # 响应APP的API路由
        # ptSp 的第二个成员是appName
        for i in APP_ROUTE[ptSp [1]]:
            # (url1,func,youNeed)
            if i [0] == pt [pt.find ('/',pt.find('/')+1):]:
                # pt.find ('/',pt.find('/')) :  返回一个过滤掉第一层'/'的结果
                return i [1] () # 调用并传入 flask 对象