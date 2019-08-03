from bot import Bot

import discord
from discord.ext import commands
from discord.utils import get

class Control(commands.Cog):

    def __init__(self, client):
        self.client = client

    #Command bot to join voice channel
    #---------------------------------
    @commands.command(pass_context=True)
    @commands.has_any_role('Owner', 'Admin')
    async def join(self, ctx):
        global voice
        channel = ctx.message.author.voice.channel
        voice = get(self.client.voice_clients, guild=ctx.guild)

        if voice and voice.is_connected():
            await voice.move_to(channel)
            await ctx.send("I'm already in here, dummy.")
        else:
            voice = await channel.connect()
            print(f"The bot has connected to {channel}\n")
            await ctx.channel.purge(limit = 1)
            await ctx.send("Sup, nerds?")

    #Command bot to leave voice channel
    #----------------------------------
    @commands.command(pass_context=True)
    @commands.has_any_role('Owner', 'Admin')
    async def leave(self, ctx):
        channel = ctx.message.author.voice.channel
        voice = get(self.client.voice_clients, guild=ctx.guild)

        if voice and voice.is_connected():
            await ctx.channel.purge(limit = 1)
            await voice.disconnect()
            print(f"The bot has left {channel}\n")
            await ctx.send("I'm out this mf.")
        else:
            print("Leave command failed: Bot not in channel\n")
            await ctx.send("You tryna kick me out and I'm not even in here?")

def setup(client):
    client.add_cog(Control(client))
