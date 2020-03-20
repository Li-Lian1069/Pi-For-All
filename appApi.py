import toml,logging,time
from os import path , makedirs , sep
from urllib import request as _request
import urllib as _urllib
from collections import UserDict as _UserDict

def openurl (url,data=None):
        '''
            执行网页get操作,并且返回结果
        '''
        return _request.urlopen (url,data).read ()

def mkdir (path,mode=0o766):
    '''
        检测文件夹是否存在,并递归创建
        成功返回 T 失败返回失败文本
    '''
    try:
        if path.isdir (path):
            return True
        else:
            makedirs (path,mode)
    except Exception as e:
        return repr (e)

class _timeApi ():
    def sp (self,target):
        '''将传入的 "-" ":" 字符分割后返回'''
        if ':' in target:
            return target.split (':')
        else:
            return target.split ('-')

    def getYMD (self):
        '''2020-03-16'''
        return time.strftime("%F")

    def getD (self):
        '''获取天数'''
        return time.strftime("%d")

    def getM (self):
        '''获取月份'''
        return time.strftime("%m")

    def getY (self):
        '''获取年份'''
        return time.strftime("%Y")

    def getH (self):
        '''获取小时'''
        return time.strftime("%H")

    def getMin (self):
        '''获取分钟'''
        return time.strftime("%M")

    def getS (self):
        '''获取秒钟'''
        return time.strftime("%S")

    def getHMS (self):
        '''获取时分秒'''
        return time.strftime("%T")

    def getHM (self):
        '''获取时分'''
        return time.strftime("%R")

    def get (self,fmt='%X'):
        '''
            根据自定义规则取时间
            格式参数：
                %a  星期几的简写
                %A  星期几的全称
                %b  月分的简写
                %B  月份的全称
                %c  标准的日期的时间串
                %C  年份的后两位数字
                %d  十进制表示的每月的第几天
                %D  月/天/年
                %e  在两字符域中，十进制表示的每月的第几天
                %F  年-月-日
                %g  年份的后两位数字，使用基于周的年
                %G  年分，使用基于周的年
                %h  简写的月份名
                %H  24小时制的小时
                %I  12小时制的小时
                %j  十进制表示的每年的第几天
                %m  十进制表示的月份
                %M  十时制表示的分钟数
                %n  新行符
                %p  本地的AM或PM的等价显示
                %r  12小时的时间
                %R  显示小时和分钟：hh:mm
                %S  十进制的秒数
                %t  水平制表符
                %T  显示时分秒：hh:mm:ss
                %u  每周的第几天，星期一为第一天 （值从0到6，星期一为0）
                %U  第年的第几周，把星期日做为第一天（值从0到53）
                %V  每年的第几周，使用基于周的年
                %w  十进制表示的星期几（值从0到6，星期天为0）
                %W  每年的第几周，把星期一做为第一天（值从0到53）
                %x  标准的日期串
                %X  标准的时间串
                %y  不带世纪的十进制年份(值从0到99)
                %Y  带世纪部分的十制年份
                %z,%Z   时区名称，如果不能得到时区名称则返回空字符。
                %%  百分号
        '''
        return time.strftime("%x")

timeApi = _timeApi ()

class LOG_leave ():
    DEBUG=logging.DEBUG
    INFO=logging.INFO
    WARN=logging.WARN
    ERROR=logging.ERROR
    CRITICAL=logging.CRITICAL

