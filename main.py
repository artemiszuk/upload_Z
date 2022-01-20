#!/usr/bin/python
import os
import shutil
from pyrogram import Client, filters, errors
from urllib.parse import urlparse
from plugins.tools import progress, is_url, extension, speedtst , get_details, dl_link
from plugins.progress import progress_for_pyrogram, humanbytes
import asyncio
import subprocess
import time
from patoolib import extract_archive
tdict = dict()
upload_as_doc = dict()
q_link = dict()
from pyrogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton,  CallbackQuery


api_id = int(os.environ.get('API_ID'))
api_hash = os.environ.get('API_HASH')
bot_token = os.environ.get('BOT_TOKEN')
app = Client("account", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

class messageobj: 
    def __init__(self, message, unzip = False): 
        self.message = message 
        self.unzip = unzip

async def upload_folder(app,path,user_id):
  if os.path.isdir(path) and len(os.listdir(path)) > 0 :
    allfiles = os.listdir(path)
    allfiles.sort()
    info = await app.send_message(user_id,f"Currently in Folder : __{os.path.basename(path)}__\nTotal Files : {len(allfiles)}")
    await asyncio.sleep(3)
    await info.delete()
    #print("Total files",len(allfiles),"allfiles = ",allfiles)
    for flist in allfiles:
      npath = os.path.join(path,flist)
      await upload_folder(app,npath,user_id)
  else:
    await asyncio.sleep(3) 
    bot_msg = await app.send_message(user_id,"Trying to Upload...")
    await upload(bot_msg,path,user_id)

async def unzip_and_upload(bot_msg,filepath,user_id):
  new_dir = filepath[0:filepath.index(extension(filepath))] + "/"
  os.makedirs(new_dir)
  try:
    extract_archive(filepath,outdir=new_dir)
  except Exception as e:
    e_text = str(e)
    await bot_msg.edit_text(e_text)
    return
  else:
    await bot_msg.delete()
    await asyncio.sleep(3)
    await upload_folder(app,new_dir,user_id)


async def upload(message, filepath, user_id):
  c_time= time.time()
  global upload_as_doc
  global tdict
  if user_id not in upload_as_doc : upload_as_doc[user_id] = True
  filename = os.path.basename(filepath)
  exten = extension(filepath)
  await app.edit_message_text(user_id, message.message_id ,                              f"__Uploading {filename}__ ... 📤")
  if(user_id in tdict):
    if upload_as_doc[user_id] == False  and (exten == '.mp4' or exten == '.mkv'):
      mydict = await get_details(filepath)
      await app.send_chat_action(user_id, "upload_video")
      await app.send_video(user_id, filepath,supports_streaming=True,caption=filename,thumb=str(tdict[user_id]),duration=int(float(mydict['duration'])),width=int(mydict['width']),height = int(mydict['height']),progress=progress_for_pyrogram,progress_args=("Upload Status: \n",message,c_time))
    else:
      await app.send_chat_action(user_id, "upload_document")
      await app.send_document(user_id, filepath,caption=filename,thumb=str(tdict[user_id]),progress=progress_for_pyrogram,progress_args=("Upload Status: \n",message,c_time))
  else:
    if upload_as_doc[user_id] == False  and (exten == '.mp4' or exten == '.mkv'):
      mydict = await get_details(filepath)
      await app.send_chat_action(user_id, "upload_video")
      await app.send_video(user_id, filepath,supports_streaming=True,caption=filename,thumb=mydict['tname'],duration=int(float(mydict['duration'])),width=int(mydict['width']),height = int(mydict['height']),progress=progress_for_pyrogram,progress_args=("Upload Status: \n",message,c_time))
      os.remove(mydict['tname'])
    elif (exten == '.mp4' or exten == '.mkv'):
    	mydict = await get_details(filepath)
    	await app.send_chat_action(user_id, "upload_document")
    	await app.send_document(user_id, filepath,caption=filename,thumb=mydict['tname'],progress=progress_for_pyrogram,progress_args=("Upload Status: \n",message,c_time))
    	os.remove(mydict['tname'])
    else:
      await app.send_chat_action(user_id, "upload_document")
      await app.send_document(user_id, filepath,caption=filename,progress=progress_for_pyrogram,progress_args=("Upload Status: \n",message,c_time))
   
  await app.delete_messages(user_id, message.message_id)


@app.on_message(filters.command(["unzip"]) & filters.private)
async def unzip_cmd(client, message):
  archives = [".zip",".rar"]
  if extension(message.text) not in archives:
    await message.reply_text("Not A Zip/Rar Link")
    return
  await link(client,message,True)


@app.on_callback_query()
async def button(client, cmd: CallbackQuery):
  cb_data = cmd.data
  if "help" in cb_data :
    text = "**HELP MENU**:\n\n/start : Check Alive Status \n/upload : Upload DIrect Links \n/unzip : Unzip zip/rar files from direct Links\n/thumb : Reply to photo to save as custom thumb \n/clrthumb : Clear Custom ThumbNail \n/toggle : Upload videos as streamable/document\n/speedtest: Check DL and UL Speed"  
    await cmd.message.edit(text,reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Back ◀", callback_data="start")]]))
  elif "start" in cb_data:
    text = "**MAIN MENU**\n\nHi ! This is Simple File Upload Bot \n\n__Check Below for commands/features__"
    await cmd.message.edit(text,reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Help ❓", callback_data="help"),InlineKeyboardButton("Developer 🧑‍💻", url="https://t.me/SorceryBhai")],[InlineKeyboardButton("Close ❌", callback_data="close"),InlineKeyboardButton("Source Code 📝", url="https://github.com/artemiszuk/upload_Z")]]))
  elif "close" in cb_data:
    await cmd.message.delete()
  elif "toggle" in cb_data:
    global upload_as_doc
    user_id = cmd.from_user.id
    if upload_as_doc[user_id]: upload_as_doc[user_id] = False
    else : upload_as_doc[user_id] = True
    text = "**TOGGLE MENU:**\n[__Click to change__]\n\nVideo File Will be Uploaded as "
    if upload_as_doc[user_id]: text_append = "Document 📁"
    else: text_append = "Streamable 🎬"
    await cmd.message.edit(text,reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text_append, callback_data="toggle"),InlineKeyboardButton("Close ❌", callback_data="close")]]))
