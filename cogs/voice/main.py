"""A Py-Cord Cog (Gear) Made to mange temp channels"""
import discord
from cogs.voice.Views import Views
from cogs.voice.DataBase import DataBase

class Control(discord.Cog):
    def __init__(self, bot):
        self.bot: discord.Bot = bot

    @discord.slash_command(name="setup",description="To setup temp channels on your server", guilds_only=True)
    @discord.default_permissions(administrator=True)
    async def setup(self, ctx: discord.ApplicationContext):
        await ctx.response.defer()
        category = await ctx.guild.create_category(name="Temp Voice")
        channel = await category.create_voice_channel(name="Join To Create")
        await DataBase.add_guild(guild_id=ctx.guild.id, vc_id=channel.id, vc_category_id=category.id, channel_limit=0, channel_bitrate=3,)
        return await ctx.respond(f"Done setup the temp voice channel, this is the {channel.mention}!")
        
    # -- Events -- #        

    @discord.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        guild_settings = await DataBase.get_guild(member.guild.id)
        before_channel = before.channel
        after_channel = after.channel
        if before_channel == after_channel: # Yes i know this is unuseful but expect anything from discord.
            return
        if before_channel and before_channel.id:
            if await DataBase.get_channel(member.id, before_channel.id, member.guild.id):
                await DataBase.delete_channel(member.id, before_channel.id, member.guild.id)
                await before_channel.delete()

        if after_channel and after_channel.id in guild_settings:
            temp_channel = await after_channel.clone(name=f"{member.display_name}'s Voice")
            await member.move_to(temp_channel)
            await DataBase.create_channel(member.id, temp_channel.id, member.guild.id)
            return await temp_channel.send(f"{member.mention} has created this channel", view=Views.Dropdown())
        
    @discord.Cog.listener()
    async def on_guild_channel_update(self, before: discord.abc.GuildChannel, after: discord.abc.GuildChannel):
        if not before.id in await DataBase.get_guild(before.guild.id):
            return
        if not after.category:
            try:
                await after.send(f"""{before.guild.owner.mention}, Please resetup your server temp channels\n- To edit the temp channel parant you can just edit its name/prefrences or anything\n- To change the temp channel category you can just place it at any category but **DO NOT** let it without category.""")
            except:
                pass
            return await DataBase.remove_guild(before.guild.id, before.id)
        else:
            return
        
    @discord.Cog.listener()
    async def on_guild_channel_delete(self, channel: discord.abc.GuildChannel):
        if not channel.id in await DataBase.get_guilds(channel.guild.id):
            return
        return await DataBase.remove_guild(channel.guild.id, channel.id)




# - Do You know What Girl Called "Lisa"?
# - No!


def setup(bot: discord.Bot):
    bot.add_cog(Control(bot))
    


# future: <Task finished name='discord-ui-view-timeout-bf49781d1cdd9d809357153cab8832ad' coro=<View.on_timeout() done, defined at D:\FokeTheBot_final\.venv\Lib\site-packages\discord\ui\view.py:364> exception=NotFound('404 Not Found (error code: 10003): Unknown Channel')>
# Traceback (most recent call last):
#   File "D:\V5\.venv\Lib\site-packages\discord\ui\view.py", line 373, in on_timeout
#     m = await message.edit(view=self)
#         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "D:\V5\.venv\Lib\site-packages\discord\message.py", line 1479, in edit
#     data = await self._state.http.edit_message(
#            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "D:\V5\.venv\Lib\site-packages\discord\http.py", line 367, in request
#     raise NotFound(response, data)
# discord.errors.NotFound: 404 Not Found (error code: 10003): Unknown Channel

# The following tracebacks happen when i use disable in timeout.