class APPSDK ():
    def __init__ (self,appName):

        import webService

        self.get_cfg_file.appName = appName
        self.create_loger.appName = appName
        self.add_route = webService.add_route
        self.url_encoder = _urllib.parse.urlencode
        self.webObj = webService.app
        self.web_route = webService.app.route

        if not path.isdir (f'settings{sep}{appName}'):
            mkdir (f'settings{sep}{appName}')

        if not path.isdir (f'log{sep}{appName}'):
            mkdir (f'log{sep}{appName}')
        

    def getFileDir (self,file):
        '''
            取得目前脚本的所在目录
        '''
        return path.split(path.realpath(file))[0]

    def getFilePath (self,file):
        '''
            取得目前脚本的所在目录
        '''
        return path.realpath(file)

    class get_cfg_file(_UserDict):
        '''
            获取一个文件,返回一个类似于dict的对象,之后可以用dict的方法使用此对象.
                - file : 文件名,不存在则创建
                - saveMode : 文件保存的时机,可以指定多种方式,若需指定多种方式,可以传入一个list或tuple
        '''
        def __init__ (self,fileName,save_when_change=True):
            '''
            获取一个文件,返回一个类似于dict的对象,之后可以用dict的方法使用此对象.
                - file : 文件名,不存在则创建
                - save_when_change=True : 对象的字典被更改时是否自动保存
            '''
            super ().__init__ ()
            
            self.__is_loading = True
            self.__filePath = f'settings{sep}{self.appName}{sep}{fileName}'
            self.__saveWhenCh = save_when_change
            
            if fileName [-5:] != '.toml':
                # 判断并补全后缀
                self.__filePath = self.__filePath + '.toml'

            if not path.isfile (self.__filePath):
                # 如果文件不存在,创建之
                with open (self.__filePath,'w'):
                    pass

            self.reload ()

        def reload (self):
            self.__is_loading = True
            self.data = toml.load (self.__filePath)
            self.__is_loading = False

        def __setitem__(self, key, item):
            # 当设置一个值的时候,会调用此函数
            self.data[str(key)] = item
            if self.__is_loading:
                # 如果正在初始化或载入配置,不执行保存操作,防止死循环
                return
            
            if self.__saveWhenCh:
                # 更改时保存
                self.save ()

        def save (self):
            with open (self.__filePath,'w') as self.fp:
                toml.dump (self.data,self.fp)

        def __missing__(self, key):
            
            if isinstance(key, str):
                raise KeyError(key)
            return self[str(key)]

        def __contains__(self, key):
            
            return str(key) in self.data

        def __getattr__(self, key):
            return self.data[str(key)]

    class create_loger ():
        '''
                创建一个Log生产者,并返回一个对象
                    name : 每一个程序单独使用一个name,并将日志保存于 "log/name" 文件夹下
                    toConsole : 是否输出到控制台
                    toFile : 是否输出到文件
                    fileLeave : 控制文件日志输出等级,详见 以 leave.开头的常量
                    consolLeave : 控制台输出等级 同上
                    strFormat : 日志记录的格式
        '''
        def __init__ (self,toConsole=False,toFile=True,fileLeave=LOG_leave.INFO,consolLeave=LOG_leave.WARN,strFormat="%(asctime)s %(levelname)s %(name)s-Line:%(lineno)d"):
            '''
                创建一个Log生产者,并返回一个对象
                    name : 每一个程序单独使用一个name,并将日志保存于 "log/name" 文件夹下
                    toConsole : 是否输出到控制台
                    toFile : 是否输出到文件
                    fileLeave : 控制文件日志输出等级,详见 以 leave.开头的常量
                    consolLeave : 控制台输出等级 同上
                    strFormat : 日志记录的格式
            '''
            self.__loger = logging.getLogger (self.appName)
            self.__fmter = logging.Formatter(strFormat)
            self.__loger.setLevel(fileLeave)
            if toFile:
                self.__handler = logging.FileHandler (f'log{sep}{self.appName}{sep}{timeApi.getYMD ()}.log')
                self.__handler.setLevel (fileLeave)
                self.__handler.setFormatter(self.__fmter)
                self.__loger.addHandler (self.__handler)
            if toConsole:
                self.__schandler = logging.StreamHandler ()
                self.__schandler.setLevel (consolLeave)
                self.__schandler.setFormatter (self.__fmter)
                self.__loger.addHandler (self.__schandler)
            
            self.error = self.__loger.error
            self.info = self.__loger.info
            self.debug = self.__loger.debug
            self.warn = self.__loger.warn
            self.critical = self.__loger.critical

    def add_item_to_web_page (self,icon,link="",content=""):
        '''
            在 Web 主页上注册一个入口
            icon & content : 两个参数只能二选一,如果选择 icon,请传入一个以app为根目录定义的图片,如果是conten,请传入html代码
            link : 用户点击之后会打开此链接的窗口.

            !!! 注意 每个 item 在页面上显示的大小是会有限制的 !!!

        '''
        pass

    def add_cfg_to_web_page (self,key,func,defaultValue=None):
        '''
            添加一个配置项到主页上,用户修改后将触发回调 func (key,value)
        '''
        pass

    
