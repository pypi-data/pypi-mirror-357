from yt_dlp import YoutubeDL
from .create_log import CreateLog

def DownloadVideo(video_url: str):
  conf = {
    'format': 'best',
    'outtmpl': 'video.mp4',
    'quiet': True,
    'no_warnings': True,
    'logtostderr': False
  }
  with YoutubeDL(conf) as ydl:
    ydl.download(video_url)