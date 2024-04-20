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
video_info_path = "video_info.csv"
exist_id_path = "exist_id.csv"
related_album_path = "album.csv"
related_album_full_path = "album_full.csv"
favorites_path = "favorites.csv"

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
    local_web_lists = read_csv(video_pages_path)
    exist_id = read_csv(exist_id_path)
    new_info = []
    for info in local_web_lists:
        if info[0] not in exist_id:
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

def main_app():
    get_dl_links()


if __name__ == '__main__':
    log_config()
    main_app()

# parse_related_playlists(open("html/10.html", "r", encoding="utf-8").read())
