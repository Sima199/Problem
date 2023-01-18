import discord
import asyncio
import time
import itertools
from discord.ext import commands
from youtube_dl import YoutubeDL
from discord.ext.commands import Bot
import nacl
import random
from discord import FFmpegPCMAudio, player
from discord.utils import get

# DO NOT TOUCH

songlist = []

def embedding(text: str):
  text= discord.Embed(
  description=f"**{text}**",
  color = 53380,
  )
  return(text)

YDL_OPTIONS = {'format': 'worstaudio/best', 'noplaylist': 'False', 'simulate': 'True',
               'preferredquality': '192', 'preferredcodec': 'mp3', 'key': 'FFmpegExtractAudio'}
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

config = {
    'token': 'MTA1OTE2ODYyMDMyNTkwMDQwOA.GXW3yA.xaNbQM8TGa36MjbQNgmYBF7ZgltaE0sGaQ9HPQ',
    'prefix': '$',
}

def txt():
    for i in range(0,1):
        txt1 = 'Будет сделано'
        txt2 = 'Ага'
        txt = random.choices([txt1,txt2], weights=[50, 50])
        i = i + 1
        return txt

# I N T E N T S
intents = discord.Intents(messages = True, guilds = True)
intents.guild_messages = True
intents.members = True
intents.message_content = True
intents.voice_states = True
intents.emojis_and_stickers = True
all_intents = intents.all()
all_intents= True

bot = commands.Bot(command_prefix=config['prefix'], intents = intents)

    # C O M M A N D S


# M U S I C A L

"Записывает в массив, берет из массива. Если трек .is_playing, то ждет окончания и начинает воспроизводить."


@bot.command()
async def play(ctx, *, arg):
    SuccText = embedding(txt()) #Текст при выполнении команды
    FailText = embedding('Уже') #Текст при выполнении команды

    voice_client = ctx.guild.voice_client
    try: #Заход в канал
        vc = await ctx.message.author.voice.channel.connect(self_deaf=True) #подключение к каналу
        if voice_client == None: #понятия не имею, я это украл и все заработало

            await ctx.send(embed=SuccText) #Успешное выполнение всех условий выше
            with YoutubeDL(YDL_OPTIONS) as ydl:
                if 'https://' in arg: #поиск в случае если трек запросили через ссылку
                    info = ydl.extract_info(arg, download=False)
                else: #поиск в случае если трек запросили через название трека
                    info = ydl.extract_info(f"ytsearch:{arg}", download=False)['entries'][0]

            url = info['formats'][0]['url']
            vc.play(discord.FFmpegPCMAudio(executable="ffmpeg", source=url, **FFMPEG_OPTIONS)) #проигрывание трека


    except discord.ClientException: # случай если бот уже в канале

        songlist.put(arg)

        if 'https://' in songlist:

            info = ydl.extract_info(songlist, download=False)

        else:

            info = ydl.extract_info(f"ytsearch:{songlist}", download=False)['entries'][0]

        urlnext = info['formats'][0]['url']

        vc.play(discord.FFmpegPCMAudio(executable="ffmpeg", source=urlnext, **FFMPEG_OPTIONS))

        songlist.get()

        await ctx.send(embed=FailText) #для проверки, что все работает


@bot.command()
async def stop(ctx):
    voice_client = ctx.guild.voice_client
    await voice_client.disconnect()

@bot.command()
async def join(ctx):
    channel = ctx.message.author.voice.channel
    voice = get(bot.voice_clients, guild=ctx.guild)
    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()

@bot.command()
async def pause(ctx):
    await ctx.voice_client.pause()

@bot.command()
async def resume(ctx):
    await ctx.voice_client.resume()

    # E T C

# S H I T/T E S T

@bot.command()
async def boom(ctx):
    await ctx.reply('boom', file=discord.File('boom.webp'))

# K I C K FROM SERVER

@bot.command()
async def kick(ctx, member: discord.Member):
 await member.kick()

# K I C K FROM VOICE

@bot.command()
async def kickvc(ctx, member: discord.Member):
    if member.is_connected():
        await member.move_to(None)
    else:
        await ctx.send(embed="Нет такого чубрика в голосовом")

# C L E A R LAST "N" MESSAGES

@bot.command()
async def clear(ctx, amount):
    try:
        if int(amount) > 0:
            if int(amount) < 10:
                await ctx.channel.purge(limit=int(amount))
                if int(amount) < 5:
                    text = embedding("Последние "+ str(amount) +" сообщения съебались в ужасе")
                    await ctx.send(embed=text, delete_after=10.0)
                else:
                    text = embedding("Последние " + str(amount) + " сообщений съебались в ужасе")
                    await ctx.send(embed=text, delete_after=10.0)
            else:
                text = embedding("Не, стока нельзя удалять, броу")
                await ctx.send(embed=text, delete_after=10.0)
        else:
            text = embedding("Значение 0 или меньше 0")
            await ctx.send(embed=text, delete_after=10.0)

    except ValueError:
        text = embedding("Значение не является числом")
        await ctx.send(embed=text, delete_after=10.0)


# R U N N I N G

bot.run(config['token'])