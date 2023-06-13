import discord
import aiosqlite
from colorama import Fore
from prettytable import PrettyTable


database_file = 'voice.db'

querys = ["""
CREATE TABLE IF NOT EXISTS channels (
    user_id INTEGER,
    channel_id INTEGER,
    guild_id INTEGER
);
""",
"""
CREATE TABLE IF NOT EXISTS guilds (
    guild_id INTEGER,
    vc_id INTEGER,
    vc_category_id INTEGER,
    channel_limit INTEGER,
    channel_bitrate INTEGER
);
""",
"""
CREATE TABLE IF NOT EXISTS rejected_users (
    user_id INTEGER,
    channel_id INTEGER,
    guild_id INTEGER
);

""",]

class ReadyListener(discord.Cog):
    def __init__(self, bot):
        self.bot: discord.Bot = bot
    
    @discord.Cog.listener()
    async def on_ready(self):
        for query in querys:
            async with aiosqlite.connect(database_file) as conn:
                async with conn.execute(query) as cursor:
                    await conn.commit()
        guilds_count = len(self.bot.guilds)
        bot_data = await self.bot.application_info()
        owner: discord.User = bot_data.owner
        table = PrettyTable()
        table.field_names = ["Bot User", "Bot ID", "Owner User", "Owner ID", "Guild Count"]
        table.add_row([f"{self.bot.user}", f"{self.bot.user.id}", f"{owner}", f"{owner.id}", f"{guilds_count}"])
        print(Fore.CYAN, table)
        print("Logged In Successfully")
        
def setup(bot: discord.Bot):
    bot.add_cog(ReadyListener(bot))
        
    