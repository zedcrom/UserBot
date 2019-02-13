import bs4
import requests
import os
import re
import subprocess
import time
from datetime import datetime, timedelta

import urbandict
import wikipedia
from google_images_download import google_images_download
from googletrans import Translator
from gtts import gTTS
from telethon import TelegramClient, events

from userbot import LOGGER, LOGGER_GROUP, bot

langi = "en"


@bot.on(events.NewMessage(outgoing=True, pattern="^.img (.*)"))
@bot.on(events.MessageEdited(outgoing=True, pattern="^.img (.*)"))
async def img_sampler(e):
    if not e.text[0].isalpha() and e.text[0] not in ("/", "#", "@", "!"):
        await e.edit("Processing...")
        start = round(time.time() * 1000)
        s = e.pattern_match.group(1)
        lim = re.findall(r"lim=\d+", s)
        try:
            lim = lim[0]
            lim = lim.replace("lim=", "")
            s = s.replace("lim=" + lim[0], "")
        except IndexError:
            lim = 2
        response = google_images_download.googleimagesdownload()
        arguments = {
            "keywords": s,
            "limit": lim,
            "format": "jpg",
        }  # creating list of arguments
        paths = response.download(arguments)  # passing the arguments to the function
        lst = paths[s]
        await bot.send_file(await bot.get_input_entity(e.chat_id), lst)
        end = round(time.time() * 1000)
        msstartend = int(end) - int(start)
        await e.delete()


@bot.on(events.NewMessage(outgoing=True, pattern=r"^.google (.*)"))
@bot.on(events.MessageEdited(outgoing=True, pattern=r"^.google (.*)"))
async def gsearch(e):
    if not e.text[0].isalpha() and e.text[0] not in ("/", "#", "@", "!"):
        match = e.pattern_match.group(1)
        result_ = subprocess.run(["gsearch", match], stdout=subprocess.PIPE)
        result = str(result_.stdout.decode())
        await e.edit(
            "**Search Query:**\n`" + match + "`\n\n**Result:**\n" + result
        )
        if LOGGER:
            await bot.send_message(
                LOGGER_GROUP,
                "Google Search query " + match + " was executed successfully",
            )


@bot.on(events.NewMessage(outgoing=True, pattern=r"^.wiki (.*)"))
@bot.on(events.MessageEdited(outgoing=True, pattern=r"^.wiki (.*)"))
async def wiki(e):
    if not e.text[0].isalpha() and e.text[0] not in ("/", "#", "@", "!"):
        match = e.pattern_match.group(1)
        result = wikipedia.summary(match)
        await e.edit(
            "**Search:**\n`" + match + "`\n\n**Result:**\n" + result
        )
        if LOGGER:
            await bot.send_message(
                LOGGER_GROUP, "Wiki query " + match + " was executed successfully"
            )


@bot.on(events.NewMessage(outgoing=True, pattern="^.ud (.*)"))
@bot.on(events.MessageEdited(outgoing=True, pattern="^.ud (.*)"))
async def ud(e):
    if not e.text[0].isalpha() and e.text[0] not in ("/", "#", "@", "!"):
        await e.edit("Processing...")
        str = e.pattern_match.group(1)
        mean = urbandict.define(str)
        if len(mean) >= 0:
            await e.edit(
                "Text: **"
                + str
                + "**\n\nMeaning: **"
                + mean[0]["def"]
                + "**\n\n"
                + "Example: \n__"
                + mean[0]["example"]
                + "__"
            )
            if LOGGER:
                await bot.send_message(
                    LOGGER_GROUP, "ud query " + str + " executed successfully."
                )
        else:
            await e.edit("No result found for **" + str + "**")


@bot.on(events.NewMessage(outgoing=True, pattern="^.tts"))
@bot.on(events.MessageEdited(outgoing=True, pattern="^.tts"))
async def tts(e):
    if not e.text[0].isalpha() and e.text[0] not in ("/", "#", "@", "!"):
        textx = await e.get_reply_message()
        replye = e.text
        if replye[5:]:
            message = str(replye[5:])
        elif textx:
            message = textx
            message = str(message.message)
        current_time = datetime.strftime(datetime.now(), "%d.%m.%Y %H:%M:%S")
        tts = gTTS(message, langi)
        tts.save("k.mp3")
        with open("k.mp3", "rb") as f:
            linelist = list(f)
            linecount = len(linelist)
        if linecount == 1:
            try:  # tts on personal chats is broken
                tts = gTTS(message, langi)
                tts.save("k.mp3")
            except:
                await e.edit("`Some Internal Error! Try Again!`")
                return
        with open("k.mp3", "r") as speech:
            await bot.send_file(e.chat_id, "k.mp3", voice_note=True)
            os.remove("k.mp3")
            if LOGGER:
                await bot.send_message(
                    LOGGER_GROUP, "tts of " + message + " executed successfully!"
                )
            await e.delete()


