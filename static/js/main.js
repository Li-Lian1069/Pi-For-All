// 导航栏
window.onload = function() {

    // 导航栏
    page_home = document.getElementById('container-home');
    page_app = document.getElementById('container-app');
    page_settings = document.getElementById('container-settings');
    page_about = document.getElementById('container-about');
    nowPage = page_home;
    $(page_home).fadeIn(CONSTANT.ACR_TIME_NOR);
    // 导航栏
    // =========================
    // HomePage
    HOME_WINDOW_SELECT_WIFI = document.getElementById('home-wifi-select-window');
    HOME_WINDOW_SELECT_BT = document.getElementById('home-bt-select-window');

    // HomePage
}

// init
CONSTANT= {
    ACR_TIME_NOR : 500,
    ACR_TIME_S : 300,
    ACR_TIME_L : 800,
}
// init

function showHomePage() {
    if (nowPage != page_home) {
        $(nowPage).fadeOut(CONSTANT.ACR_TIME_NOR);
        $(page_home).fadeIn(CONSTANT.ACR_TIME_NOR);
        nowPage = page_home;
    }
}

function showAppPage() {
    if (nowPage != page_app) {
        $(nowPage).fadeOut(CONSTANT.ACR_TIME_NOR);
        $(page_app).fadeIn(CONSTANT.ACR_TIME_NOR);
        nowPage = page_app;
    }
}

function showSettingsPage() {
    if (nowPage != page_settings) {
        $(nowPage).fadeOut(CONSTANT.ACR_TIME_NOR);
        $(page_settings).fadeIn(CONSTANT.ACR_TIME_NOR);
        nowPage = page_settings;
    }
}

function showAboutPage() {
    if (nowPage != page_about) {
        $(nowPage).fadeOut(CONSTANT.ACR_TIME_NOR);
        $(page_about).fadeIn(CONSTANT.ACR_TIME_NOR);
        nowPage = page_about;
    }
}

// 导航栏换页


// HomePage

var home = {SELECT_SHOWING: null,}

function home_show_wifi_bt_select(target) {
    
    if (target=='wifi') {
        if (home.SELECT_SHOWING==HOME_WINDOW_SELECT_WIFI){
            //  关闭wifi卡
            $(home.SELECT_SHOWING).hide(CONSTANT.ACR_TIME_S);
            home.SELECT_SHOWING=null;return;
        }if (home.SELECT_SHOWING == HOME_WINDOW_SELECT_BT || home.SELECT_SHOWING == null ){
            //  打开wifi卡
            $(home.SELECT_SHOWING).hide(CONSTANT.ACR_TIME_S);
            home.SELECT_SHOWING=HOME_WINDOW_SELECT_WIFI;
            $(home.SELECT_SHOWING).show(CONSTANT.ACR_TIME_S);
        }
    }
    
    if (target=='bt') {
        if (home.SELECT_SHOWING==HOME_WINDOW_SELECT_BT){
            //  关闭BT卡
            $(home.SELECT_SHOWING).hide(CONSTANT.ACR_TIME_S);
            home.SELECT_SHOWING=null;return;
        }if (home.SELECT_SHOWING == HOME_WINDOW_SELECT_WIFI || home.SELECT_SHOWING == null ){
            //  打开BT卡
            $(home.SELECT_SHOWING).hide(CONSTANT.ACR_TIME_S);
            home.SELECT_SHOWING=HOME_WINDOW_SELECT_BT;
            $(home.SELECT_SHOWING).show(CONSTANT.ACR_TIME_S);
        }
    }
    
}

// HomePage
