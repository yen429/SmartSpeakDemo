const request = require("request");
//把client_id和client_secret改成自己的
let client_id = "VR4HAyiWR9iqZlM55t2VQGzkwI52CmTh";
let client_secret = "X99DGcge0P8hSS9fCB9Awmb0R5pVXboS";

let device_id = "tpv_voide_assistant_test";


const child_process = require("child_process");
const unameAll = child_process.execSync("uname -a").toString();
const config = require("./config");

function isUbuntu() {
    return unameAll.match(/Ubuntu/);
}


function openBrowser(url) {
    let open_cmd = isUbuntu() ? "xdg-open" : "chromium-browser";
    let cmd = open_cmd + ' "' + url + '"';
    console.log("exec command:" + cmd);
    child_process.exec(cmd);
}

request({
    "url": "https://openapi.baidu.com/oauth/2.0/device/code?client_id=" + client_id + "&response_type=device_code&scope=basic,netdisk"
}, function(error, response, body) {
    let json = JSON.parse(body);
    console.log("device code return:", json);
    let user_code = json.user_code;
    let device_code = json.device_code;
    let timeout = new Date().getTime() + json.expires_in * 1000;
    openBrowser('http://openapi.baidu.com/device?code=' + user_code)

    let device_code_interval_id = setInterval(() => {
        request({
            "url": "https://openapi.baidu.com/oauth/2.0/token?grant_type=device_token&code=" + json.device_code + "&client_id=" + client_id + "&client_secret=" + client_secret,
        }, function(error, response, body) {
            let json = JSON.parse(body);
            console.log("get token by device code", json);
            if (!json.access_token) {
                return;
            }
            //console.log("set access_token: "+json.access_token);
            //dcs_controller.setAccessToken(json.access_token);
            config.save("oauth_token", json.access_token);
            console.log("access_token:", json.access_token);
            clearInterval(device_code_interval_id);
        });
    }, json.interval * 1000);
});
