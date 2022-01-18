from urllib.parse import urlparse
import pathlib
import subprocess
import os
import random
import ffmpeg
import speedtest
import wget

async def speedtst(client, message):
  message =  await message.reply_text(f"Performing Speedtest ...")
  try:
      test = speedtest.Speedtest()
      test.get_best_server()
      await message.edit_text("`Performing download test . . .`")
      test.download()
      await message.edit_text("`Performing upload test . . .`")
      test.upload()
      test.results.share()
      result = test.results.dict()
  except Exception as e:
      await message.edit_text(f"{str(e)}")
  path = wget.download((result['share']))
  await message.reply_photo(photo=path)
  await message.delete()
  os.remove(path)

def extension(fpath):
  return str(pathlib.Path(fpath).suffix)

def is_url(url):
  try:
    result = urlparse(url)
    return all([result.scheme, result.netloc])
  except :
    return False

def progress(current,total):
  bar =""
  current = int(current/10)
  for i in range(0,10):
      if(i < current):
          bar += "█" 
      else:
          bar += "░"
  return f"[{bar}]"

async def get_details(filepath):
    mydict = dict()
    probe = ffmpeg.probe(filepath)
    video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
    mydict['width'] = int(video_stream['width'])
    mydict['height'] = int(video_stream['height'])
    mydict['duration'] = probe['format']['duration']
    filename = os.path.basename(filepath)
    mydict['tname'] = filename[0:filename.index(".")] + ".jpeg"
    (
      ffmpeg
      .input(filepath, ss=random.randrange(0,int(float(mydict['duration']))))
      .filter('scale', mydict['width'], -1)
      .output(mydict['tname'], vframes=1)
      .run()
    )
    return mydict