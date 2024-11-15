from requests import get
import json
import re
import base64
import wmi
import os
import getpass


def get_macaddress():
    for nw in wmi.WMI().Win32_NetworkAdapterConfiguration(IPEnabled=True):  # 从已连接的网络中寻找mac地址
        return nw.MACAddress.replace(":", "").lower()  # 更改为小写,去除冒号


print("请确认已连接至GUET-WIFI,按回车继续...", end='')
input()

if os.path.exists('info.json'):  # 文件存储
    print("正在使用已保存的账户密码登录...")
    with open('info.json', 'r') as f:
        data = json.load(f)
        user_name = str(data.get('user_name'))
        pwd = str(data.get('pwd'))
        f.close()
else:  # 找不到文件时需用户输入
    user_name = str(input('请输入智慧校园账号/学号:'))
    try:
        pwd = str(getpass.getpass('请输入密码:'))
    except:
        pwd = str(input('请输入密码:'))
    pwd = base64.b64encode(pwd.encode("ascii")).decode("ascii")  # base64加密

# 生成登录url、header
url = f"http://10.0.1.5:801/eportal/portal/login?user_account=%2C0%2C{user_name}&user_password={pwd}&wlan_user_mac={get_macaddress()}&wlan_ac_name=HJ-BRAS-ME60-01"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0',
    'Referer': 'https://10.0.1.5:801/',
    'Host': '10.0.1.5'
}

try:
    response = get(url, headers=headers, timeout=2)  # 发送get请求
    content = json.loads(re.search(r'\{.*}', response.text).group())["msg"]
    print(response.status_code, content)

    # 返回正确,如果密码正确,且文件不存在,则创建文件存储正确账户密码以供下次使用
    if not os.path.exists('info.json') and "ldap auth error" not in content and response.status_code == 200:
        with open('info.json', 'w') as f:
            data = {'user_name': user_name, 'pwd': pwd}
            json.dump(data, f, indent=4)
            f.close()
            print("已将账户密码加密存入文件,下次认证无需输入")
    elif "ldap auth error" in content:  # 如果密码错误,删除账户文件,以防下次再使用错误的账户密码
        os.remove('info.json')
except:  # get超时3s后捕获
    print("连接失败!")

os.system("pause")
