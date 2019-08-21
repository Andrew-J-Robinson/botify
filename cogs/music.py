'''
    File name: Music.py
    Author: Andrew Robinson
    Date Created: 8/3/2019
    Last Modified: 8/3/2019
    Python Version 3.6
'''

from bot import Bot

import discord
from discord.ext import commands
from discord.utils import get

import youtube_dl
import os
from os import system
import shutil
import urllib.request
import urllib.parse
import re

class Music(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.queues = {}                        # List to keep track of song numbers in queue
        self.embedColor = discord.Color.green() # Emedded messages will be styled with a green bar

# Command bot to queue next song
# -------------------------------------------------------------------------------
    @commands.command(pass_context=True)
    async def queue(self, ctx,* , url: str):

        '''
        Variables for use later
        "channel" is used to send messages to the general channel specifically
        "songName" is used inside messages to report the song that is playing
        "ydlOptions" configures the options for downloading the youtube audio
        '''
        channel = self.client.get_channel(592792914799624194)
        songName = url
        ydlOptions = {
            'format': 'bestaudio/best',
            'quiet': True,
            'outtmpl': queuePath,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',
            }],
        }

        # Create Queue directory
        queueInfile = os.path.isdir("./Queue")
        if queueInfile is False:
            os.mkdir("Queue")
        DIR = os.path.abspath(os.path.realpath("Queue"))
        queueNumber = len(os.listdir(DIR))
        queueNumber += 1
        addQueue = True
        while addQueue:
            if queueNumber in self.queues:
                queueNumber += 1
            else:
                addQueue = False
                self.queues[queueNumber] = queueNumber
        queuePath = os.path.abspath(os.path.realpath("Queue") + f"/song{queueNumber}.%(ext)s")

        # Check if play request is already in URL format
        if url.startswith("http://") or url.startswith("https://"):
            pass
        else:
            # If the requested string isn't in URL format, convert it to a usable YouTube URL
            queryString = urllib.parse.urlencode({"search_query" : url})
            htmlContent = urllib.request.urlopen("http://www.youtube.com/results?" + queryString)
            searchResults = re.findall(r'href=\"\/watch\?v=(.{11})', htmlContent.read().decode())
            url = "http://www.youtube.com/watch?v=" + searchResults[0]

        try:
            # Download the file from  the given url using the initialized options above
            with youtube_dl.YoutubeDL(ydlOptions) as ydl:
                print("Downloading audio file now\n")
                ydl.download([url])
        except RuntimeError:
            print("Fallback: youtube-dl doesn't support this link\n")
            q_path = os.path.abspath(os.path.realpath("Queue"))
            system(f"spotdl -ff song{queueNumber} -f " + '"' + q_path + '"' + " -s " + url)
        except:
            print("\nERROR: Song not found\n")
            await channel.send("I couldn't find that song, try queueing again with the title and artist typed out.")
            return

        embedTitle = (f"Added {songName} to the queue\n")
        embed = discord.Embed(title=embedTitle, colour=self.embedColor, url=url)
        embed.set_author(name=self.client.user.name, icon_url=self.client.user.avatar_url)
        embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
        print(f"{songName} added to the queue.")
        await channel.send(embed=embed)

        print("Song added to queue\n")

