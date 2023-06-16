"""
VoiceFive, A Py-Cord Cog (Gear) Made to mange temp channels 

Main File | main.py
"""
import discord
from cogs.voice.Embeds import Embeds
from cogs.voice.Views import Views
from cogs.voice.DataBase import DataBase

db = DataBase()

# Change this for your own (IF YOU WANT)
DEFAULT_PERMISSIONS = discord.Permissions()
DEFAULT_PERMISSIONS.administrator = True

class Control(discord.Cog):
    def __init__(self, bot):
        self.bot: discord.Bot = bot
    
    temp_voice = discord.SlashCommandGroup(name="temp_voice", description="To manage temp channels on your server", guild_only=True, default_member_permissions=DEFAULT_PERMISSIONS)
    @temp_voice.command(name="setup",description="To setup temp channels on your server", guild_only=True)
    async def setup(self, ctx: discord.ApplicationContext):
        await ctx.response.defer()
        if isinstance(ctx.channel, discord.DMChannel):
            return await ctx.respond("You can't setup temp channels in DMs!")
        category = await ctx.guild.create_category(name="Temp Voice")
        channel = await category.create_voice_channel(name="Join To Create")
        await db.add_guild(guild_id=ctx.guild.id, vc_id=channel.id, vc_category_id=category.id, channel_limit=0, channel_bitrate=3,)
        return await ctx.respond(f"Done setup the temp voice channel, this is the {channel.mention}!")

    # -- Events -- #

    @discord.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(Views.Dropdown())
        print("Loadded Presistent View (Dropdown)")

    @discord.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        """This Function is called when a member joins or leaves a voice channel
            - This Func also intented to get refactored one day.
        """
        guild_settings = await db.get_guild(member.guild.id)
        before_channel = before.channel
        after_channel = after.channel
        if before_channel == after_channel: # Yes i know this is unuseful but expect anything from discord.
            return
        if before_channel and before_channel.id:
            if await db.get_channel(member.id, before_channel.id, member.guild.id):
                await db.delete_channel(member.id, before_channel.id, member.guild.id)
                await before_channel.delete()
        if after_channel and after_channel.id in map((lambda x: x[1] if x else []), guild_settings): # (Fixed) Possible error, the bot cant be able to work if the guild is using more then one config for the temps
            temp_channel = await after_channel.clone(name=f"{member.display_name}'s Voice")
            await member.move_to(temp_channel)
            await db.create_channel(member.id, temp_channel.id, member.guild.id)
            embed = Embeds.Panel(member=member)
            return await temp_channel.send(embed=embed, view=Views.Dropdown())

    @discord.Cog.listener()
    async def on_guild_channel_update(self, before: discord.abc.GuildChannel, after: discord.abc.GuildChannel):
        if not before.id in map((lambda x: x[1] if x else []), (await db.get_guild(before.guild.id))):
            return
        if not after.category:
            try:
                embed = Embeds.Warning()
                await after.send(f"{after.guild.owner.mention}", embed=embed)
            except:
                pass
            return await db.remove_guild(before.guild.id, before.id)
        else:
            return

    @discord.Cog.listener()
    async def on_guild_channel_delete(self, channel: discord.abc.GuildChannel):
        if not channel.id in await db.get_guilds(channel.guild.id):
            return
        return await db.remove_guild(channel.guild.id, channel.id)



# - Do You know What Girl Called "Lisa"?
# - No!


def setup(bot: discord.Bot):
    bot.add_cog(Control(bot))
