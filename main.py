#!/usr/bin/python
import os
import shutil
from pyrogram import Client, filters
from urllib.parse import urlparse
from pySmartDL import SmartDL
import asyncio
#from pyrogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

api_id = int(os.environ.get('API_ID'))
api_hash = os.environ.get('API_HASH')
bot_token = os.environ.get('BOT_TOKEN')
app = Client("account", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

def progress(current,total):
  bar =""
  current = int(current/10)
  for i in range(0,10):
      if(i < current):
          bar += "■" 
      else:
          bar += "□"
  return f"[{bar}]"
def is_url(url):
  try:
    result = urlparse(url)
    return all([result.scheme, result.netloc])
  except :
    return False
#on getting start msg
@app.on_message(filters.command(["start"]))
async def start(client, message):
    user_id = message.chat.id
    text = "Hi ! This is Simple File Upload Bot \n\nSend Link along with command e.g '/link your_link'"
    await app.send_message(user_id, text)  #sends above messsage


#on getting link msg
@app.on_message(filters.command(["link"]))
async def link(client, message):
    user_id = message.chat.id
    if os.path.isdir(f"download/{user_id}"):
        await app.send_message(user_id,
                         "Please wait for previous task to complete...")
        return
    
    url = message.text[6:len(message.text)]  #seperate link from message
    if(is_url(url) == False):
      await app.send_message(user_id, "Some error occurred/invalid url")
      return
    text = f"Your entered link = {url}"
    await app.send_message(user_id, text,
                     disable_web_page_preview=True)  #displays user input
    await app.send_message(user_id, "File Downloading")
    path = f"download/{user_id}/{message.message_id}"
    if os.path.isdir(f"download/{user_id}") == False:
      os.makedirs(path)
      downloader = SmartDL(url, path, progress_bar=False)
      downloader.start(blocking=False)
      file_name = os.path.basename(url)
      while not downloader.isFinished():
        percentage = downloader.get_progress() * 100
        prg = progress(int(percentage),100)
        speed = downloader.get_speed(human=True)
        eta_time = downloader.get_eta(human=True)
        progress_str = f"File Name : {file_name} \n" +f"Progress : {prg}\n" +"Completed : " + str(int(percentage)) +"%\n" + f"Speed : {speed}\n" + f"ETA : {eta_time}"
        await app.edit_message_text(user_id, message.message_id + 2, f"{progress_str}")
        await asyncio.sleep(5)
      await app.edit_message_text(user_id, message.message_id + 2, "File Downloaded")
      f = []
      for file in os.listdir(f"{path}"):
          f.append(
              file
          )  #  will make a list of all files downloaded according to user_id
      filepath = f"{path}/{f[0]}"
      await app.edit_message_text(user_id, message.message_id + 2,
                            "Please wait ...file is being uploaded")

      await app.send_chat_action(user_id, "upload_document")
      msg_toedit = await app.get_messages(user_id,message.message_id + 2)
      await app.send_document(user_id, filepath,progress=progress)
      await app.delete_messages(user_id, message.message_id + 2)
      filepath = f"download/{user_id}/"
      shutil.rmtree(filepath)  #remove user_id folder from downloads


app.run()
