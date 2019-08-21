'''
    File name: bot.py
    Author: Andrew Robinson
    Date Created: 8/3/2019
    Last Modified: 8/3/2019
    Python Version 3.6
'''

import discord
from discord.ext import commands
import os

class Bot:
    def __init__(self, TOKEN, CHAR):
        self.token = TOKEN
        self.prefix = CHAR
        self.client = commands.Bot(command_prefix = self.prefix)

    def run(self):

        # Connect to cogs folder
        # ----------------------
        @self.client.command()
        @commands.has_permissions(administrator=True)
        async def load(ctx, extension):
            self.client.load_extension(f'cogs.{extension}')

        @self.client.command()
        @commands.has_permissions(administrator=True)
        async def unload(ctx, extension):
            self.client.unload_extension(f'cogs.{extension}')

        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                self.client.load_extension(f'cogs.{filename[:-3]}')

        @self.client.event
        async def onReady():
            print(self.client.user.name + " is online.\n")

        self.client.run(self.token)
