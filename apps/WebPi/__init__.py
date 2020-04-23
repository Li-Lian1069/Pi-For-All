import psutil,os,time,json,pywifi
from appApi import APPSDK
from flask import Blueprint , redirect , url_for , render_template , request

# 留了个坑:
# 启动软件后会默认接管wifi,如果用户唯一的连接方式是wifi的话,将会直接断联
# 解决方法:
#     在 /boot 或者程序根目录 下新建一个 wificonf.json 的文件 , 程序启动后自动读取该文件.



SDK = APPSDK ('WebPi',__name__,url_prefix='/WebPi',static_url_path='',static_folder='static',template_folder='templates')

logger = SDK.create_loger ()
config = SDK.get_cfg_file ('config.toml')
app = SDK.webApp
logger.info ('WebPi now start.')

try:
    # 导入wifi模块
    from . import wifi
    wifi.logger = SDK.create_loger ('wifi')
    wifi.settingDir = SDK.get_cfg_dir ()
    wifi.main ()
except Exception as e:
    logger.error ('wifi module has some error.',exc_info=e)
    wifi = False
# =========================
try:
    # 导入volume模块
    from . import volume
except OSError as e:
    logger.error ('volume module will disable in your os.',exc_info=e)
    volume = False
# =========================

def template (**agrs):
    return render_template ('template.html',iface=wifi.get_ifaces (),**agrs)


@app.route ('/')
def index ():
    # 网页入口
    return redirect ( url_for ('WebPi.home') )

@app.route ('/home/')
def home ():
    return template (content = render_template ('home.html'))

@app.route ('/drive_state/')
def drive_state ():
    return template (content = render_template ('drive_state.html'))

@app.route ('/applications/')
def applications ():
    return template (content = render_template ('applications.html'))

@app.route ('/settings/')
def settings ():
    return template (content = render_template ('settings.html'))

@app.route ('/about/')
def about ():
    return template (content = render_template ('about.html'))

@app.route ('/api/wifi',methods=["POST"])
def api_wifi ():
    """
    WIFI接口:
        传入:
            # {
            #     'command'      : check | list | scan | connect | disconnect
            #     'ifaceName'    : ifaceName | all 使用All时查询wifi是否可用
            #     'profile'      : 连接时使用 json文本
            # }
        返回:
            # {
            #     'statu' : STATU.DISCONNETCED # 状态识别码
            #     'scan_results' : list[dict]  # 网卡扫描的profile
            #     'ifaces' : ['wlan0'] # 返回网卡列表
            #     'errormsg' : str # 发生错误时错误信息
            # }
    """


    if request.method == "GET":
        request.form = request.args

    # 检查某个网卡状态
    # {
    #     'command'  : 'check'
    #     'iface'    : ifaceName | all 使用All时查询wifi是否可用
    #     'profile'  : 连接时使用
    # }

    # 返回:
    # {
    #     'statu' : STATU.DISCONNETCED ,
    #     'scan_results' : dict
    #     'ifaces' : ['wlan0']
    #     'errormsg' : str
    # }

    # scan_results : {
    #   'id': 0,
    #   'auth': 0,
    #   'akm': [4],
    #   'cipher': 0,
    #   'ssid': 'YMJK_5G',
    #   'bssid': 'a4:9b:4f:93:08:48',
    #   'key': None,
    #   'freq': 5745,
    #   'signal': -49
    # }

    if not wifi:
        return json.dumps ({
            'statu' : -1 ,
            'errormsg' : 'wifi is unloaded.'
        })

    result = {
        'statu' : wifi.DISCONNETCED
    }

    try:
        if not wifi.INTERFACES:
            # list为空表示 WIFI 不能用.
            result ['statu'] = wifi.DISABLE
            result ['errormsg'] = 'wifi is disavailable.'
            return json.dumps (result)

        command = request.form.get ('command')

        if command == 'list':
            """
                # 获取网卡列表 , 返回一个网卡名的list
            """
            result ['ifaces'] = wifi.get_ifaces ()
            return json.dumps (result)

        ifaceName = request.form.get ('ifaceName')

        if command == 'check':
            """
                检查某个 wlan 的状态
            """

            iface = wifi.get_iface (ifaceName)
            result ['statu'] = iface.status ()
            return json.dumps (result)

        if command == 'scan':
            # 扫描,返回结果 默认时间10秒
            # 传入:
            # {
            #    'command' : 'check'
            #    'iface'   : ifaceName | all
            # }
            # 开始扫描
            iface = wifi.get_iface (ifaceName)
            iface.scan ()
            time.sleep (10) # 等待10秒
            result ['scan_results'] = []
            for profile in iface.scan_results ():
                result ['scan_results'].append (profile.__dict__)
            return json.dumps (result)

        if command == 'connect':
            # 连接 , 然后返回网卡状态

            # form 里的 ['profile'] 是 json 文本,先解析
            profile = json.loads (request.form.get ('profile'))
            try:
                statu = wifi.connect (ifaceName,profile)
            except Exception as e:
                result ['statu'] = wifi.ERROR
                result ['errormsg'] = repr (e)
                return json.dumps (result)

            result ['statu'] = statu
            return json.dumps (result)

        if command == 'disconnect':
            # 断连
            iface = wifi.get_iface (ifaceName)
            iface.disconnect ()
            result ['statu'] = iface.status ()
            return json.dumps (result)

        iface = wifi.get_iface (ifaceName)
        result['statu'] = iface.status ()
        raise Exception ('Unknow command.')
    except Exception as e:
        result['statu'] = wifi.ERROR
        result['errormsg'] = str (e)
        logger.error ('wifi operater has a error.',exc_info=e)
        return json.dumps (result)

