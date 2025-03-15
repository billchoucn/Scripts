# !/usr/bin/python3
# -- coding: utf-8 --
# -------------------------------
# @Author CHERWIN???
# -------------------------------
# cron "30 9 * * *" script-path=xxx.py,tag=匹配cron用
# const $ = new Env('蜜雪冰城小程序')
import json
import base64
import os
import time

import requests
from urllib.parse import quote_plus
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256

from requests.packages.urllib3.exceptions import InsecureRequestWarning

# 禁用安全请求警告
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

IS_DEV = False
if os.path.isfile('DEV_ENV.py'):
    import DEV_ENV
    IS_DEV = True
if os.path.isfile('notify.py'):
    from notify import send
    print("加载通知服务成功！")
else:
    print("加载通知服务失败!")
send_msg = ''
one_msg=''
def Log(cont=''):
    global send_msg,one_msg
    print(cont)
    if cont:
        one_msg += f'{cont}\n'
        send_msg += f'{cont}\n'

class RUN:
    def __init__(self,info,index):
        global one_msg
        one_msg = ''
        split_info = info.split('@')
        token = split_info[0]
        len_split_info = len(split_info)
        last_info = split_info[len_split_info - 1]
        self.send_UID = None
        if len_split_info > 0 and "UID_" in last_info:
            print('检测到设置了UID')
            print(last_info)
            self.send_UID = last_info
        self.index = index + 1
        self.s = requests.session()
        self.s.verify = False
        self.unionid = token
        self.headers = {
        'Host': 'mxsa.mxbc.net',
        'Content-Type': 'application/json',
        'xweb_xhr': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x6309080f) XWEB/9105',
        'version': '2.2.5',
        'Accept': '*/*',
        'Sec-Fetch-Site': 'cross-site',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': 'https://servicewechat.com/wx7696c66d2245d107/105/page-frame.html',
        'Accept-Language': 'zh-CN,zh;q=0.9'}
        self.accessToken =''
        self.base_url = 'https://mxsa.mxbc.net'


    def getSign(self,params):
        privateKeyString = '''-----BEGIN PRIVATE KEY-----
    MIIEvwIBADANBgkqhkiG9w0BAQEFAASCBKkwggSlAgEAAoIBAQCtypUdHZJKlQ9L
    L6lIJSphnhqjke7HclgWuWDRWvzov30du235cCm13mqJ3zziqLCwstdQkuXo9sOP
    Ih94t6nzBHTuqYA1whrUnQrKfv9X4/h3QVkzwT+xWflE+KubJZoe+daLKkDeZjVW
    nUku8ov0E5vwADACfntEhAwiSZUALX9UgNDTPbj5ESeII+VztZ/KOFsRHMTfDb1G
    IR/dAc1mL5uYbh0h2Fa/fxRPgf7eJOeWGiygesl3CWj0Ue13qwX9PcG7klJXfToI
    576MY+A7027a0aZ49QhKnysMGhTdtFCksYG0lwPz3bIR16NvlxNLKanc2h+ILTFQ
    bMW/Y3DRAgMBAAECggEBAJGTfX6rE6zX2bzASsu9HhgxKN1VU6/L70/xrtEPp4SL
    SpHKO9/S/Y1zpsigr86pQYBx/nxm4KFZewx9p+El7/06AX0djOD7HCB2/+AJq3iC
    5NF4cvEwclrsJCqLJqxKPiSuYPGnzji9YvaPwArMb0Ff36KVdaHRMw58kfFys5Y2
    HvDqh4x+sgMUS7kSEQT4YDzCDPlAoEFgF9rlXnh0UVS6pZtvq3cR7pR4A9hvDgX9
    wU6zn1dGdy4MEXIpckuZkhwbqDLmfoHHeJc5RIjRP7WIRh2CodjetgPFE+SV7Sdj
    ECmvYJbet4YLg+Qil0OKR9s9S1BbObgcbC9WxUcrTgECgYEA/Yj8BDfxcsPK5ebE
    9N2teBFUJuDcHEuM1xp4/tFisoFH90JZJMkVbO19rddAMmdYLTGivWTyPVsM1+9s
    tq/NwsFJWHRUiMK7dttGiXuZry+xvq/SAZoitgI8tXdDXMw7368vatr0g6m7ucBK
    jZWxSHjK9/KVquVr7BoXFm+YxaECgYEAr3sgVNbr5ovx17YriTqe1FLTLMD5gPrz
    ugJj7nypDYY59hLlkrA/TtWbfzE+vfrN3oRIz5OMi9iFk3KXFVJMjGg+M5eO9Y8m
    14e791/q1jUuuUH4mc6HttNRNh7TdLg/OGKivE+56LEyFPir45zw/dqwQM3jiwIz
    yPz/+bzmfTECgYATxrOhwJtc0FjrReznDMOTMgbWYYPJ0TrTLIVzmvGP6vWqG8rI
    S8cYEA5VmQyw4c7G97AyBcW/c3K1BT/9oAj0wA7wj2JoqIfm5YPDBZkfSSEcNqqy
    5Ur/13zUytC+VE/3SrrwItQf0QWLn6wxDxQdCw8J+CokgnDAoehbH6lTAQKBgQCE
    67T/zpR9279i8CBmIDszBVHkcoALzQtU+H6NpWvATM4WsRWoWUx7AJ56Z+joqtPK
    G1WztkYdn/L+TyxWADLvn/6Nwd2N79MyKyScKtGNVFeCCJCwoJp4R/UaE5uErBNn
    OH+gOJvPwHj5HavGC5kYENC1Jb+YCiEDu3CB0S6d4QKBgQDGYGEFMZYWqO6+LrfQ
    ZNDBLCI2G4+UFP+8ZEuBKy5NkDVqXQhHRbqr9S/OkFu+kEjHLuYSpQsclh6XSDks
    5x/hQJNQszLPJoxvGECvz5TN2lJhuyCupS50aGKGqTxKYtiPHpWa8jZyjmanMKnE
    dOGyw/X4SFyodv8AEloqd81yGg==
    -----END PRIVATE KEY-----'''
        sorted_params = sorted(params.items())
        param_str = "&".join(
            f"{k}={quote_plus(json.dumps(v)) if isinstance(v, dict) else quote_plus(str(v))}" for k, v in sorted_params)
        key = RSA.importKey(privateKeyString)
        # 创建一个SHA256哈希对象
        hash_obj = SHA256.new(param_str.encode())
        # 创建一个签名者
        signer = PKCS1_v1_5.new(key)
        # 对哈希对象进行签名
        signature = signer.sign(hash_obj)
        # 对签名进行Base64编码，并替换"/"和"+"字符
        signature = base64.b64encode(signature).decode()
        signature = signature.replace("/", "_").replace("+", "-")
        # print(signature)
        return signature

    def login(self):
        Log(f'开始登陆----->>>')
        params = {
            'third': 'wxmini',
            'unionid': self.unionid,
            't': int(time.time() * 1000),  # 获取当前13位时间戳
            'appId': 'd82be6bbc1da11eb9dd000163e122ecb'
        }
        sign = self.getSign(params)
        params['sign'] = sign
        try:
            response = self.s.post(f'{self.base_url}/api/v1/app/loginByUnionid', headers=self.headers, json=params)

            if response.status_code == 200:
                res_json = response.json()
                code = res_json.get('code', None)
                if code == 0:
                    data = res_json.get('data', {})
                    accessToken = data.get('accessToken', '')

                    if accessToken:
                        self.accessToken = accessToken
                        self.headers['Access-Token'] = accessToken
                        Log('登陆成功?')
                        return True
                    else:
                        Log('登录失败?，accessToken未找到。')
                        return False
                else:
                    print('登录请求未成功?，返回的code不为0')
                    return False
            else:
                print('登录请求失败?，状态码：', response.status_code)
                print('响应内容：', response.text)
                return False
        except Exception as e:
            print('登录过程中出错?，错误信息：', str(e))
            return False

    def get_userInfo(self,END = False):
        # Log(f'获取用户信息----->>>')
        params = {
            't': int(time.time() * 1000),  # 获取当前13位时间戳
            'appId': 'd82be6bbc1da11eb9dd000163e122ecb'
        }
        sign = self.getSign(params)
        params['sign'] = sign
        try:
            response = self.s.get(f'{self.base_url}/api/v1/customer/info', headers=self.headers, params=params)

            if response.status_code == 200:
                res_json = response.json()
                code = res_json.get('code', None)
                if code == 0:
                    data = res_json.get('data', {})
                    mobilePhone = data.get('mobilePhone', '')
                    customerPoint = data.get('customerPoint', '')
                    isSignin = data.get('isSignin', 0)
                    if END:
                        Log(f'[执行后]雪王币：【{customerPoint}】')
                        return
                    Log(f'获取用户信息成功?\n手机号：【{mobilePhone}】\n[执行前]雪王币：【{customerPoint}】')
                    if isSignin == 0:
                        Log('今日未签到')
                        self.signin()
                    else:
                        Log('今日已签到')

                else:
                    print('获取用户信息请求未成功?，返回的code不为0')
                    return False
            else:
                print('获取用户信息请求失败?，状态码：', response.status_code)
                print('响应内容：', response.text)
                return False
        except Exception as e:
            print('获取用户信息过程中出错?，错误信息：', str(e))
            return False

    def signin(self):
        Log(f'签到----->>>')
        params = {
            't': int(time.time() * 1000),  # 获取当前13位时间戳
            'appId': 'd82be6bbc1da11eb9dd000163e122ecb'
        }
        sign = self.getSign(params)
        params['sign'] = sign
        try:
            response = self.s.get(f'{self.base_url}/api/v1/customer/signin', headers=self.headers, params=params)

            if response.status_code == 200:
                res_json = response.json()
                code = res_json.get('code', None)
                if code == 0:
                    data = res_json.get('data', {})
                    ruleValuePoint = data.get('ruleValuePoint', '')
                    Log(f'签到成功?\n获得：【{ruleValuePoint}】雪王币')
                elif code == 5020 :
                    Log('今日已签到')
                else:
                    print('签到请求未成功?，返回的code不为0')
                    return False
            else:
                print('签到请求失败?，状态码：', response.status_code)
                print('响应内容：', response.text)
                return False
        except Exception as e:
            print('签到过程中出错?，错误信息：', str(e))
            return False



    def main(self):
        Log(f"\n开始执行第{self.index}个账号--------------->>>>>")
        if self.login():
            self.get_userInfo()
            self.get_userInfo(True)
            return True
        else:
            return False


    def sendMsg(self, help=False):
        if self.send_UID:
            push_res = CHERWIN_TOOLS.wxpusher(self.send_UID, one_msg, APP_NAME, help)
            print(push_res)


