#!/usr/bin/env /home/lu5je0/.dotfiles/submodule/SubtitlesDownloader/.env/bin/python3
import hashlib
import requests
import json
import os
import sys
import asstosrt
import chardet
from concurrent.futures import ThreadPoolExecutor


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

    if num != 0:
        sub_name = "{}.{}.{}".format(video_name, num, ext)
    else:
        sub_name = "{}.{}".format(video_name, ext)

    file_name = os.path.join(path, sub_name)
    with open(file_name, "w", encoding="utf8") as f:
        content = resp.content
        charset = chardet.detect(content)["encoding"].lower()

        if charset in ["gb2312", "big5"]:
            charset = "gb18030"

        f.write(bytes.decode(content, encoding=charset))
        print("成功下载:" + sub_name)
    if ext == "ass":
        duplicate_srt_sub(file_name)


def duplicate_srt_sub(ass_filename):
    srt_filename = ass_filename.replace(".ass", ".srt")
    with open(srt_filename, "w+", encoding="utf8") as srt_file:
        try:
            with open(ass_filename, encoding="utf8") as ass_file:
                srt_file.write(asstosrt.convert(ass_file))
            print("duplicate srt {}".format(srt_filename))
        except Exception as e:
            print(e)


sub_suffixes = ["srt", "ass"]


def check_if_exists_subs(filename):
    for suffix in sub_suffixes:
        if os.path.exists(filename + "." + suffix):
            print("存在{}的字幕, 跳过".format(filename))
            return True
    return False


def fetch(video):
    print('fetching {}'.format(video))
    path = os.getcwd()
    if check_if_exists_subs(video):
        return
    try:
        file_hash = video_hash(os.path.join(path, video))
        subs = get_subs(file_hash, video)
        for num, sub in enumerate(subs):
            for file in sub["Files"]:
                download_sub(file["Link"], path, video, file["Ext"], num)
    except Exception as e:
        print("未找到{}的字幕 cause:{}".format(video, e))

def main(videos):
    executor = ThreadPoolExecutor(max_workers=30)
    
    for video in videos:
        executor.submit(fetch, video)
        
    executor.shutdown()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("usage: fetch_subs filename")
    else:
        main(sys.argv[1:])
