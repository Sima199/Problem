import asyncio

import discord
from discord.ext import commands
from discord import Colour
from youtube_dl import YoutubeDL
import random
from asyncio.queues import Queue
from discord.utils import get

# DO NOT TOUCH


YDL_OPTIONS = {
    'format': 'worstaudio/best',
    'noplaylist': 'False',
    'simulate': 'True',
    'preferredquality': '192',
    'preferredcodec': 'mp3',
    'key': 'FFmpegExtractAudio'
}
FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}
API_TOKEN = 'MTA1OTE2ODYyMDMyNTkwMDQwOA.GXW3yA.xaNbQM8TGa36MjbQNgmYBF7ZgltaE0sGaQ9HPQ'

OKS = [
    'Будет сделано',
    'Ага',
    'Окей',
    'Угу',
    'Понятненько',
]


def ok():
    return random.choice(OKS)


def embedding(text: str, color=Colour.blue()):
    return discord.Embed(
        description=f"**{text}**",
        color=color,
    )


# I N T E N T S
intents = discord.Intents(
    messages=True,
    guilds=True,
    guild_messages=True,
    members=True,
    message_content=True,
    voice_states=True,
    emojis_and_stickers=True,
)

bot = commands.Bot(command_prefix='$', intents=intents)

# C O M M A N D S


playlist = Queue()


def run_playlist(voice_client):
    async def loop():
        # тут мы просто ждем очередной трек из очереди и проигрываем его
        while True:
            next_song = await playlist.get()
            voice_client.play(
                discord.FFmpegPCMAudio(
                    source=next_song,
                    **FFMPEG_OPTIONS
                ))

    return loop


# M U S I C A L


def is_url(text: str):
    return text.strip().startswith('https://')


def get_song_url(song_title):
    if not is_url(song_title):
        song_title = f"ytsearch:{song_title}"
    with YoutubeDL(YDL_OPTIONS) as ydl:
        info = ydl.extract_info(song_title, download=False)
    return info['formats'][0]['url']


@bot.command()
async def play(ctx, *, song_title):
    voice = get(bot.voice_clients, guild=ctx.guild)
    if not voice.is_connected():
        ctx.send(embedding("Бот не подключен к голосовому чату", Colour.red()))
        return

    next_song = get_song_url(song_title)
    await playlist.put(next_song)
    ctx.send(embedding(ok(), Colour.green()))


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
    # тут мы запускаем в бэкграунде проигрывание треков их очереди
    asyncio.create_task(
        run_playlist(voice)
    )



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
                    text = embedding("Последние " + str(amount) + " сообщения съебались в ужасе")
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

bot.run(API_TOKEN)
