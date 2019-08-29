'''
    File name: control.py
    Author: Andrew Robinson
    Date Created: 8/3/2019
    Last Modified: 8/3/2019
    Python Version 3.6
'''

from bot import Bot

import discord
from discord.ext import commands
from discord.utils import get

class Control(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.acceptedChannel = self.client.get_channel(610881900365479963)

    # Command bot to join voice channel
    # ---------------------------------
    @commands.command(pass_context=True)
    @commands.has_any_role('Owner', 'Admin')
    async def join(self, ctx):
        if ctx.channel != self.acceptedChannel:
            global voice
            channel = ctx.message.author.voice.channel
            voice = get(self.client.voice_clients, guild=ctx.guild)

            if voice and voice.is_connected():
                await voice.move_to(channel)
                await ctx.send("I'm already in your voice channel.")
            else:
                voice = await channel.connect()
                print(f"Botify has connected to {channel}\n")
                await ctx.channel.purge(limit = 1)
        else:
            print("ERROR: A user attempted to send a command sin an unsupported channel")
            await channel.send("'''#send-bot-commands-here'''")

    # Command bot to leave voice channel
    # ----------------------------------
    @commands.command(pass_context=True)
    @commands.has_any_role('Owner', 'Admin')
    async def leave(self, ctx):
        if ctx.channel != self.acceptedChannel:
            channel = ctx.message.author.voice.channel
            voice = get(self.client.voice_clients, guild=ctx.guild)

            if voice and voice.is_connected():
                await ctx.channel.purge(limit = 1)
                await voice.disconnect()
                print(f"The bot has left {channel}\n")
            else:
                print("Leave command failed: Bot not in channel\n")
                await ctx.send("I must be in your voice channel to leave.")
        else:
            print("ERROR: A user attempted to send a command sin an unsupported channel")
            await channel.send("'''#send-bot-commands-here'''")

def setup(client):
    client.add_cog(Control(client))
