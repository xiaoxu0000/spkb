# coding=utf-8
#!/usr/bin/python

import os
import requests
import logging
import csv
from fake_useragent import UserAgent

requests.packages.urllib3.disable_warnings()

LOG_PATH = '.'
def log_config():
    # 创建输出目录
    if(os.path.exists(LOG_PATH) != True):
        os.makedirs(LOG_PATH)

    # 配置log
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(name)-6s %(levelname)-8s %(message)s',
                        datefmt='%m/%d/%Y %H:%M:%S',
                        filemode='a')

    # 定义一个Handler打印DEBUG及以上级别的日志到文件
    console = logging.FileHandler(LOG_PATH + '/debug.log', encoding='utf-8')
    console.setLevel(logging.INFO)
    # 设置日志打印格式
    formatter = logging.Formatter(
        '%(asctime)s %(name)-6s %(levelname)-8s %(message)s')
    console.setFormatter(formatter)
    # 将定义好的console日志handler添加到root logger
    logging.getLogger('').addHandler(console)


def write_csv(file_name, user_data, mode):
    if (len(user_data) == 0):
        return
    f = open(file_name, mode, encoding="utf-8", newline="")
    csv_write = csv.writer(f)
    csv_write.writerows(user_data)


def read_csv(file_name):
    data = []
    if (os.path.exists(file_name)):
        f = open(file_name, "r", encoding="utf-8")
        csv_read = csv.reader(f)
        for line in csv_read:
            data.append(line)
    return data

def web_requests(url):
    logging.info("requests: " + url)
    try:
        data = requests.get(url, headers=UserAgent().random, verify=False, allow_redirects=True, stream=True)
        return data.text
    except:
        logging.info("requests err: " + url)
        return None