#on getting start msg

@app.on_message(filters.command(["start"]) & filters.private)
async def start(client, message):
    user_id = message.from_user.id
    text = "**MAIN MENU**\n\nHi ! This is Simple File Upload Bot \n\n__Check Below for commands/features__"
    await app.send_message(user_id, text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Help ❓", callback_data="help"),InlineKeyboardButton("Developer 🧑‍💻", url="https://t.me/SorceryBhai")],[InlineKeyboardButton("Close ❌", callback_data="close"),InlineKeyboardButton("Source Code 📝", url="https://github.com/artemiszuk/upload_Z")]]))  #sends above messsage

@app.on_message(filters.command(["help"]) & filters.private)
async def help(client, message):
  await start(client, message)

@app.on_message(filters.command(["thumb"]) & filters.private)
async def thumb(client, message):
  global tdict
  photo_msg = message.reply_to_message
  if (photo_msg is not None and photo_msg.photo is not None ):
    photo_dl_path = f"downloads/{message.chat.id}/"
    await photo_msg.download(file_name = photo_dl_path)
    f = []      
    for file in os.listdir(f"{photo_dl_path}"):f.append(str(file))
    tdict[message.chat.id] = f"{photo_dl_path}/{f[-1]}"
    await message.reply_text(f"Custom Thumb Saved",reply_to_message_id=photo_msg.message_id,quote=True) 
  else:
    await message.reply_text(f"Not a Photo",quote=True)

@app.on_message(filters.command(["clrthumb"]) & filters.private)
async def thumb(client, message):
  user_id = message.chat.id
  global tdict
  if(user_id in tdict):
    tdict.pop(user_id)
    shutil.rmtree(f"downloads/{user_id}/")
    await message.reply_text("Thumbnail Cleared")
  else :
    await message.reply_text("No Custom Thumbnail Found")

@app.on_message(filters.command(["speedtest"]) & filters.private)
async def speedtest_cmd(client, message):
  await speedtst(client, message)
  
#on getting toggle msg
@app.on_message(filters.command(["toggle"]) & filters.private)
async def toggle(client, message):
  user_id = message.chat.id
  global upload_as_doc
  if user_id in upload_as_doc : 
    if upload_as_doc[user_id]: upload_as_doc[user_id] = False
    else : upload_as_doc[user_id] = True
  else:
    upload_as_doc[user_id] = False
  text = "**TOGGLE MENU:**\n[__Click to change__]\n\nVideo File Will be Uploaded as "
  if upload_as_doc[user_id]: text_append = "Document 📁"
  else: text_append = "Streamable 🎬"
  await app.send_message(user_id, text,reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text_append, callback_data="toggle"),InlineKeyboardButton("Close ❌", callback_data="close")]]))

#on getting link msg
@app.on_message(filters.command(["upload"]) & filters.private)
async def link(client, message,unzipflag = False):
  user_id = message.chat.id
  global q_link
  if user_id not in q_link : q_link[user_id] = []
  q_link[user_id].append(messageobj(message))
  q_link[user_id][-1].unzip = unzipflag
  if os.path.isdir(f"download/{user_id}") and len(q_link[user_id])>1:
      queue_msg = await app.send_message(user_id,f"Queue Added\nPENDING TASKS :{str(len(q_link[user_id])-1)}")
      await asyncio.sleep(5)
      await queue_msg.delete()
      return
  while len(q_link[user_id][:]) > 0 :
    obj = q_link[user_id][0]
    print("Download task is started ,size of Queue= ",len(q_link[user_id]))
    try:
      filepath,bot_msg = await dl_link(app,obj.message)
    except Exception as e:
      q_link[user_id].pop(0)
      return
    if(len(filepath)!= 0):
      if(obj.unzip):
        await unzip_and_upload(bot_msg,filepath,user_id)
      else:
        await upload(bot_msg, filepath, obj.message.chat.id)
      shutil.rmtree(f"download/{obj.message.chat.id}/")
    q_link[user_id].pop(0)
    print("Download Task is Done ,size of Queue = ",len(q_link[user_id]))

app.run()
