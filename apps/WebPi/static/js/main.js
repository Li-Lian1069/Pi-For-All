function ifaceOnChange (Element) {
    // {
    //      'iface' : 'wlan0',
    //      'command' : 'check' ,
    //
    // }
}

function volumeOnChange (vaule) {
    $.post (
        '/WebPi/api/volume',
        {vaule:vaule}
    )
}