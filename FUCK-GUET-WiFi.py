from requests import get
import json
import re
import base64
import os
import getpass
import subprocess
import time
import sys


def get_wifi_info():
    output = subprocess.run(["netsh", "WLAN", "show", "interfaces"],
                            capture_output=True,
                            text=False, shell=False)
    output = output.stdout.decode("gb18030").replace(" ", "").split()
    tmp_list = {}
    for line in output:
        if "接口" in line:
            continue
        if ':' in line:
            key, value = line.split(':', 1)
            tmp_list[key.strip()] = value.strip()
    return tmp_list


connect_retry_times = 0
wifi_info = get_wifi_info()
while connect_retry_times <= 3:
    if "SSID" not in wifi_info:  # 如果wifi未连接
        print("WiFi未连接,正在尝试连接...")
        try:
            subprocess.run(["netsh", "WLAN", "connect", "GUET-WiFi"],
                           capture_output=False, stdout=subprocess.DEVNULL)
            time.sleep(3)  # 等待wifi连接
        except:
            print("连接失败!请手动连接或稍后再试。")
            os.system("pause")
            sys.exit(0)
    elif wifi_info["SSID"] != "GUET-WiFi":  # 如果连接的wifi不是校园网
        print("未正确连接至校园网,正在尝试连接...")
        try:
            subprocess.run(["netsh", "WLAN", "disconnect"],
                           capture_output=False, stdout=subprocess.DEVNULL)
            time.sleep(1)  # 等待断开连接
            subprocess.run(["netsh", "WLAN", "connect", "GUET-WiFi"],
                           capture_output=False, stdout=subprocess.DEVNULL)
            time.sleep(3)  # 等待重新连接
        except:
            print("连接失败!请手动连接或稍后再试。")
            os.system("pause")
            sys.exit(0)
    else:
        break
    wifi_info = get_wifi_info()  # 重新尝试获取wifi信息
    connect_retry_times += 1

if "SSID" not in wifi_info or wifi_info["SSID"] != "GUET-WiFi" or connect_retry_times > 3:
    print("wifi连接异常!请检查wifi连接、确保在校园网覆盖范围内或稍后再试")
    os.system("pause")
    sys.exit(0)

if os.path.exists('info.json'):  # 文件存储
    print("正在使用已保存的账户密码登录...")
    with open('info.json', 'r') as f:
        data = json.load(f)
        user_name = str(data.get('user_name'))
        pwd = str(data.get('pwd'))
else:  # 找不到文件时需用户输入
    user_name = str(input('首次使用,请输入智慧校园账号/学号:'))
    while len(user_name) != 10:
        user_name = str(input('输入格式不正确!请重新输入:'))
    try:
        pwd = str(getpass.getpass('请输入密码:'))
    except:
        pwd = str(input('请输入密码:'))
    pwd = base64.b64encode(pwd.encode("ascii")).decode("ascii")  # base64加密

# 生成登录url、header
url = f"http://10.0.1.5:801/eportal/portal/login?user_account=%2C0%2C{user_name}\
        &user_password={pwd}&wlan_user_mac={wifi_info['物理地址']}&wlan_ac_name=HJ-BRAS-ME60-01"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 \
    (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0',
    'Referer': 'https://10.0.1.5:801/',
    'Host': '10.0.1.5'
}

try:
    response = get(url, headers=headers, timeout=3)  # 发送get请求
    content = json.loads(re.search(r'\{.*}', response.text).group())["msg"]
    print(response.status_code, content)

    # 返回正确,如果密码正确,且文件不存在,则创建文件存储正确账户密码以供下次使用
    if not os.path.exists('info.json') and "ldap auth error" not in content and response.status_code == 200:
        with open('info.json', 'w') as f:
            data = {'user_name': user_name, 'pwd': pwd}
            json.dump(data, f, indent=4)
            print("已将账户密码加密存入程序目录下的info.json文件,下次认证无需输入")

    elif "ldap auth error" in content and os.path.exists('info.json'):
        # 如果密码错误且账户文件存在,删除账户文件,以防下次再使用错误的账户密码
        os.remove('info.json')

except Exception as e:  # get超时3s后捕获
    print(e)
    print("连接失败,可能是请求频率过高,请稍后再试...")
    os.system("pause")
    sys.exit(0)

os.system("pause")
sys.exit(0)
