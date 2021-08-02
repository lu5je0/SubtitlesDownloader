# SubtitlesDownloader
使用射手字幕网的公开API，快速下载字幕

### 使用方法
####  下载单个视频的字幕
下载/home/videos/xxx.mkv的字幕
```sh
python3 fetch_subs.py ~/xxx.mkv
```

#### 下载一个目录及子目录下的所有视频的字幕
下载/home/videos目录下的所有视频的字幕
```sh
python3 fetch_subs.py ~/videos
```

#### 下载当前目录及子目录的所有视频的字幕
```sh
python3 fetch_subs.py .
```
