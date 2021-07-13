import os

import discord
from discord.ext import tasks, commands
from dotenv import load_dotenv

from ocr_flame import *

from datetime import datetime
import shutil
import requests
import quiz

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

#client = discord.Client()
client = commands.Bot(command_prefix = '!')
calloutquiz = quiz.Quiz(client)


@tasks.loop(seconds=10)
async def mvp_reminder():
    channel = client.get_channel(857216166656868393)
    server = client.get_guild(289460846222901259)

    role1 = discord.utils.get(server.roles, name="MVP :00 :30")
    role2 = discord.utils.get(server.roles, name="MVP :15 :45")

    now = datetime.now().time()
    minute = now.minute
    second = now.second
    if (minute == 59 or minute == 29) and second >= 20 and second <= 29:
        await channel.send(role1.mention + " Go to MVP now", delete_after=30)
    if (minute == 14 or minute == 44) and second >= 20 and second <= 29:
        await channel.send(role2.mention + " Go to MVP now", delete_after=30)


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    await mvp_reminder.start()

@client.event
async def on_message(message):
    if calloutquiz is not None and calloutquiz.started():
        #check if we have a question pending
        await calloutquiz.answer_question(message)
        #check quiz question correct

    await client.process_commands(message)

@client.command(aliases=['halt'])
async def stop(ctx):
    await calloutquiz.stop()

@client.command()
async def reset(ctx):
    await calloutquiz.reset() 

@client.command(aliases=['start', 'callouts'])
async def quiz(ctx, *args):
    await calloutquiz.start(ctx.message.channel, args) 

@client.command(aliases=['score'])
async def scores(ctx):
    await calloutquiz.print_scores() 

@client.command()
async def next(ctx):
    await calloutquiz.next_question(ctx.message.channel)

@client.command()
async def flame(ctx):
    if len(ctx.message.attachments) > 0:
        for attachment in ctx.message.attachments:
            if is_Image(attachment):
                url = attachment.url
                response = requests.get(url, stream=True)
                with open('img.png', 'wb') as out_file:
                    shutil.copyfileobj(response.raw, out_file)
                del response

                text = ocr_core("img.png")
                os.remove("img.png")
                
                flame = parse(text)
                if is_valid_image(flame):
                    flameScore = flame.flame_score()
                    format_float = "{:.2f}".format(flameScore)
                    embed = discord.Embed()
                    embed.add_field(name="__**Flame Stats**__", value=flame.flame_stats(), inline=False)
                    embed.add_field(name="__**Flame Score**__", value=format_float, inline=False)
                    embed.add_field(name="__**Flame Recommendation**__", value=flame.flame_recommendation(), inline=False)
                    await ctx.send(embed=embed)
                else:
                    await ctx.send("Please ensure that the image you are sending is of a maplestory item")
            else:
                await ctx.send("Please send this command together with an image of a maplestory item")
    else:
        await ctx.send("Please send this command together with an image of a maplestory item")
                    

@client.command()
async def commandhelp(ctx):
    embed = discord.Embed()
    embed.add_field(name="__**!flame**__", value="Returns the flame profile of a maplestory item", inline=False)
    embed.add_fied(name="__**!callouts**__", value="Starts a multiplayer quiz for rainbow six siege callouts", inline=False)
    await ctx.send(embed=embed)

client.run(TOKEN)
