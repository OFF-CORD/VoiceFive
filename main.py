import discord
import os

bot = discord.Bot(intents=discord.Intents.all())

def load_cogs():
    # Loading the cogs like this kinda better O.O
    [bot.load_extension(f"cogs.{folder}.__init__") for folder in os.listdir("cogs") if not "." in folder]


load_cogs()

# DONT FORGET TO EDIT THIS
bot.run("TOKEN")
