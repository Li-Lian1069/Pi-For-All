$$ = mdui.JQ;
$(document).ready((function () {
    ifaceOnChange (document.getElementById ('iface-select').firstElementChild);

    dialogWifi = new mdui.Dialog('#toolbar-wifi-dialog');
}));
function ifaceOnChange (Element) {
    // {
    //      'iface' : 'wlan0',
    //      'command' : 'check' ,
    // }
    $.post("/WebPi/api/wifi",
        {
            command : 'scan',
            ifaceName : Element.value
        },
        function (data, textStatus, jqXHR) {
            if (textStatus == 'success') {
                data = JSON.parse (data);
                // data : {
                //     "statu": 0,
                //     "scan_results": [
                //       {
                //         "id": 0,
                //         "auth": 0,
                //         "akm": [
                //           4
                //         ],
                //         "cipher": 0,
                //         "ssid": "YMJK_5G",
                //         "bssid": "a4:9b:4f:93:08:48",
                //         "key": null,
                //         "freq": 5745,
                //         "signal": -36
                //       }
                // }
                var wifis = data.scan_results;
                for ( let i = 0; i < wifis.length ; i++ ) {
                    var template = $('#toolbar-wifi-list-template').clone ();
                    template.attr ('id','wifi-item-' + wifis[i].ssid);

                    if (wifis[i].ssid == '') {continue;}

                    if (wifis[i].key != null) {
                        // 有key,说明是已经保存过的
                        $('#toolbar-wifi-connected-list').append (template);
                    }else {
                        // 没key,没保存过
                        $('#toolbar-wifi-list').append (template);
                    }
                    template.find ('.wifi-name').text (wifis[i].ssid);
                    template.find ('.wifi-data').data ('profile', wifis[i]);
                    template.removeClass('mdui-hidden');
                    dialogWifi.handleUpdate(); // 刷新对话框高度
                }}});
}

function wifi_connect (E) {

    dialogWifi.close();

    var profile = $(E).data('profile');
    if (profile.key!=null) {
        // 有key,直接连接
    }else {
        // 没key,输入密码
        mdui.prompt('input the passwd:',
            function (value) {
                profile.key = value;
            }
        );
    }

    $.post("/WebPi/api/wifi",
        {
            command : 'connect',
            ifaceName : document.getElementById ('iface-select').value + '',
            profile : JSON.stringify (profile)
        },
        function (data, textStatus, jqXHR) {
            data = JSON.parse (data);
            if (data.statu == 4){
                mdui.alert ('connect successed!')

                e = $('#' + 'wifi-item-' + profile.ssid).clone();
                $('#' + 'wifi-item-' + profile.ssid).remove();
                $('#toolbar-wifi-connected-list').append(e);
                // 移除到已连接一栏

            }else {
                mdui.alert ('connect faild!')
            }
        },
    );
    dialogWifi.open ();
}


function volumeOnChange (vaule) {
    $.post (
        '/WebPi/api/volume/',
        {value:vaule}
    )
}
