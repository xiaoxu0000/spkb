# coding=utf-8
#!/usr/bin/python

import requests
import os
from bs4 import BeautifulSoup
import sys
import random
import time
import json
import logging
import csv

requests.packages.urllib3.disable_warnings()

# 越多越好
meizi_headers = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'
    "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:30.0) Gecko/20100101 Firefox/30.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/537.75.14",
    "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Win64; x64; Trident/6.0)",
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11',
    'Opera/9.25 (Windows NT 5.1; U; en)',
    'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)',
    'Mozilla/5.0 (compatible; Konqueror/3.5; Linux) KHTML/3.5.5 (like Gecko) (Kubuntu)',
    'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.0.12) Gecko/20070731 Ubuntu/dapper-security Firefox/1.5.0.12',
    'Lynx/2.8.5rel.1 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/1.2.9',
    "Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.7 (KHTML, like Gecko) Ubuntu/11.04 Chromium/16.0.912.77 Chrome/16.0.912.77 Safari/535.7",
    "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:10.0) Gecko/20100101 Firefox/10.0",
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36'
]

spkb = "https://spankbang.com"
web_info_path = "web_info.csv"
video_info_path = "video_info.csv"
exist_id_path = "exist_id.csv"
related_album_path = "album.csv"
related_album_full_path = "album_full.csv"
favorites_path = "favorites.csv"

global headers
headers = {
    "User-Agent": random.choice(meizi_headers),
}

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
        data = requests.get(url, headers=headers, verify=False, allow_redirects=True, stream=True)
        return data.text
    except:
        logging.info("requests err: " + url)
        return None

"""
解析related playlists
"""
def parse_related_playlists(data):
    try:
        local = read_csv(related_album_path)
        urls = []
        for a in local:
            urls.append(a[0])
        new = []
        new_full = []
        soup = BeautifulSoup(data, "html.parser")
        lists = soup.find_all("div", class_="playlist-item")
        for list in lists:
            url = spkb + list.a["href"]
            name = str(list.p.contents[0])
            if (url not in urls):
                new.append([url])
                new_full.append([url, name])
        write_csv(related_album_path, new, "a+")
        write_csv(related_album_full_path, new_full, "a+")
    except:
        logging.info("parse_related_playlists err")

"""
解析视频链接
"""
def parse_video_links(data):
    try:
        soup = BeautifulSoup(data, "html.parser")
        video_json = str(soup.find("script", type="application/ld+json").contents[0])
        video_json = video_json.replace("\n", "").replace("\r", "")
        video_json = json.loads(video_json)
        if ("@type" in video_json and video_json["@type"] == "VideoObject"):
            return video_json
        else:
            return None
    except:
        logging.info(data)
        return None

def get_dl_links():
    local_web_lists = read_csv(web_info_path)
    exist_id = read_csv(exist_id_path)
    new_info = []
    for info in local_web_lists:
        if info[0] not in exist_id:
            # data = open("html/2.html", "r", encoding="utf-8").read()
            data = web_requests(info[1])
            if (data == None):
                continue
            parse_related_playlists(data) # 解析相关播报列表
            video_json = parse_video_links(data) # 解析当前视频链接
            if (video_json == None):
                continue
            new_info.append([info[0], info[1], video_json["name"], video_json["contentUrl"], video_json["thumbnailUrl"],
                            video_json["description"], video_json["keywords"], video_json["uploadDate"]])
            time.sleep(random.randint(0, 2))
    write_csv(video_info_path, new_info, "a+")


"""
读取本地共享列表url
"""
def get_shared_playlists():
    shared_playlists = []
    f = open("shared_lists", "r")
    for line in f:
        if (line[0] != "#"):
            line = line.replace("\r", "")
            line = line.replace("\n", "")
            shared_playlists.append(line)
    f.close()
    return shared_playlists

def album_parse_html(data):
    info = []
    is_last_page = False
    soup = BeautifulSoup(data, "html.parser")
    video_lists = soup.find("div", class_="video-list video-rotate video-list-with-ads").find_all("div", class_="video-item")
    for video_list in video_lists:
        url_a = video_list.find("a", class_="n")
        if (url_a != None):
            url = spkb + url_a["href"]
            id = video_list["data-id"]
            info.append([id, url])
    return info

def album_get_all_items(url):
    page = 1
    items = []
    while (True):
        # data = open("html/" + str(page) + ".html", "r", encoding="utf-8").read()
        url = url + "/" + str(page)
        data = web_requests(url)
        if (data == None):
            break

        items = items + album_parse_html(data)

        # 判断是否是最后一页
        soup = BeautifulSoup(data, "html.parser")
        total_num = int(soup.find("div", class_="pagination-page-info").find_all("b")[1].contents[0])
        cur_num = int(soup.find("div", class_="pagination-page-info").find_all("b")[0].contents[0].replace(" ", "").split("-")[1])
        if (cur_num >= total_num):
            break
        else:
            page = page + 1
    return items

def album_cal_matching_rate(items):
    # 本地id lists
    local_all = read_csv(favorites_path)
    local = []
    for a in local_all:
        local.append(a[0])

    total_len = len(items)
    valid_len = 0
    for item in items:
        if item[0] in local:
            valid_len = valid_len + 1
    rate = round(valid_len * 100 / total_len)
    return rate


def album_save_items(items):
    # 读取本地items
    local_info = read_csv(web_info_path)
    all_id = [] 
    for a in local_info:
        all_id.append(a[0])
    
    # 新增的items
    new_info = []
    for item in items:
        if (item[0] not in all_id):
            new_info.append(item)
    
    # 保存到本地
    write_csv(web_info_path, new_info, "a+")

"""
抓取共享列表url中的video page
"""
def get_video_page():
    shared_playlists = get_shared_playlists()
    for playlist_url in shared_playlists:

        # 获取当前播放列表所有条目信息
        items = album_get_all_items(playlist_url)

        # 分析该播放列表匹配度（根据favarite匹配）
        rate = album_cal_matching_rate(items)
        logging.info(playlist_url + " rate: " + str(rate))

        # 保存播放列表（去重）/丢掉播放列表
        if (rate > 0):
            album_save_items(items)


def main_app():
    get_video_page()
    get_dl_links()


if __name__ == '__main__':
    log_config()
    main_app()

# parse_related_playlists(open("html/10.html", "r", encoding="utf-8").read())