# Command bot to find youtube video and play audio
# ------------------------------------------------------------------------------
    @commands.command(pass_context=True)
    @commands.has_any_role('Owner', 'Admin', 'Member')
    async def play(self, ctx, *, url: str):


        # Variables for use later
        # "channel" is used to send messages to the general channel specifically
        # "ydlOptions" configures the options for downloading the youtube audio

        channel = self.client.get_channel(592792914799624194)
        ydlOptions = {
            'format': 'beat audio/best',
            'quiet': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',
            }],
        }

        # checkQueue() Checks to see if any songs are in the Queue directory.
        # If so, it moves the next queued song to the main directory and updates the queue count.

        def checkQueue():
            queueInfile = os.path.isdir("./Queue")
            if queueInfile is True:
                DIR = os.path.abspath(os.path.realpath("Queue"))
                length = len(os.listdir(DIR))
                queueCount = length - 1
                try:
                    firstFile = os.listdir(DIR)[0]
                except:
                    print("No more songs in queue\n")
                    self.queues.clear()
                    return
                mainLocation = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
                songPath = os.path.abspath(os.path.realpath("Queue") + "//" + firstFile)

                # If there are songs in the queue, process the next song:
                if length != 0:
                    print("Playing next song in queue\n")
                    print(f"Songs still in queue: {queueCount}\n")
                    songPresent = os.path.isfile("song.mp3")

                    # Remove the old song file:
                    if songPresent:
                        os.remove("song.mp3")

                    # Move the next song to main directory here:
                    shutil.move(songPath, mainLocation)

                    # Rename the file in the main directory "song.mp3" so the play command can play it:
                    for file in os.listdir("./"):
                        if not file.endswith("clip.mp3") and file.endswith(".mp3"):
                            os.rename(file, 'song.mp3')

                    # Check if the bot is connected to a voice channel. If it is, play the clip with FFmpeg:
                    if voice.is_connected():
                        voice.play(discord.FFmpegPCMAudio("song.mp3"), after=lambda e: checkQueue())
                        voice.source = discord.PCMVolumeTransformer(voice.source)
                        voice.source.volume = 0.5
                    else:
                        print("ERROR: Bot isn't connected to a voice channel.\n")
                else:
                    self.queues.clear()
                    return
            else:
                self.queues.clear()
                print("No songs were queued before the end of the last song\n")

        songPresent = os.path.isfile("song.mp3")
        try:
            # If song.mp3 is already present, remove it to be replaced by the next song:
            if songPresent:
                os.remove("song.mp3")
                self.queues.clear()
                print("Removed old song file\n")
        except PermissionError:
            print("ERROR to remove audio file: file is in use\n")
            await channel.send("ERROR: audio clip is playing.")
            return

        # Check to make sure there's no old Queue folder:
        queueInfile = os.path.isdir("./Queue")
        try:
            queueFolder = "./Queue"
            if queueInfile is True:
                print("Removed old Queue folder\n")
                shutil.rmtree(queueFolder)
        except:
            print("No old Queue folder\n")
        await channel.send("Getting everything ready now")

        # Initialize voice client:
        voice = get(self.client.voice_clients, guild=ctx.guild)

        # Check if play request is already in URL format
        if url.startswith("http://") or url.startswith("https://"):
            pass
        else: # If the requested string isn't in URL format, convert it to a usable YouTube URL
            queryString = urllib.parse.urlencode({"search_query" : url})
            htmlContent = urllib.request.urlopen("http://www.youtube.com/results?" + queryString)
            searchResults = re.findall(r'href=\"\/watch\?v=(.{11})', htmlContent.read().decode())
            url = "http://www.youtube.com/watch?v=" + searchResults[0]

        try:
            # Download the file from  the given url using the initialized options above:
            with youtube_dl.YoutubeDL(ydlOptions) as ydl:
                print("Downloading audio file now\n")
                ydl.download([url])
        except RuntimeError:
            print("Fallback: youtube-dl doesn't support this link\n")
            c_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
            # Execute spotdl shell comamnd:
            system("spotdl -f " + '"' + c_path + '"' + " -s " + url)
        except:
            print("\nERROR: Song not found\n")
            await channel.send("I couldn't find that song, try playing again with the title and artist typed out.")
            return

        # Check if the downloaded file is an mp3 and isn't the 'song.mp3' file used in another command:
        # If both pass, rename the downloaded file to 'clip.mp3':
        for file in os.listdir('./'):
            if not file.endswith("clip.mp3") and file.endswith(".mp3"):
                name = file
                os.rename(file, "song.mp3")
                print(f"Renamed file: {file}\n")

        # Check if the bot is connected to a voice channel. If it is, play the clip with FFmpeg:
        if voice.is_connected():
            try:
                voice.play(discord.FFmpegPCMAudio("song.mp3"), after=lambda e: checkQueue())
                voice.source = discord.PCMVolumeTransformer(voice.source)
                voice.source.volume = 0.5
            except:
                print("ERROR: Music is already playing")
                await channel.send("Music is already playing, queue that song instead.")
                return

        else:
            print("ERROR: Bot isn't connected to a voice channel.\n")

        try:
            newName = name.rsplit("-", 2)
            embedTitle = (f"Playing {newName[0]}")
            embed = discord.Embed(title=embedTitle, colour=self.embedColor, url=url)
            embed.set_author(name=self.client.user.name, icon_url=self.client.user.avatar_url)
            embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
            print(f"{newName[0]} playing\n")
            await channel.send(embed=embed)
        except:
            embedDescription = (f"Playing song.")
            embed = discord.Embed(title=embedDescription, colour=self.embedColor, url=url)
            embed.set_author(name=self.client.user.name, icon_url=self.client.user.avatar_url)
            embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
            print(f"{newName[0]} playing\n")
            await channel.send(embed=embed)

# Command bot to pause voice output
# -------------------------------------------------------------------------------
    @commands.command(pass_context=True)
    async def pause(self, ctx):

        # The bot will send messages to specified channel
        channel = self.client.get_channel(592792914799624194)


        voice = get(self.client.voice_clients, guild=ctx.guild)

        if voice and voice.is_playing():
            print("Music Paused\n")
            voice.pause()
            await channel.send("Music Paused")
        else:
            print("Music not playing: Failed pause\n")
            await channel.send("Music isn't playing")

# Command bot to resume voice output
# -------------------------------------------------------------------------------
    @commands.command(pass_context=True, aliases=['res'])
    async def resume(self, ctx):

        # The bot will send messages to specified channel
        channel = self.client.get_channel(592792914799624194)

        voice = get(self.client.voice_clients, guild=ctx.guild)
        if voice and voice.is_paused():
            print("Resuming Music\n")
            voice.resume()
            await channel.send("Resuming Music")
        else:
            print("Music is not paused\n")
            await channel.send("Music isn't paused")

# Command bot to stop voice output
# -------------------------------------------------------------------------------
    @commands.command(pass_context=True)
    async def stop(self, ctx):

        # The bot will send messages to specified channel
        channel = self.client.get_channel(592792914799624194)

        voice = get(self.client.voice_clients, guild=ctx.guild)

        self.queues.clear()

        queueInfile = os.path.isdir("./Queue")
        if queueInfile is True:
            shutil.rmtree("./Queue")

        if voice and voice.is_playing():
            print("Music Stopped\n")
            voice.stop()
            await channel.send("Music stopped.")
        else:
            print("Music not playing: Failed to Stop\n")
            await channel.send("Music isn't playing")

# Command bot to skip song in queue
# -------------------------------------------------------------------------------
    @commands.command(pass_context=True)
    async def skip(self, ctx):

        # The bot will send messages to specified channel
        channel = self.client.get_channel(592792914799624194)

        voice = get(self.client.voice_clients, guild=ctx.guild)

        if voice and voice.is_playing():
            print("Skipping song\n")
            voice.stop()
            await channel.send("Skipping song.")
        else:
            print("Music not playing: Failed to skip\n")
            await channel.send("Music isn't playing")

def setup(client):
    client.add_cog(Music(client))
