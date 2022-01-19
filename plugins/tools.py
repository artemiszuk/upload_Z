from urllib.parse import urlparse
import pathlib
import subprocess
from pyrogram import Client, filters, errors
import os
import shutil
import random
import ffmpeg
import speedtest
import wget
import asyncio

from pySmartDL import SmartDL
from urllib.parse import unquote
from plugins.progress import humanbytes

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



async def dl_link(app,message):
  user_id = message.chat.id
  '''if os.path.isdir(f"download/{user_id}"):
      bot_msg = await app.send_message(user_id,
                        "Queue Added")
      return "",bot_msg'''
  url = message.text.split()[-1]  #seperate link from message
  if(len(url) == 0):
    bot_msg = await app.send_message(user_id, "Enter URL along with command")
    return "",bot_msg
  text = f"Checking url..."
  bot_msg = await app.send_message(user_id, text,
                    disable_web_page_preview=True)  #displays user input
  path = f"download/{user_id}/{message.message_id}"
  if os.path.isdir(f"download/{user_id}") == False:
    try:
      await bot_msg.edit_text("File Downloading")
      os.makedirs(path)
      downloader = SmartDL(url, path, progress_bar=False)
      downloader.start(blocking=False)
      file_name = os.path.basename(url)
      while not downloader.isFinished():
        total_length = downloader.filesize if downloader.filesize else 0
        downloaded = downloader.get_dl_size()
        percentage = downloader.get_progress() * 100
        prg = progress(int(percentage),100)
        speed = downloader.get_speed(human=True)
        eta_time = downloader.get_eta(human=True)
        progress_str = f"File Name : {unquote(file_name)} \n" +f"Progress : {prg}\n"+f"{humanbytes(downloaded)} of {humanbytes(total_length)}\n" +"Completed : " + str(int(percentage)) +"%\n" + f"Speed : {speed}\n" + f"ETA : {eta_time}"
        await app.edit_message_text(user_id, bot_msg.message_id , f"{progress_str}")
        await asyncio.sleep(3)
      await app.edit_message_text(user_id, bot_msg.message_id , "File Downloaded")
      f = os.listdir(path)
      filepath = f"{path}/{f[0]}"
      return filepath,bot_msg
    except errors.MessageNotModified:
      while not downloader.isFinished(): pass
      f = os.listdir(path)
      filepath = f"{path}/{f[0]}"
      return filepath,bot_msg
    except Exception as e:
      e_text = str(e)
      shutil.rmtree(f"download/{user_id}/")
      print(e_text)
      await bot_msg.edit_text("Some Error Occcured,Can't Download ")
      return 


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