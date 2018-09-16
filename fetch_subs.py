import hashlib
import re
import requests
import json
import os
import sys


def movie_hash(file_path):
    with open(file_path, 'rb') as file:
        file.seek(0, 2)
        length = file.tell()
        file_hash = []
        for i in [4096, int(length * 2 / 3), int(length / 3), length - 8192]:
            file.seek(i, 0)
            buffer = file.read(4096)
            file_hash.append(hashlib.md5(buffer).hexdigest())
        return ';'.join(file_hash)


def get_subs(file_hash, movie_name):
    resp = requests.post("https://www.shooter.cn/api/subapi.php", data={
        "filehash": file_hash,
        "pathinfo": movie_name, "format": "json"})
    return json.loads(resp.content)


def download_sub(url, path, movie, ext, num):
    resp = requests.get(url)

    sub_name = "{}.{}.{}".format(movie, num, ext)
    with open(os.path.join(path, sub_name), "wb") as f:
        f.write(resp.content)
        print("成功下载:" + sub_name)


def main(path):
    # 文件夹
    if os.path.isdir(path):
        movies = os.listdir(path)
        movies = filter(lambda x: re.match("(?i).*(mkv|mp4|rmvb|avi)$", x), movies)
    # 文件
    else:
        movies = {path}
        path = os.path.split(path)[0]
    for movie in movies:
        try:
            file_hash = movie_hash(os.path.join(path, movie))
            subs = get_subs(file_hash, movie)
            for num, sub in enumerate(subs):
                for file in sub["Files"]:
                    download_sub(file["Link"], path, movie, file["Ext"], num)
        except:
            print("未找到{}的字幕".format(movie))


if __name__ == '__main__':
    main(sys.argv[1])
