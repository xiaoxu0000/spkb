# coding=utf-8
#!/usr/bin/python

from bs4 import BeautifulSoup
import random
import time
import json
import logging
from publib import *

spkb = "https://spankbang.com"
video_pages_path = "video_pages.csv"    # 所有播放页面url
related_album_path = "album.csv"        # 所有专辑
favorites_path = "favorites.csv"        # 喜欢的id


"""
读取本地共享列表url
"""
def get_album_playlists():
    shared_playlists = []
    f = open(related_album_path, "r")
    for line in f:
        if (line[0] != "#"):
            line = line.replace("\r", "").replace("\n", "")
            shared_playlists.append(line)
    f.close()
    return shared_playlists

def album_parse_html(data):
    info = []
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
    try:
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
    except:
        logging.info("album_get_all_items err")
    return items

def album_cal_matching_rate(items):
    if (len(items) == 0):
        return 0,[]
    # 本地id lists
    local_all = read_csv(favorites_path)
    local = []
    for a in local_all:
        local.append(a[0])

    total_len = len(items)
    valid_len = 0
    valid_items = []
    for item in items:
        if item[0] in local:
            valid_len = valid_len + 1
            valid_items.append(item[0])
    rate = round(valid_len * 100 / total_len)
    logging.info("rate: " + str(rate) + "(" + str(valid_len) + "/" + str(total_len) + ")")
    return rate, valid_items


def album_save_items(items):
    # 读取本地items
    local_info = read_csv(video_pages_path)
    all_id = [] 
    for a in local_info:
        all_id.append(a[0])
    
    # 新增的items
    new_info = []
    for item in items:
        if (item[0] not in all_id):
            new_info.append(item)
    
    # 保存到本地
    write_csv(video_pages_path, new_info, "a+")

"""
抓取共享列表url中的video page
"""
def get_video_pages():
    album_playlists = get_album_playlists()
    for playlist_url in album_playlists:

        # 获取当前播放列表所有条目信息
        items = album_get_all_items(playlist_url)

        # 分析该播放列表匹配度（根据favarite匹配）
        rate, valid_items = album_cal_matching_rate(items)

        # 保存播放列表（去重）/丢掉播放列表
        if (rate >= 10):
            album_save_items(items)


def main_app():
    get_video_pages()


if __name__ == '__main__':
    log_config()
    main_app()