@app.route ('/api/state/',methods=['POST'])
def api_check_state ():

    d = {
        'cpu' : {
            'total' : 0,
            'per' : [],
        } ,
        'ram' : {} ,
        'disk' : {} ,
        'net' : {} ,
    }


    #     cpu : {
    #         total : xxx,
    #         per : [xxx,xxx,xxx,xxx]
    #     }
    cpu_state = psutil.cpu_percent (percpu=True)
    # [20.0, 20.0, 60.0, 0.0]

    for i in range (len(cpu_state)):
        d['cpu']['total'] += cpu_state[i]
        d['cpu']['per'].append (cpu_state[i])
    d['cpu']['total'] = d['cpu']['total'] / len (cpu_state)
    # ↑ 获取 相对百分比

    #     ram : {
    #         percent : xxx,
    #         total : xxx,
    #         available : xxx,
    #         used : xxx,
    #         free : xxx,
    #     }

    ram_state = psutil.virtual_memory ()

    #ram_template = ['total','available','percent','used','free']
    for i in range (len(ram_state)):
        d['ram']['total'] = ram_state [0]
        d['ram']['available'] = ram_state [1]
        d['ram']['percent'] = ram_state [2]
        d['ram']['used'] = ram_state [3]
        d['ram']['free'] = ram_state [4]


    #     disk : {
    #         percent : xxx,
    #         disk1 {
    #             total : 456916996096 ,
    #             used : 258353971200
    #             free : 198563024896,
    #             percent : 56.5,
    #             mountpoint : 'C:\\',
    #             opts : 'rw',
    #             fstype :
    #         }
    #         disk2 {...}
    #     }

    diskPartitions = psutil.disk_partitions ()
    d['disk']['percent'] = psutil.disk_usage ('/')[-1]
    for i in diskPartitions:
        # 遍历每个 disk
        #[(device='C:\\', mountpoint='C:\\', fstype='NTFS', opts='rw,fixed'),
        #(device='D:\\', mountpoint='D:\\', fstype='NTFS', opts='rw,fixed'),
        try:
            usage = psutil.disk_usage (i[1])
        except Exception :
            # 如果出错,跳过
            continue

        d['disk'][i[0]] = {} #disk1 {}
        d['disk'][i[0]]['mountpoint'] = i[1]
        d['disk'][i[0]]['fstype'] = i[2]
        d['disk'][i[0]]['opts'] = i[3]
        d['disk'][i[0]]['total'] = usage[0]
        d['disk'][i[0]]['used'] = usage[1]
        d['disk'][i[0]]['free'] = usage[2]
        d['disk'][i[0]]['percent'] = usage[3]


    #     net {
    #         total : xxx,
    #         upload : xxx,
    #         download : xxx,
    #         if0 : [
    #             ip1 : 'xxx',
    #             ip2 : 'xxx'
    #         ]
    #         if1 : [...]
    #     }
    sp = next (netSpeed)
    d['net']['total'] = sp [0]
    d['net']['upload'] = sp [1]
    d['net']['download'] = sp [2]

    for k,v in psutil.net_if_addrs().items () :
        d['net'][k] = [] # if0 {}
        for i in v:
            # [snicaddr(family=<AddressFamily.AF_LINK: -1>, address='00-FF-F0-A8-37-96', netmask=None, broadcast=None, ptp=None),
            # snicaddr(family=<AddressFamily.AF_INET: 2>, address='10.198.75.60', netmask='255.255.255.0', broadcast=None, ptp=None),]
            d['net'][k].append (i[1])

    return json.dumps (d)

@app.route ('/api/volume/',methods=["GET","POST"])
def api_volume ():
    """
    # 音量接口 , get 取 post 置.

    传入:
        {
            value : ''
        }
    """

    class STATU:
        OK = 1
        ERROR = 0
    result = {
        'statu' : STATU.ERROR
    }
    if not volume:
        return json.dumps (result)
    if request.method == "GET":
        # 取音量
        result ['value'] = volume.getV ()
        result ['statu'] = STATU.OK
        return json.dumps (result)
    if request.method == "POST":
        # 设置后返回
        result ['statu'] = STATU.OK
        volume.setV (request.form.get ('value',str))
        result ['value'] = volume.getV ()
        return json.dumps (result)

def get_net_speed ():
    '''
        返回一个生成器,每次迭代时返回一个元组: (sp_total,sp_dn,sp_up)
    '''
    tm = time.time ()
    counters = psutil.net_io_counters ()
    total_dn = counters[0]
    total_up = counters[1]
    time.sleep (1)
    while True:
        counters = psutil.net_io_counters ()
        sp_dn = (counters[0] - total_dn) / (time.time () - tm )
        sp_up = (counters[1] - total_up) / (time.time () - tm )
        total_dn = counters[0]
        total_up = counters[1]
        tm = time.time ()
        yield (sp_dn+sp_up,sp_dn,sp_up)
netSpeed = get_net_speed ()
next (netSpeed)


