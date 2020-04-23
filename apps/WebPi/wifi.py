"""
    wifi 管理模块
    启动后会从配置文件 , /boot/wificonf.json , ./wificonf.json 中读取并自动连接

    # /boot/wificonf.json: & ./wificonf.json
    # {
    #     'iface':'wlan0',
    #     'ssid' : 'xxx',
    #     'key'  : 'xxx'
    # }
"""
import pywifi , json , time
from logging import Logger
from os import path

# profiles.json:
# {
#     'wlan1': [
#         {
#             profile 1
#         },
#         {
#             profile 2
#         }
#     ],

#     'wlan2': [
#         {
#             profile 1
#         } ,
#         ...
#     ]
# }

# /boot/wificonf.json: & ./wificonf.json
# {
#     'iface':'wlan0',
#     'ssid' : '',
#     'key' : ''
# }

logger:Logger
settingDir:str
INTERFACES:list = []
# =====STATUS======
DISABLE = -2
ERROR = -1
DISCONNETCED = 0
SCANNING = 1
INACTIVE = 2
CONNETCING = 3
CONNETCED = 4
# =================


def get_iface (ifaceName:str) -> pywifi.iface.Interface:
    """
        返回一个网卡的对象
    """
    global INTERFACES
    for i in INTERFACES:
        if i.name () == ifaceName:
            return i

def get_ifaces () -> list:
    """
    返回所有可用网卡的网卡名
    """
    global INTERFACES
    l = []
    for i in INTERFACES:
        if 'p2p' in i.name (): # 树莓派有个p2p开头的网卡是不能用的
            continue
        l.append ( i.name () )
        i.scan () # 开始搜索
    return l

def get_profiles (ifaceName) -> list:
    """
    从文件中读取配置,并转化为 pywifi 的 profile 文件
    -> list[pywifi.Profile]
    """

    l = []

    try:
        with open (path.join (settingDir,'wifi-profiles.json'),'r') as fp:
            PROFILES = json.load (fp)
    except Exception as e:
        logger.error ('load profiles error.',exc_info=e)
        return []

    assert ifaceName in PROFILES , Exception ('this iface is not in profile.')

    for i in PROFILES [ifaceName]: # each profile
        profile = pywifi.Profile ()
        profile.__dict__ = i
        l.append (profile)

    return l

def add_profile (ifaceName:str,profile:dict):
    """
    添加某个配置项到配置文件中
    """
    # 读取
    try:
        with open (path.join (settingDir,'wifi-profiles.json'), 'r') as fp:
            PROFILES = json.load (fp)
    except Exception as e:
        logger.error ('load profiles error. try create file',exc_info=e)


    if not (ifaceName in PROFILES): PROFILES [ifaceName] = [] # 如果网卡还没有过数据,添加数据
    # 修改
    PROFILES [ifaceName].append (profile)

    # 写入
    try:
        with open (path.join (settingDir,'wifi-profiles.json'), 'w') as fp:
            json.dump (PROFILES,fp)
    except Exception as e:
        logger.error ('dump profiles error.',exc_info=e)

def remove_profile (ifaceName:str,ssid:dict) -> pywifi.Profile:
    """
        从配置文件中删除一个配置项
    """
    # 读取
    try:
        with open (path.join (settingDir,'wifi-profiles.json'), 'a') as fp:
            fp.seek (0) # 指针到文件头
            PROFILES = json.load (fp)
    except Exception as e:
        logger.error ('read profile error at `remove profile`.',exc_info=e)
        return

    if not (ifaceName in PROFILES): return # 啥都没有,返回 空

    # 删除
    for i in PROFILES [ifaceName]:
        if i['ssid'] == ssid:
            PROFILES [ifaceName].remove (i)
            break

    # 写入
    try:
        with open (path.join (settingDir,'wifi-profiles.json'), 'w') as fp:
            json.dump (PROFILES,fp)
    except Exception as e:
        logger.error ('dumps profile error at `remove profile`' , exc_info= e)

def connect (ifaceName:str,profile:dict) -> int:
    """
        连接,并返回网卡状态,如果连接成功自动记录wifi
    """
    iface = get_iface (ifaceName)


    iface.disconnect ()# 先断连
    while not (iface.status () == DISCONNETCED):
        time.sleep (1) # 等待断联

    PROFILE = pywifi.Profile ()
    PROFILE.__dict__ = profile

    iface.add_network_profile (PROFILE)
    iface.connect (PROFILE)

    time.sleep (2) # 等待两秒
    while iface.status () == CONNETCING :
        time.sleep (0.5)

    if iface.status () == CONNETCED:
        # 连接成功
        logger.info ('add a wifi profile to local.')
        add_profile (ifaceName,profile)

    return iface.status ()


def main ():
    global WIFI , INTERFACES
    WIFI = pywifi.PyWiFi ()
    INTERFACES = WIFI.interfaces ()

    if not INTERFACES: # 没有可用的wifi网卡
        logger.warn ('No wireless card available, Wifi function will disabled.')

    if not path.isfile (path.join (settingDir,'wifi-profiles.json')):
        # 创建配置文件
        with open (path.join (settingDir,'wifi-profiles.json'),'w') as fp:
            fp.write ('{}')

    for iface in INTERFACES:
        # 自动连接
        try:
            if 'p2p' in iface.name (): # 树莓派有一个名字里带有 'p2p' 的网卡是不能用的
                continue

            if (iface.status == CONNETCED) or (iface.status == CONNETCING): iface.disconnect ()

            PROFILES = get_profiles (iface.name ())
            if len (PROFILES) == 0: continue # 防止出现没有配置文件的情况

            iface.add_network_profile (PROFILES[0])
            iface.connect (PROFILES[0])

            logger.info (f'wireless card {iface.name ()} connect to `{PROFILES[0].ssid}`')
        except Exception as e:
            logger.error ('auto connect faild.',exc_info=e)


    # 尝试加载boot分区下的文件
    def load_at_boot ():
        if path.isfile ('./wificonf.json'):
            try:
                logger.info ('find `./wificonf.json` , try to use it.')
                with open ('./wificonf.json','r') as fp:
                    settings = json.load (fp)
                    iface = get_iface (settings ['iface'])
                    iface.scan ()
                    time.sleep (10)
                    result = iface.scan_results ()
                    for i in result:
                        if i.ssid == settings ['ssid']:
                            PROFILE = pywifi.Profile ()
                            PROFILE.__dict__ = i.__dict__
                            PROFILE.key = settings ['key']
                            iface.add_network_profile (PROFILE)
                            iface.connect (PROFILE)
                            break
            except Exception as e:
                logger.warn ('have something wrong at `./wificonf.json`.' ,exc_info=e)

        if path.isfile ('/boot/wificonf.json'):
            try:
                logger.info ('find `/boot/wificonf.json` , try to use it.')
                with open ('/boot/wificonf.json','r') as fp:
                    settings = json.load (fp)
                    iface = get_iface (settings ['iface'])
                    iface.scan ()
                    time.sleep (10)
                    result = iface.scan_results ()
                    for i in result:
                        if i.ssid == settings ['ssid']:
                            PROFILE = pywifi.Profile ()
                            PROFILE.__dict__ = i.__dict__
                            PROFILE.key = settings ['key']
                            iface.add_network_profile (PROFILE)
                            iface.connect (PROFILE)
                            break
            except Exception as e:
                logger.warn ('have something wrong at `/boot/wificonf.json`.' ,exc_info=e)

    load_at_boot ()

    logger.info ('wifi module loaded.')