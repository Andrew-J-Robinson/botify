'''
    File name: main.py
    Author: Andrew Robinson
    Date Created: 7/31/2019
    Last Modified: 7/31/2019
    Python Version 3.6
'''

from bot import Bot

import discord
from discord.ext import commands
from discord.utils import get

def main():

    tokenFile = open("token.txt", 'r')
    TOKEN = tokenFile.read().replace('\n', '')
    tokenFile.close()

    botify = Bot(TOKEN, '/')

    botify.run()

#------------------------------------------------------------------------------

main()
