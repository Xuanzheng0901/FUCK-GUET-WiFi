from requests import get
import json
import re
import base64
import wmi
import os
import getpass


def get_macaddress():
    for nw in wmi.WMI().Win32_NetworkAdapterConfiguration(IPEnabled=True):
        return nw.MACAddress.replace(":", "").lower()


print("请连接至GUET-WIFI,按回车继续...", end='')

input()

user_name = str(input('请输入智慧校园账号/学号:'))

try:
    pwd = str(getpass.getpass('请输入密码:'))
except:
    pwd = str(input('请输入密码:'))

pwd = base64.b64encode(pwd.encode("ascii")).decode("ascii")

url = f"http://10.0.1.5:801/eportal/portal/login?user_account=%2C0%2C{user_name}&user_password={pwd}&wlan_user_mac={get_macaddress()}&wlan_ac_name=HJ-BRAS-ME60-01"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0',
    'Referer': 'https://10.0.1.5:801/',
    'Host': '10.0.1.5'
}
try:
    x = get(url, headers=headers, timeout=2)
    str0 = re.search(r'\{.*}', x.text).group()

    json_obj = json.loads(str0)

    content = json_obj["msg"]

    print(x, content)

except:
    print("连接超时!请确认您已连接到校园网")

os.system("pause")
