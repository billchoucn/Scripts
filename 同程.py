import requests
from datetime import datetime
import time
import json

#近期有长期大流量卡，有需要可以了解：
#https://hk.yunhaoka.cn/#/pages/micro_store/index?agent_id=78fe575cb0b88f72b967e505d8255dd7

#2025/2/24更新1.2版本：
#修复签到接口，建议重新抓包替换apptoken和device值

# 直接将phone、apptoken、device 写入 Python 文件
ACCOUNTS = [
    {
        'phone': '13700137000',
        'apptoken': 'XXXXXXXXXXXXXXXXXXXXXXXXXX',
        'device': 'XXXXXXXXXXXXXXXXXXXXXXXXXX'
    },
#    {
#        'phone': '13800138000',
#        'apptoken': 'XXXXXXXXXXXXXXXXXXXXXXXXXX',
#        'device': 'XXXXXXXXXXXXXXXXXXXXXXXXXX'
#    }
]

# 获取请求头
def get_headers(phone, apptoken, device, payload):
    payload_str = json.dumps(payload)
    headers = {
        'accept': 'application/json, text/plain, */*',
        'phone': phone,
        'channel': '1',
        'apptoken': apptoken,
        'sec-fetch-site': 'same-site',
        'accept-language': 'zh-CN,zh-Hans;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'sec-fetch-mode': 'cors',
        'origin': 'https://m.17u.cn',
        'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 TcTravel/11.0.0 tctype/wk',
        'referer': 'https://m.17u.cn/',
        'content-length': str(len(payload_str.encode('utf-8'))),
        'device': device,
        'sec-fetch-dest': 'empty'
    }
    return headers

# 获取当前日期
def get_today_date():
    return datetime.now().strftime('%Y-%m-%d')

# 执行签到请求
def sign_in(phone, apptoken, device):
    url = "https://app.17u.cn/welfarecenter/index/signIndex"
    payload = {}
    headers = get_headers(phone, apptoken, device, payload)

    response = requests.post(url, json=payload, headers=headers)
    data = response.json()

    if data['code'] != 2200:
        print(f"用户{phone}的token失效，请更新")
        return None
    else:
        today_sign = data['data']['todaySign']
        mileage = data['data']['mileageBalance']['mileage']
        print(f"用户{phone}今日{'已' if today_sign else '未'}签到，当前剩余里程{mileage}")
        return today_sign

# 执行签到操作
def do_sign_in(phone, apptoken, device):
    url = "https://app.17u.cn/welfarecenter/index/sign"
    payload = {"type": 1, "day": get_today_date()}
    headers = get_headers(phone, apptoken, device, payload)

    response = requests.post(url, json=payload, headers=headers)
    data = response.json()

    if data['code'] != 2200:
        print(f"用户{phone}签到失败，尝试获取任务列表")
        return False
    else:
        print(f"用户{phone}签到成功，开始获取任务列表")
        return True

# 获取任务列表
def get_task_list(phone, apptoken, device):
    url = "https://app.17u.cn/welfarecenter/task/taskList?version=11.0.0.0"
    payload = {}
    headers = get_headers(phone, apptoken, device, payload)

    response = requests.post(url, json=payload, headers=headers)
    data = response.json()

    if data['code'] != 2200:
        print(f"用户{phone}获取任务列表失败，跳过当前账号")
        return None
    else:
        tasks = []
        for task in data['data']:
            if task['state'] == 1 and task['browserTime'] != 0:
                tasks.append({
                    'taskCode': task['taskCode'],
                    'title': task['title'],
                    'browserTime': task['browserTime']
                })
        return tasks

# 开始做任务
def start_task(phone, apptoken, device, task_code):
    url = "https://app.17u.cn/welfarecenter/task/start"
    payload = {"taskCode": task_code}
    headers = get_headers(phone, apptoken, device, payload)

    response = requests.post(url, json=payload, headers=headers)
    data = response.json()

    if data['code'] != 2200:
        print(f"用户{phone}做任务【{task_code}】失败，跳过当前任务")
        return None
    else:
        task_id = data['data']
        return task_id

# 完成任务
def finish_task(phone, apptoken, device, task_id):
    url = "https://app.17u.cn/welfarecenter/task/finish"
    payload = {"id": task_id}
    headers = get_headers(phone, apptoken, device, payload)

    response = requests.post(url, json=payload, headers=headers)
    data = response.json()

    if data['code'] != 2200:
        print(f"用户{phone}完成任务【{task_id}】失败，尝试重新提交...")
        time.sleep(2)
        response = requests.post(url, json=payload, headers=headers)
        data = response.json()

        if data['code'] != 2200:
            print(f"用户{phone}完成任务【{task_id}】失败，开始下一个任务")
            return False
        else:
            print(f"用户{phone}完成任务【{task_id}】成功，开始领取奖励")
            return True
    else:
        print(f"用户{phone}完成任务【{task_id}】成功，开始领取奖励")
        return True

# 领取奖励
def receive_reward(phone, apptoken, device, task_id):
    url = "https://app.17u.cn/welfarecenter/task/receive"
    payload = {"id": task_id}
    headers = get_headers(phone, apptoken, device, payload)

    response = requests.post(url, json=payload, headers=headers)
    data = response.json()

    if data['code'] != 2200:
        print(f"用户{phone}领取任务【{task_id}】奖励失败，请尝试手动领取")
    else:
        print(f"用户{phone}领取任务【{task_id}】奖励成功，开始下一个任务")

# 获取积分信息
def get_mileage_info(phone, apptoken, device):
    url = "https://app.17u.cn/welfarecenter/index/signIndex"
    payload = {}
    headers = get_headers(phone, apptoken, device, payload)

    response = requests.post(url, json=payload, headers=headers)
    data = response.json()

    if data['code'] != 2200:
        print(f"用户{phone}获取积分信息出错")
        return None
    else:
        cycle_sign_num = data['data']['cycleSighNum']
        continuous_history = data['data']['continuousHistory']
        mileage = data['data']['mileageBalance']['mileage']
        today_mileage = data['data']['mileageBalance']['todayMileage']
        print(f"用户{phone}本月签到{cycle_sign_num}天，连续签到{continuous_history}天，今日共获取{today_mileage}里程，当前剩余里程{mileage}")

# 主程序
def main():
    for account in ACCOUNTS:
        phone = account['phone']
        apptoken = account['apptoken']
        device = account['device']

        # 获取签到状态
        today_sign = sign_in(phone, apptoken, device)
        if today_sign is None:
            continue

        # 如果已签到则跳过签到操作，继续执行任务
        if today_sign:
            print(f"用户{phone}已经签到，跳过签到操作")
        else:
            # 执行签到
            if do_sign_in(phone, apptoken, device):
                print(f"用户{phone}成功签到")
        
        # 获取任务列表
        tasks = get_task_list(phone, apptoken, device)
        if tasks:
            for task in tasks:
                task_code = task['taskCode']
                title = task['title']
                browser_time = task['browserTime']
                print(f"用户{phone}开始做任务【{title}】，需要浏览{browser_time}秒")
                
                task_id = start_task(phone, apptoken, device, task_code)
                if task_id:
                    time.sleep(browser_time)
                    if finish_task(phone, apptoken, device, task_id):
                        receive_reward(phone, apptoken, device, task_id)

        # 获取积分信息
        get_mileage_info(phone, apptoken, device)

if __name__ == "__main__":
    main()