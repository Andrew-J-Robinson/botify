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
        self.queues = {}

#Command bot to queue next song
#-------------------------------------------------------------------------------

    @commands.command(pass_context=True)
    async def queue(self, ctx,* , url: str):
        #Create queue directory
        Queue_infile = os.path.isdir("./Queue")
        if Queue_infile is False:
            os.mkdir("Queue")
        DIR = os.path.abspath(os.path.realpath("Queue"))
        q_num = len(os.listdir(DIR))
        q_num += 1
        add_queue = True
        while add_queue:
            if q_num in self.queues:
                q_num += 1
            else:
                add_queue = False
                self.queues[q_num] = q_num

        queue_path = os.path.abspath(os.path.realpath("Queue") + f"/song{q_num}.%(ext)s")

        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'outtmpl': queue_path,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

        #Check if play request is already in URL format
        if url.startswith("http://") or url.startswith("https://"):
            pass
        else: #If the requested string isn't in URL format, convert it to a usable YouTube URL
            query_string = urllib.parse.urlencode({"search_query" : url})
            html_content = urllib.request.urlopen("http://www.youtube.com/results?" + query_string)
            search_results = re.findall(r'href=\"\/watch\?v=(.{11})', html_content.read().decode())
            url = "http://www.youtube.com/watch?v=" + search_results[0]

        try:
            #Download the file from  the given url using the initialized options above
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                print("Downloading audio file now\n")
                ydl.download([url])
        except RuntimeError:
            print("Fallback: youtube-dl doesn't support this link\n")
            q_path = os.path.abspath(os.path.realpath("Queue"))
            system(f"spotdl -ff song{q_num} -f " + '"' + q_path + '"' + " -s " + url)
        except:
            print("\nERROR: Song not found\n")
            await ctx.send("I couldn't find that song, try queueing again with the title and artist typed out.")
            return

        newName = name.rsplit("-", 2)
        embedTitle = (f"Added {newName[0]} to the queue\n")
        embed = discord.Embed(title=embedTitle, colour=embedColor, url=url)
        embed.set_author(name=self.client.user.name, icon_url=self.client.user.avatar_url)
        embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
        print(f"{newName[0]} added to the queue.")
        await ctx.send(embed=embed)

        print("Song added to queue\n")