def down_file(filename, file_url):
    print(f'开始下载：{filename}，下载地址：{file_url}')
    try:
        response = requests.get(file_url, verify=False, timeout=10)
        response.raise_for_status()
        with open(filename + '.tmp', 'wb') as f:
            f.write(response.content)
        print(f'【{filename}】下载完成！')

        # 检查临时文件是否存在
        temp_filename = filename + '.tmp'
        if os.path.exists(temp_filename):
            # 删除原有文件
            if os.path.exists(filename):
                os.remove(filename)
            # 重命名临时文件
            os.rename(temp_filename, filename)
            print(f'【{filename}】重命名成功！')
            return True
        else:
            print(f'【{filename}】临时文件不存在！')
            return False
    except Exception as e:
        print(f'【{filename}】下载失败：{str(e)}')
        return False

def import_Tools():
    global CHERWIN_TOOLS,ENV, APP_INFO, TIPS, TIPS_HTML, AuthorCode
    import CHERWIN_TOOLS
    ENV, APP_INFO, TIPS, TIPS_HTML, AuthorCode = CHERWIN_TOOLS.main(APP_NAME, local_script_name, ENV_NAME,local_version)

if __name__ == '__main__':
    APP_NAME = '蜜雪冰城小程序'
    ENV_NAME = 'MXBC'
    CK_NAME = 'unionid'
    CK_URL = 'https://mxsa.mxbc.net/api/v1/app/loginByUnionid'
    print(f'''
??? {APP_NAME}签到???
? 功能：
      积分签到
? 抓包步骤：
      打开抓包工具
      打开{APP_NAME}
      授权登陆
      找{CK_URL}的URl(如果已经授权登陆先退出登陆)
      复制里面的{CK_NAME}参数值
参数示例：o0GLKv7aPboGaxxxxxxxxx
? ??wxpusher一对一推送功能，
  ?需要定义变量export WXPUSHER=wxpusher的app_token，不设置则不启用wxpusher一对一推送
  ?需要在{ENV_NAME}变量最后添加@wxpusher的UID
? 设置青龙变量：
export {ENV_NAME}='{CK_NAME}参数值【不要】前面的Bearer'多账号#或&分割
export SCRIPT_UPDATE = 'False' 关闭脚本自动更新，默认开启
? ? 注意：抓完CK没事儿别打开小程序，重新打开小程序请重新抓包
? 推荐cron：30 9 * * *
??? @Author CHERWIN???
''')
    local_script_name = os.path.basename(__file__)
    local_version = '2024.05.15'
    if IS_DEV:
        import_Tools()
    else:
        if os.path.isfile('CHERWIN_TOOLS.py'):
            import_Tools()
        else:
            if down_file('CHERWIN_TOOLS.py', 'https://github.com/CHERWING/CHERWIN_SCRIPTS/raw/main/CHERWIN_TOOLS.py'):
                print('脚本依赖下载完成请重新运行脚本')
                import_Tools()
            else:
                print('脚本依赖下载失败，请到https://github.com/CHERWING/CHERWIN_SCRIPTS/raw/main/CHERWIN_TOOLS.py下载最新版本依赖')
                exit()
    print(TIPS)
    token = ''
    token = ENV if ENV else token
    if not token:
        print(f"未填写{ENV_NAME}变量\n青龙可在环境变量设置 {ENV_NAME} 或者在本脚本文件上方将{CK_NAME}填入token =''")
        exit()
    tokens = CHERWIN_TOOLS.ENV_SPLIT(token)
    # print(tokens)
    if len(tokens) > 0:
        print(f"\n>>>>>>>>>>共获取到{len(tokens)}个账号<<<<<<<<<<")
        access_token = []
        for index, infos in enumerate(tokens):
            run_result = RUN(infos, index).main()
            if not run_result: continue
        if send: send(f'{APP_NAME}挂机通知', send_msg + TIPS_HTML)