import discord
import os

bot = discord.Bot(intents=discord.Intents.all())

def load_cogs():
    for folder in os.listdir("cogs"):
        if not "." in folder:
            bot.load_extension(f"cogs.{folder}.__init__")


load_cogs()

# DONT FORGET TO EDIT THIS
bot.run("TOKEN")