#Command bot to find youtube video and play audio
#------------------------------------------------------------------------------
    @commands.command(pass_context=True)
    @commands.has_any_role('Owner', 'Admin', 'Member')
    async def play(self, ctx, *, url: str):
        embedColor = discord.Color.green()
        def check_queue():
            Queue_infile = os.path.isdir("./Queue")
            if Queue_infile is True:
                DIR = os.path.abspath(os.path.realpath("Queue"))
                length = len(os.listdir(DIR))
                still_q = length - 1
                try:
                    first_file = os.listdir(DIR)[0]
                except:
                    print("No more songs in queue\n")
                    self.queues.clear()
                    return
                main_location = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
                song_path = os.path.abspath(os.path.realpath("Queue") + "//" + first_file)
                if length != 0:
                    print("Playing next song in queue\n")
                    print(f"Songs still in queue: {still_q}\n")
                    song_there = os.path.isfile("song.mp3")
                    if song_there:
                        os.remove("song.mp3")
                    shutil.move(song_path, main_location)
                    for file in os.listdir("./"):
                        if not file.endswith("clip.mp3") and file.endswith(".mp3"):
                            os.rename(file, 'song.mp3')

                    if voice.is_connected(): #Check if the bot is connected to a voice channel. If it is, play the clip with FFmpeg
                        voice.play(discord.FFmpegPCMAudio("song.mp3"), after=lambda e: check_queue())
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


        song_there = os.path.isfile("song.mp3")
        try:
            if song_there: #If song.mp3 is already present, remove it to be replaced by the next song
                os.remove("song.mp3")
                self.queues.clear()
                print("Removed old song file\n")
        except PermissionError:
            print("ERROR to remove audio file: file is in use\n")
            await ctx.send("ERROR: audio clip is playing.")
            return

        #Check to make sure there's no old Queue folder
        Queue_infile = os.path.isdir("./Queue")
        try:
            Queue_folder = "./Queue"
            if Queue_infile is True:
                print("Removed old Queue folder\n")
                shutil.rmtree(Queue_folder)
        except:
            print("No old Queue folder\n")

        await ctx.send("Getting everything ready now")
        voice = get(self.client.voice_clients, guild=ctx.guild)#Initialize voice client

        #Sets youtube_dl options
        ydl_opts = {
            'format': 'beat audio/best',
            'quiet': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',
            }],
        }

        #Check if play request is already in URL format
        if url.startswith("http://") or url.startswith("https://"):
            pass
        else: #If the requested string isn't in URL format, convert it to a usable YouTube URL
            query_string = urllib.parse.urlencode({"search_query" : url})
            html_content = urllib.request.urlopen("http://www.youtube.com/results?" + query_string)
            search_results = re.findall(r'href=\"\/watch\?v=(.{11})', html_content.read().decode())
            url = "http://www.youtube.com/watch?v=" + search_results[0]

        try:
            #Download the file from  the given url using the initialized options above
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                print("Downloading audio file now\n")
                ydl.download([url])
        except RuntimeError:
            print("Fallback: youtube-dl doesn't support this link\n")
            c_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
            system("spotdl -f " + '"' + c_path + '"' + " -s " + url)
        except:
            print("\nERROR: Song not found\n")
            await ctx.send("I couldn't find that song, try playing again with the title and artist typed out.")
            return

        #Check if the downloaded file is an mp3 and isn't the 'song.mp3' file used in another command
        #If both pass, rename the downloaded file to 'clip.mp3'
        for file in os.listdir('./'):
            if not file.endswith("clip.mp3") and file.endswith(".mp3"):
                name = file
                os.rename(file, "song.mp3")
                print(f"Renamed file: {file}\n")

        if voice.is_connected(): #Check if the bot is connected to a voice channel. If it is, play the clip with FFmpeg
            try:
                voice.play(discord.FFmpegPCMAudio("song.mp3"), after=lambda e: check_queue())
                voice.source = discord.PCMVolumeTransformer(voice.source)
                voice.source.volume = 0.5
            except:
                print("ERROR: Music is already playing")
                await ctx.send("Music is already playing, queue that song instead.")
                return

        else:
            print("ERROR: Bot isn't connected to a voice channel.\n")

        try:
            newName = name.rsplit("-", 2)
            embedTitle = (f"Playing {newName[0]}")
            embed = discord.Embed(title=embedTitle, colour=embedColor, url=url)
            embed.set_author(name=self.client.user.name, icon_url=self.client.user.avatar_url)
            embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
            print(f"{newName[0]} playing\n")
            await ctx.send(embed=embed)
        except:
            embedDescription = (f"Playing song.")
            embed = discord.Embed(title=embedDescription, colour=embedColor, url=url)
            embed.set_author(name=self.client.user.name, icon_url=self.client.user.avatar_url)
            embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
            print(f"{newName[0]} playing\n")
            await ctx.send(embed=embed)

#Command bot to pause voice output
#-------------------------------------------------------------------------------
    @commands.command(pass_context=True)
    async def pause(self, ctx):
        voice = get(self.client.voice_clients, guild=ctx.guild)

        if voice and voice.is_playing():
            print("Music Paused\n")
            voice.pause()
            await ctx.send("Music Paused")
        else:
            print("Music not playing: Failed pause\n")
            await ctx.send("Music isn't playing")

#Command bot to resume voice output
#-------------------------------------------------------------------------------
    @commands.command(pass_context=True, aliases=['res'])
    async def resume(self, ctx):
        voice = get(self.client.voice_clients, guild=ctx.guild)
        if voice and voice.is_paused():
            print("Resuming Music\n")
            voice.resume()
            await ctx.send("Resuming Music")
        else:
            print("Music is not paused\n")
            await ctx.send("Music isn't paused")

#Command bot to stop voice output
#-------------------------------------------------------------------------------
    @commands.command(pass_context=True)
    async def stop(self, ctx):
        voice = get(self.client.voice_clients, guild=ctx.guild)

        self.queues.clear()

        Queue_infile = os.path.isdir("./Queue")
        if Queue_infile is True:
            shutil.rmtree("./Queue")

        if voice and voice.is_playing():
            print("Music Stopped\n")
            voice.stop()
            await ctx.send("Music stopped.")
        else:
            print("Music not playing: Failed to Stop\n")
            await ctx.send("Music isn't playing")

#Command bot to skip song in queue
#-------------------------------------------------------------------------------
    @commands.command(pass_context=True)
    async def skip(self, ctx):
        voice = get(self.client.voice_clients, guild=ctx.guild)

        if voice and voice.is_playing():
            print("Skipping song\n")
            voice.stop()
            await ctx.send("Skipping song.")
        else:
            print("Music not playing: Failed to skip\n")
            await ctx.send("Music isn't playing")

def setup(client):
    client.add_cog(Music(client))
