import requests
import hashlib
import json
import time

import os
from dotenv import load_dotenv

load_dotenv()

USER_ID = os.getenv("USER_ID")
API_TOKEN = os.getenv("API_TOKEN")
API_URL = "https://ifdian.net/api/open/query-sponsor"


def generate_sign(token, params, ts, user_id):
    """
    生成爱发电API签名
    :param token: 你的API token
    :param params: 请求参数的JSON字符串
    :param ts: 时间戳（秒）
    :param user_id: 你的user_id
    :return: 签名字符串
    """
    # 按照爱发电规则拼接字符串
    sign_string = f"{token}params{params}ts{ts}user_id{user_id}"
    # 计算MD5签名
    md5 = hashlib.md5()
    md5.update(sign_string.encode('utf-8'))
    return md5.hexdigest()


def get_sponsors(page=1):
    """
    获取指定页的赞助者信息
    :param page: 页码，从1开始
    :return: 赞助者列表和总页数
    """
    # 生成时间戳
    ts = int(time.time())
    # 构建请求参数
    params = {"page": page}
    params_json = json.dumps(params)

    # 生成签名
    sign = generate_sign(API_TOKEN, params_json, ts, USER_ID)

    # 构建请求数据（不打印）
    request_data = {
        "user_id": USER_ID,
        "params": params_json,
        "ts": ts,
        "sign": sign
    }

    # 发送请求
    headers = {'Content-Type': 'application/json'}
    try:
        response = requests.post(
            API_URL, json=request_data, headers=headers, timeout=10)

        # 处理响应
        if response.status_code == 200:
            data = response.json()
            if data.get("ec") == 200:
                return data["data"]["list"], data["data"]["total_page"]
            else:
                return None, None
        else:
            return None, None
    except Exception:
        return None, None


def get_all_sponsors():
    """
    获取所有赞助者信息（自动分页）
    :return: 所有赞助者列表
    """
    all_sponsors = []
    page = 1
    while True:
        sponsors, total_page = get_sponsors(page)
        if not sponsors:
            break
        all_sponsors.extend(sponsors)
        if total_page is None or page >= total_page:
            break
        page += 1
    return all_sponsors


def generate_markdown(sponsors):
    """将赞助者数据转换为markdown表格"""
    if not sponsors:
        return "暂无赞助者数据"
    md = ""
    md += "| --- | --- | --- |\n"
    for sponsor in sponsors:
        user_info = sponsor.get("user", {})
        name = user_info.get("name", "未知")
        amount = sponsor.get("all_sum_amount", "0.00")
        last_time = sponsor.get("last_pay_time", 0)
        last_time_str = time.strftime(
            "%Y-%m-%d", time.localtime(last_time)) if last_time else "-"
        md += f"| {name} | {amount}元 | {last_time_str} |\n"
    return md


# 程序启动时获取数据
all_sponsors = get_all_sponsors()
sponsors_md = generate_markdown(all_sponsors)
# sponsors_md = ""

from datetime import datetime

now = datetime.now()


def define_env(env):
    """
    This is the hook for the variables, macros and filters.
    """
    @env.macro
    def get_time():
        "generate compile time"
        return now.strftime("%Y-%m-%d %H:%M:%S")

    @env.macro
    def get_md_list_sponsors() -> str:
        return sponsors_md


if __name__ == "__main__":
    print(sponsors_md)
