#!/usr/bin/env python3
import hashlib
import re
import requests
import json
import os
import sys
from multiprocessing.dummy import Pool as ThreadPool
from requests import RequestException


def video_hash(file_path):
    with open(file_path, 'rb') as file:
        file.seek(0, 2)
        length = file.tell()
        file_hash = []
        for i in [4096, int(length * 2 / 3), int(length / 3), length - 8192]:
            file.seek(i, 0)
            buffer = file.read(4096)
            file_hash.append(hashlib.md5(buffer).hexdigest())
        return ';'.join(file_hash)


def get_subs(file_hash, video_name):
    resp = requests.post("https://www.shooter.cn/api/subapi.php", data={
        "filehash": file_hash,
        "pathinfo": video_name, "format": "json"})
    return json.loads(resp.content)


def download_sub(url, path, video_name, ext, num):
    resp = requests.get(url)

    sub_name = "{}.{}.{}".format(video_name, num, ext)
    with open(os.path.join(path, sub_name), "wb") as f:
        f.write(resp.content)
        print("成功下载:" + sub_name)


def task(path, video):
    file_hash = video_hash(os.path.join(path, video))
    subs = get_subs(file_hash, video)
    for num, sub in enumerate(subs):
        for file in sub["Files"]:
            download_sub(file["Link"], path, video, file["Ext"], num)


def main(path):
    videos = []
    pool = ThreadPool(processes=30)

    # 如果是目录
    if os.path.isdir(path):
        for root, _, files in os.walk(path):
            for file in files:
                if re.match("(?i).*(mkv|mp4|rmvb|avi)$", file):
                    videos.append(os.path.join(root, file))
    # 如果是文件
    else:
        videos = {path}
        path = os.path.split(path)[0]
    for video in videos:
        try:
            pool.apply_async(task, (path, video))
        except RequestException as _:
            print("网络异常")
        except:
            print("未找到{}的字幕".format(video))
    pool.close()
    pool.join()


if __name__ == '__main__':
    main(sys.argv[1])