@bot.on(events.NewMessage(outgoing=True, pattern="^.trt"))
@bot.on(events.MessageEdited(outgoing=True, pattern="^.trt"))
async def translateme(e):
    if not e.text[0].isalpha() and e.text[0] not in ("/", "#", "@", "!"):
        global langi
        translator = Translator()
        textx = await e.get_reply_message()
        message = e.text
        if message[4:]:
            message = str(message[4:])
        elif textx:
            message = textx
            message = str(message.message)
        reply_text = translator.translate(message, dest=langi).text
        reply_text = "**Source:** `\n" + message + "**\n\nTranslation: **\n" + reply_text
        await bot.send_message(e.chat_id, reply_text)
        await e.delete()
        if LOGGER:
            await bot.send_message(
                LOGGER_GROUP,
                "Translate query " + message + " was executed successfully",
            )


@bot.on(events.NewMessage(pattern=".lang", outgoing=True))
@bot.on(events.MessageEdited(pattern=".lang", outgoing=True))
async def lang(e):
    if not e.text[0].isalpha() and e.text[0] not in ("/", "#", "@", "!"):
        global langi
        message = await bot.get_messages(e.chat_id)
        langi = str(message[0].message[6:])
        if LOGGER:
            await bot.send_message(
                LOGGER_GROUP, "tts language changed to **" + langi + "**"
            )
            await e.edit("tts language changed to **" + langi + "**")

@bot.on(events.NewMessage(outgoing=True,pattern='.imdb (.*)'))
@bot.on(events.MessageEdited(outgoing=True,pattern='.imdb (.*)'))
async def imdb(e):
    movie_name = e.pattern_match.group(1)
    remove_space = movie_name.split(' ')
    final_name = '+'.join(remove_space)
    page = requests.get("https://www.imdb.com/find?ref_=nv_sr_fn&q="+final_name+"&s=all")
    lnk = str(page.status_code)
    soup = bs4.BeautifulSoup(page.content,'lxml')
    odds = soup.findAll("tr","odd")
    mov_title = odds[0].findNext('td').findNext('td').text
    mov_link = "http://www.imdb.com/"+odds[0].findNext('td').findNext('td').a['href'] 
    page1 = requests.get(mov_link)
    soup = bs4.BeautifulSoup(page1.content,'lxml')
    if soup.find('div','poster'):
    	poster = soup.find('div','poster').img['src']
    else:
    	poster = ''
    if soup.find('div','title_wrapper'):
    	pg = soup.find('div','title_wrapper').findNext('div').text
    	mov_details = re.sub(r'\s+',' ',pg)
    else:
    	mov_details = ''
    credits = soup.findAll('div', 'credit_summary_item')
    if len(credits)==1:
    	director = credits[0].a.text
    	writer = 'Not available'
    	stars = 'Not available'
    elif len(credits)>2:
    	director = credits[0].a.text
    	writer = credits[1].a.text
    	actors = []
    	for x in credits[2].findAll('a'):
    		actors.append(x.text)
    	actors.pop()
    	stars = actors[0]+','+actors[1]+','+actors[2]
    else:
    	director = credits[0].a.text
    	writer = 'Not available'
    	actors = []
    	for x in credits[1].findAll('a'):
    		actors.append(x.text)
    	actors.pop()
    	stars = actors[0]+','+actors[1]+','+actors[2]	 
    if soup.find('div', "inline canwrap"):
    	story_line = soup.find('div', "inline canwrap").findAll('p')[0].text
    else:
    	story_line = 'Not available'
    info = soup.findAll('div', "txt-block")
    if info:
    	mov_country = []
    	mov_language = []
    	for node in info:
    		a = node.findAll('a')
    		for i in a:
    			if "country_of_origin" in i['href']:
    				mov_country.append(i.text)
    			elif "primary_language" in i['href']:
    				mov_language.append(i.text) 
    if soup.findAll('div',"ratingValue"):
    	for r in soup.findAll('div',"ratingValue"):
    		mov_rating = r.strong['title']
    else:
    	mov_rating = 'Not available'
    await e.edit('<a href='+poster+'>&#8203;</a>'
    			'<b>Title : </b><code>'+mov_title+
    			'</code>\n<code>'+mov_details+
    			'</code>\n<b>Rating : </b><code>'+mov_rating+
    			'</code>\n<b>Country : </b><code>'+mov_country[0]+
    			'</code>\n<b>Language : </b><code>'+mov_language[0]+
    			'</code>\n<b>Director : </b><code>'+director+
    			'</code>\n<b>Writer : </b><code>'+writer+
    			'</code>\n<b>Stars : </b><code>'+stars+
    			'</code>\n<b>IMDB Url : </b>'+mov_link+
    			'\n<b>Story Line : </b>'+story_line,
    			link_preview = True , parse_mode = 'HTML'
    			)
