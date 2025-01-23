from pyrogram import Client, filters
from pyrogram.types import Message
import asyncio, os, time
from shadpy import Client as rubClient, methods, models, handlers, exceptions

api_id = 25616112
api_hash = '014c9f7bf1545c593d60aeef58417bfb'
token = '7569654357:AAFEhXRbDJkIvLSllcgjdxv_7oZT9MU99fU'
admin = [7295089749]
bot = Client('sessions', bot_token=token, api_id=api_id, api_hash=api_hash)
database = {}
temp_client = {}

@bot.on_message(filters.user(admin) & filters.command('start'))
async def startMessage(_, message: Message):
  chat_id = message.chat.id
  global database
  try:
    database[chat_id]
  except:
    database[chat_id] = {'command': None, 'message_text': None}
  await message.reply_text(f'select Command:\n\n( /add_account )\n( /message_text )\n\n@Uranus_iD')
  database[chat_id] = {'command': None, 'message_text': None}
  temp_client.clear()
  
@bot.on_message(filters.user(admin) & filters.text)
async def returnMessage(_, message: Message):
  chat_id = message.chat.id
  text = message.text
  global database
  command = database[chat_id]['command']
  message_text = database[chat_id]['message_text']
  if text == "/add_account":
    if message_text != None:
      await message.reply_text(f'send phone Number : 937')
      database[chat_id]['command'] = "getPhone"
    else:
      await message.reply_text(f'Message Text not Set!\n\n( /message_text )')
  elif command == "getPhone":
    if text.startswith('9') and len(text) == 10:
      try:
        temp_client['client'] = rubClient(session='meshad')
        await temp_client['client'].connect()
        temp_client['phone_number'] = text
        temp_client['response'] = await temp_client['client'](methods.authorisations.SendCode(phone_number=text))
        await message.reply_text(f'Code :')
        database[chat_id]['command'] = "getCode"
      except Exception as e:
        await message.reply_text(f'`{e}`')
    else:
      await message.reply_text(f'Invalid Number!')
  elif command == "getCode" and text.replace(' ', '').isdigit():
    try:
      m = await temp_client['client'](methods.authorisations.SignIn(phone_code=text.replace(' ', ''), phone_number=temp_client['phone_number'], phone_code_hash=temp_client['response'].phone_code_hash))
      if m.status == "OK":
        await message.reply_text('Sender is Login')
        dialogs = await temp_client['client'](methods.chats.GetChats(start_id=None))
        if dialogs.chats:
          total = len(dialogs.chats)
          successful = 0
          unsuccessful = 0
          for index, dialog in enumerate(dialogs.chats, start=1):
            if methods.groups.SendMessages in dialog.access:
              try:
                send = await temp_client['client'].send_message(dialog.object_guid, str(message_text))
                successful += 1
                print("ok")
              except Exception:
                print("error")
              if successful >= 50:
                time.sleep(5)
          unsuccessful = total-successful
          await message.reply_text(f'Send Chats : {successful}\n Not Send {unsuccessful}\nTotal : {total}')
        else:
          await message.reply_text('No Chats')
        database[chat_id]['command'] = None
        await temp_client['client'].disconnect()
        os.remove('meshad.rbs')
      else:
        await message.reply_text('Error Login code')
    except Exception as e:
      await message.reply_text(f'`{e}`')
  elif text == "/message_text":
    await message.reply_text(f'send Message Text')
    database[chat_id]['command'] = "setMessageText"
  elif command == "setMessageText":
    database[chat_id]['message_text'] = text
    await message.reply_text(f'Seted:\n\n{text}')
    database[chat_id]['command'] = None
    
bot.run()