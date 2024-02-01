import discord
from colorama import Fore


def setup(bot: discord.Bot):
    filename = "listeners"
    cog_file = "on_ready.py"
    try:
        bot.load_extension(f"cogs.{filename}.{cog_file[:-3]}")
        print(Fore.GREEN + f"[✅] Loaded {cog_file[:-3]} From {filename}")
    except Exception as e:
        print(Fore.RED + f"[❌] Failed to load {cog_file[:-3]} From {filename}")
        print(Fore.YELLOW + f"[❗] Error: {str(e)}")
