#!/usr/bin/python
import os
import shutil
from pyrogram import Client, filters, errors
from urllib.parse import urlparse
from pySmartDL import SmartDL
from plugins.tools import progress, is_url, extension, speedtest_using_cli
import asyncio
from urllib.parse import unquote
import subprocess

tdict = dict()
upload_as_doc = True
#from pyrogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton


api_id = int(os.environ.get('API_ID'))
api_hash = os.environ.get('API_HASH')
bot_token = os.environ.get('BOT_TOKEN')
app = Client("account", api_id=api_id, api_hash=api_hash, bot_token=bot_token)



async def upload(client, message, filepath, user_id):
  c_time= time.time()
  global upload_as_doc
  global tdict
  filename = os.path.basename(filepath)
  exten = extension(filepath)
  await app.edit_message_text(user_id, message.message_id ,                              f"Uploading {filename}...")
  if(user_id in tdict):
    if upload_as_doc == False  and (exten == '.mp4' or exten == '.mkv'):
      await app.send_chat_action(user_id, "upload_video")
      await app.send_video(user_id, filepath,supports_streaming=False,caption=filename,thumb=str(tdict[user_id]))
    else:
      await app.send_chat_action(user_id, "upload_document")
      await app.send_document(user_id, filepath,caption=filename,thumb=str(tdict[user_id],progress=progress_for_pyrogram,progress_args=("Upload Status: \n",message,c_time)))
  else:
    if upload_as_doc == False  and (exten == '.mp4' or exten == '.mkv'):
      await app.send_chat_action(user_id, "upload_video")
      await app.send_video(user_id, filepath,supports_streaming=False,caption=filename)
    else:
      await app.send_chat_action(user_id, "upload_document")
      await app.send_document(user_id, filepath,caption=filename,progress=progress_for_pyrogram,progress_args=("Upload Status: \n",message,c_time))
  await app.delete_messages(user_id, message.message_id)

@app.on_message(filters.command(["help"]) & filters.private)
async def help(client, message):
  text = "/start : Check Alive Status \n/upload : Upload DIrect Links \n/thumb : Reply to photo to save as custom thumb \n/clrthumb : Clear Custom ThumbNail \n/speedtest: Check DL and UL Speed"
  await app.send_message(message.chat.id, text)

#on getting start msg
@app.on_message(filters.command(["start"]) & filters.private)
async def start(client, message):
    user_id = message.chat.id
    text = "Hi ! This is Simple File Upload Bot \n\nCheck usage with '/help'"
    await app.send_message(user_id, text)  #sends above messsage

@app.on_message(filters.command(["thumb"]) & filters.private)
async def thumb(client, message):
  global tdict
  try:
    photo = message.reply_to_message
    photo_dl_path = f"downloads/{message.chat.id}/"
    await photo.download(file_name = photo_dl_path)
    f = []      
    for file in os.listdir(f"{photo_dl_path}"):f.append(str(file))
    p_ext = extension(f"photo_dl_path/{f[-1]}")
    allowed = [".jpeg",".jpg"]
    if p_ext not in allowed :
      await message.reply_text("Only jpeg photos can be used")
      return
    tdict[message.chat.id] = f"{photo_dl_path}/{f[-1]}"
    await message.reply_text(f"Custom Thumb Saved",reply_to_message_id=photo.message_id,quote=True) 
  except Exception as e:
    await message.reply_text(f"SomeThing Went Wrong ! Check Input")

@app.on_message(filters.command(["clrthumb"]) & filters.private)
async def thumb(client, message):
  user_id = message.chat.id
  global tdict
  if(user_id in tdict):
    tdict[user_id] = ""
    shutil.rmtree(f"downloads/{user_id}/")
    await message.reply_text("Thumbnail Cleared")
  else :
    await message.reply_text("No Custom Thumbnail Found")

@app.on_message(filters.command(["speedtest"]) & filters.private)
def speedtest(client, message):
  message =  message.reply_text(f"Performing Speedtest ...")
  text = speedtest_using_cli()
  message.edit_text(f"**Speedtest Results :**\n\n{text}")
  
'''#on getting toggle msg
@app.on_message(filters.command(["toggle"]) & filters.private)
async def toggle(client, message):
  global upload_as_doc
  if upload_as_doc == False: upload_as_doc = True
  else: upload_as_doc = False
  user_id = message.chat.id
  text = "Video File Will be Uploaded as "
  if upload_as_doc: text += "**Document**"
  else: text += "**Streamable**"
  await app.send_message(user_id, text)
'''
#on getting link msg
@app.on_message(filters.command(["upload"]) & filters.private)
async def link(client, message):
    user_id = message.chat.id
    if os.path.isdir(f"download/{user_id}"):
        await app.send_message(user_id,
                         "Please wait for previous task to complete...")
        return
    global filepath
    url = message.text[8:len(message.text)]  #seperate link from message
    if(is_url(url) == False):
      await app.send_message(user_id, "Please enter valid url")
      return
    text = f"Checking url..."
    bot_msg = await app.send_message(user_id, text,
                     disable_web_page_preview=True)  #displays user input
    await app.edit_message_text(user_id,bot_msg.message_id, "File Downloading")
    path = f"download/{user_id}/{message.message_id}"
    if os.path.isdir(f"download/{user_id}") == False:
      try:
        os.makedirs(path)
        downloader = SmartDL(url, path, progress_bar=False)
        downloader.start(blocking=False)
        file_name = os.path.basename(url)
        while not downloader.isFinished():
          percentage = downloader.get_progress() * 100
          prg = progress(int(percentage),100)
          speed = downloader.get_speed(human=True)
          eta_time = downloader.get_eta(human=True)
          progress_str = f"File Name : {unquote(file_name)} \n" +f"Progress : {prg}\n" +"Completed : " + str(int(percentage)) +"%\n" + f"Speed : {speed}\n" + f"ETA : {eta_time}"
          await app.edit_message_text(user_id, bot_msg.message_id , f"{progress_str}")
          await asyncio.sleep(3)
        await app.edit_message_text(user_id, bot_msg.message_id , "File Downloaded")
        f = []
        for file in os.listdir(f"{path}"):
            f.append(
                file
            )  #  will make a list of all files downloaded according to user_id
        filepath = f"{path}/{f[0]}"
        await upload(client, bot_msg, filepath, user_id)
        filepath = f"download/{user_id}/"
        shutil.rmtree(filepath) #remove user_id folder from downloads
      except errors.MessageNotModified:
        while not downloader.isFinished(): pass
        f = []
        for file in os.listdir(f"{path}"): f.append(file)
        filepath = f"{path}/{f[0]}"
        print(filepath)
        await upload(client, bot_msg, filepath, user_id)
        filepath = f"download/{user_id}/"
        shutil.rmtree(filepath)
      except Exception as e:
        e_text = str(e)
        shutil.rmtree(f"download/{user_id}/")
        await app.delete_messages(user_id, bot_msg.message_id )
        await app.send_message(user_id, e_text)


app.run()