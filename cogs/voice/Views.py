"""
Views Helpers For VoiceFive Main File

Views | Views.py
"""
# import json
# import os
# import time
from cogs.voice.DataBase import DataBase
from cogs.voice.Embeds import Embeds
import asyncio
import discord
from discord.ext import commands

db = DataBase()

class Views():
    def __init__(self):
        pass
    class UserSelector(discord.ui.View):
        """You'll need to clean up your eyes from this view"""
        def __init__(self, user: discord.Member, edit_user: discord.Member):
            self.user = user
            self.edit_user: discord.Member = edit_user
            super().__init__()

        @discord.ui.select(placeholder="Select something to do with this user",
                            options=[discord.SelectOption(label="Disconnct", description="Disconnect the user from this channel", value="disconnect"),
                                    discord.SelectOption(label="Mute", description="Mute this user from talking", value="mute"),
                                    discord.SelectOption(label="Reject", description="Reject this user from joining the channel", value="reject"),
                                    discord.SelectOption(label="Hide", description="Hide this channel from this user", value="hide")
                                ]
                            )
        async def edit_member_callback(self, select: discord.ui.Select, interaction: discord.Interaction):
            await interaction.response.defer() # DO THIS SHIT.. PLS
            selected = select.values[0]
            # -- Placeholder -- #
            if selected == "reject":
                params: discord.PermissionOverwrite = interaction.channel.overwrites_for(self.edit_user)
                params.connect = False
                await interaction.channel.set_permissions(target=self.edit_user, overwrite=params, reason="This user has been rejected by the temp owner.")
                msg = await interaction.original_response()
                await interaction.respond(content=f"The Member {self.edit_user.mention} has been rejected.", view=None, delete_after=5)
                if self.edit_user.voice and self.edit_user.voice.channel.id == interaction.channel_id: # (Fixed) Possible Error "NoneType Has No attr"
                    # If the user alr on the channel, kick it out
                    return await self.edit_user.move_to(None)
                else:
                    # otherwise continue
                    return

            if selected == "hide":
                params: discord.PermissionOverwrite = interaction.channel.overwrites_for(self.edit_user)
                params.view_channel = False
                await interaction.channel.set_permissions(target=self.edit_user, overwrite=params, reason="This channel has been hidden from this user by the temp owner.")
                await interaction.respond(content=f"The Channel has been hidden for the user {self.edit_user.mention}.", view=None, delete_after=5)
                if self.edit_user.voice.channel.id == interaction.channel_id:
                    return await self.edit_user.move_to(None)
                else:
                    return

            # -- Placeholder -- #

            # Return statements if the edit gonna need the selected user to be on vc
            if not self.edit_user.voice:
                    return await interaction.respond("This user is not connected to this voice channel.", ephemeral=True)
            elif not self.edit_user.voice.channel.id == interaction.channel_id:
                return await interaction.respond("This user is not connected to this voice channel.", ephemeral=True)

            # -- command's / interactions requires a vc connected -- #

            if selected == "disconnect":
                await self.edit_user.move_to(None)
                return await interaction.respond(content=f"The Member {self.edit_user.mention} has been disconnected.", view=None, delete_after=5)

            if selected == "mute":
                # this one actully break my mind for how its working 
                # since when you edit a user permissions (mute it)
                # the user should to reconnect to get effected ;-;
                this_channel = (await interaction.guild.fetch_channel(int(interaction.channel.id)))
                params: discord.PermissionOverwrite = this_channel.overwrites_for(self.edit_user)
                if params.speak or params.speak is None:
                    params.speak = False
                    await interaction.channel.set_permissions(target=self.edit_user, overwrite=params, reason="This user has been muted by the temp owner.")
                    msg = await interaction.original_response()
                    await self.edit_user.move_to(interaction.channel) # BRUHHHH.. it works 😭
                    return await msg.edit(content=f"The Member {self.edit_user.mention} has been muted.", view=None, delete_after=5)
                else:
                    params.speak = None
                    await interaction.channel.set_permissions(target=self.edit_user, overwrite=params, reason="This user has been unmuted by the temp owner.")
                    msg = await interaction.original_response()
                    await self.edit_user.move_to(interaction.channel)
                    return await msg.edit(content=f"The Member {self.edit_user.mention} has been unmuted.", view=None, delete_after=5)



    class Dropdown(discord.ui.View):
        """question about the class name?, bruh"""
        def __init__(self):
            super().__init__(timeout=None)
            self.cooldown = commands.CooldownMapping.from_cooldown(1, 600, commands.BucketType.member)

        @discord.ui.select(custom_id="channel_settings",
                           placeholder="Select a channel option",
                           options=[discord.SelectOption(label="Info", description="Displays Info about this temp voice", value="info"),
                                    discord.SelectOption(label="Delete", description="To delete this temp voice", value="delete"),
                                    discord.SelectOption(label="Name", description="To Change this channel Name", value="name"),
                                    discord.SelectOption(label="Limit", description="To Change this channel users limit", value="limit"),
                                    discord.SelectOption(label="Slow Mode", description="To Set/Edit this channel users slow-mode/cooldown", value="slow_mode"),
                                    discord.SelectOption(label="NSFW", description="To Mark this channel as not safe for work (+18)", value="nsfw"),
                                    discord.SelectOption(label="Lock", description="To Lock this channel with it's users", value="lock"),
                                    discord.SelectOption(label="Hide", description="To Hide this channel and only users inside will be able to see it", value="hide"),
                                    discord.SelectOption(label="Bitrate", description="To Change this channel bitrate", value="bitrate"),
                                    discord.SelectOption(label="Clear", description="To Clear up this channel Messages", value="clear"),],
                                )
        async def settings_callback(self, select: discord.ui.Select, interaction: discord.Interaction):
            await interaction.message.edit(content=interaction.message.content, view=self)

            selected = select.values[0]
            
            # -- Interactions will responded with Modal Views
            
            channel_data = await db.get_channel(None, interaction.channel_id, interaction.guild_id)
            if selected == "name":
                bucket = self.cooldown.get_bucket(interaction.message)
                retry = bucket.update_rate_limit()
                if retry:
                    return await interaction.response.send_message(f"Changing Channel Names Have a 10min Cooldown, Try again in `{round(retry, 1)}` seconds.", ephemeral=True)
                modal = discord.ui.Modal(title="Channel Name")
                modal.add_item(discord.ui.InputText(label="New Channel Name", placeholder="Please enter the new channel name", value=interaction.channel.name))
                async def modal_callback(interaction: discord.Interaction):
                    await interaction.response.defer()
                    # print(interaction.data["components"][0]["components"][0]["value"]) # why i was thinking about this 🤨
                    channel_name = modal.children[0].value # FIXME
                    if channel_name.isspace():
                        channel_name = f"{interaction.channel.user_limit}"
                    await interaction.channel.edit(name=channel_name)
                    msg = await interaction.respond(f"Done, Channel Name has been changed to {channel_name}", ephemeral=True)
                    await asyncio.sleep(5)
                    try:
                        return await msg.delete()
                    except:
                        return
                modal.callback = modal_callback
                return await interaction.response.send_modal(modal=modal)

            elif selected == "limit":
                modal = discord.ui.Modal(title="Channel Limit")
                modal.add_item(discord.ui.InputText(label="New Channel Limit", placeholder="Please enter the new channel limit (0 for unlimited)", value=interaction.channel.user_limit))
                async def modal_callback(interaction: discord.Interaction):
                    await interaction.response.defer()
                    channel_limit = modal.children[0].value
                    if not channel_limit.isnumeric():
                        return await interaction.respond(f"Please Input a Valid Number!", ephemeral=True, delete_after=5)
                    await interaction.channel.edit(user_limit=int(channel_limit))
                    return await interaction.respond(f"Done, Channel User Limit has been changed to {'Unlimited' if int(channel_limit) == 0 else channel_limit}", ephemeral=True, delete_after=5)
                modal.callback = modal_callback
                return await interaction.response.send_modal(modal=modal)

            elif selected == "bitrate":
                channel_bits = int(str(int(interaction.guild.bitrate_limit))[:-3]) # Bro wtf is this butt-shit?
                placeholder = f"From 8 To {channel_bits}"
                modal = discord.ui.Modal(title="Channel Bitrate")
                modal.add_item(discord.ui.InputText(label="Channel Bitrate Value", placeholder=placeholder, value=interaction.channel.user_limit))
                async def modal_callback(interaction: discord.Interaction):
                    await interaction.response.defer()
                    modal_value = modal.children[0].value
                    if not modal_value.isnumeric():
                        return await interaction.respond(f"Please Input a Valid Number!", ephemeral=True, delete_after=5)
                    elif int(modal_value) > channel_bits or int(modal_value) < 8:
                        return await interaction.respond(f"Please Input a Valid Number Between 8 and {str(channel_bits)}", ephemeral=True, delete_after=5)
                    await interaction.channel.edit(bitrate=(int(modal_value) * 1000))
                    return await interaction.respond(f"Done, Channel Bitrate has been Changed To {modal_value}", ephemeral=True, delete_after=5)
                modal.callback = modal_callback
                return await interaction.response.send_modal(modal=modal)
            
            # -- #
            await interaction.response.defer()
            # -- #
            if selected == "info": # No idea for adding owner check for this.. right?
                channel: discord.VoiceChannel = await interaction.guild.fetch_channel(int(interaction.channel_id))
                embed = Embeds.Info(interaction=interaction, channel=channel, channel_data=channel_data)
                return await interaction.respond(embed=embed)

            if not interaction.user.id in channel_data:
                return await interaction.respond("This Option is not available for you, only channel owner", ephemeral=True, delete_after=5)

            if selected == "delete":
                return await interaction.user.move_to(None) # maw :>, uh hell, if this bad for you 

            elif selected == "slow_mode":
                view = discord.ui.View(timeout=300)
                dropdown = discord.ui.Select(placeholder="Please Select a Cooldown Period",
                                             options=[
                                                 discord.SelectOption(label="off", value="0"),
                                                 discord.SelectOption(label="5s", value="5"),
                                                 discord.SelectOption(label="10s", value="10"),
                                                 discord.SelectOption(label="15s", value="15"),
                                                 discord.SelectOption(label="30s", value="30"),
                                                 discord.SelectOption(label="1m", value="60"),
                                                 discord.SelectOption(label="2m", value="120"),
                                                 discord.SelectOption(label="5m", value="300"),
                                                 discord.SelectOption(label="10m", value="600"),
                                                 discord.SelectOption(label="15m", value="900"),
                                                 discord.SelectOption(label="30m", value="1800"),
                                                 discord.SelectOption(label="1h", value="3600"),
                                                 discord.SelectOption(label="2h", value="7200"),
                                                 discord.SelectOption(label="6h", value="21600"),
                                                 ]
                                             )
                view.add_item(dropdown)
                async def slow_mode_select_callback(interaction: discord.Interaction):
                    slowmode_delay = int(dropdown.values[0])
                    await interaction.response.defer()
                    await interaction.channel.edit(slowmode_delay=slowmode_delay)
                    msg = await interaction.original_response()
                    return await msg.edit(f"Done, Slow Mode Has been Changed", view=None, delete_after=5)
                dropdown.callback = slow_mode_select_callback
                return await interaction.respond("Select Slowmode Delay From This DropDown", view=view, ephemeral=True, delete_after=300)

            elif selected == "nsfw":
                if interaction.channel.nsfw:
                    await interaction.channel.edit(nsfw=False)
                    return await interaction.respond(f"Done, Channel has been unMarked as NSFW", ephemeral=True, delete_after=5)
                else:
                    await interaction.channel.edit(nsfw=True)
                    return await interaction.respond(f"Done, Channel has been Marked as NSFW", ephemeral=True, delete_after=5)

            elif selected == "lock":
                this_channel = (await interaction.guild.fetch_channel(int(interaction.channel.id)))
                everyone_perms = this_channel.permissions_for(interaction.guild.default_role)
                overwrite_perms = this_channel.overwrites
                # Channel if it's on cache the updates done after bot restart, kinda bad but this is necessary to not fuck your momery
                if everyone_perms.connect:
                    for member in interaction.channel.members:
                        perms: discord.Permissions = interaction.channel.overwrites_for(member)
                        perms.connect = True
                        await interaction.channel.set_permissions(target=member, overwrite=perms, reason="This user has acsess to this channel by the temp owner.")
                    role = interaction.guild.default_role
                    perms = interaction.channel.overwrites_for(role)
                    perms.connect = False
                    await interaction.channel.set_permissions(target=role, overwrite=perms, reason="This user has no acsess to this channel by the temp owner.")
                    return await interaction.respond(f"Done, Channel has been locked successfully", ephemeral=True, delete_after=5)
                else:
                    for perm in overwrite_perms:
                        overwrite = interaction.channel.overwrites_for(perm)
                        overwrite.connect = None
                        await interaction.channel.set_permissions(target=perm, overwrite=overwrite)
                    return await interaction.respond(f"Done, Reverted to locked", ephemeral=True, delete_after=5)

            elif selected == "hide":
                this_channel = (await interaction.guild.fetch_channel(int(interaction.channel.id)))
                everyone_perms = this_channel.permissions_for(interaction.guild.default_role)
                overwrite_perms = this_channel.overwrites
                # ^^ you got the point above
                if everyone_perms.view_channel:
                    for member in interaction.channel.members:
                        perms: discord.Permissions = interaction.channel.overwrites_for(member)
                        perms.view_channel = True
                        await interaction.channel.set_permissions(target=member, overwrite=perms, reason="This channel has been hidden by the temp owner.")
                    role = interaction.guild.default_role
                    perms = interaction.channel.overwrites_for(role)
                    perms.view_channel = False
                    await interaction.channel.set_permissions(target=role, overwrite=perms, reason="This user has no acsess to this channel by the temp owner.")
                    return await interaction.respond(f"Done, Channel has been hidden successfully", ephemeral=True, delete_after=5)
                else:
                    for perm in overwrite_perms:
                        overwrite = interaction.channel.overwrites_for(perm)
                        overwrite.view_channel = None
                        await interaction.channel.set_permissions(target=perm, overwrite=overwrite, reason="")
                    return await interaction.respond(f"Done, Reverted to unhidden", ephemeral=True, delete_after=5)

            elif selected == "clear":
                btn_view = discord.ui.View()
                btn = discord.ui.Button(style=discord.ButtonStyle.danger, label="Yes")
                async def btn_view_callback(interaction: discord.Interaction):
                    await interaction.response.defer()
                    check = lambda m: not m.author.id == interaction.client.user.id # TODO: smth better
                    await interaction.channel.purge(limit=500, check=check)
                    return await interaction.edit_original_response(content="Done!", view=None, delete_after=5)
                btn.callback = btn_view_callback
                btn2 = discord.ui.Button(style=discord.ButtonStyle.green, label="No")
                async def btn2_view_callback(interaction: discord.Interaction):
                    await interaction.response.defer()
                    return await interaction.delete_original_response()
                btn2.callback = btn2_view_callback
                btn_view.add_item(btn)
                btn_view.add_item(btn2)
                return await interaction.respond(f"Are you sure you want to continue?", ephemeral=True, view=btn_view)


        @discord.ui.select(custom_id="activity",
                           placeholder="Select To Start an Activity",
                           options=[
                               discord.SelectOption(label="Watch Together", value="watch_together"),
                               discord.SelectOption(label="Poker Night", value="poker_night"),
                               discord.SelectOption(label="Jamspace", value="jamspace"),
                               discord.SelectOption(label="Putt Party", value="putt_party"),
                               discord.SelectOption(label="Gartic Phone", value="gartic_phone"),
                               discord.SelectOption(label="Know What I Meme", value="know_what_i_meme"),
                               discord.SelectOption(label="Chess In The Park", value="chess_in_the_park"),
                               discord.SelectOption(label="Bobble League", value="bobble_league"),
                               discord.SelectOption(label="Land", value="land"),
                               discord.SelectOption(label="Sketch Heads", value="sketch_heads"),
                               discord.SelectOption(label="Blazing 8s", value="blazing_8s"),
                               discord.SelectOption(label="SpellCast", value="spell_cast"),
                               discord.SelectOption(label="Checkers In The Park", value="checkers_in_the_park"),
                               discord.SelectOption(label="Letter League", value="letter_league"),
                           ])
        async def activites_callback(self, select: discord.ui.Select, interaction: discord.Interaction):
            await interaction.response.defer()
            await interaction.message.edit(content=interaction.message.content, view=self)
            channel_data = await db.get_channel(None, interaction.channel_id, interaction.guild_id)
            if not interaction.user.id in channel_data:
                return await interaction.respond("This Option is not available for you, only channel owner", ephemeral=True, delete_after=5)
            invite = await interaction.channel.create_activity_invite(discord.EmbeddedActivity[select.values[0]])
            return await interaction.respond(f"The User {interaction.user.mention} Has Created This Activity Invite_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍_‍{invite}")
            #                                                                                                      ^^^^^^^ discord ☕


        @discord.ui.select(select_type=discord.ComponentType.user_select, placeholder="Select a User to edit it", custom_id="member_settings")
        async def view_callback(self, select: discord.ui.Select, interaction: discord.Interaction):
            await interaction.response.defer()
            # the interaction will kinda take some time, so i'll defer it until it get a response
            await interaction.message.edit(content=interaction.message.content, view=self)
            # NOTE: when you respond to the interaction (with anything) then you should use a follow up interaction-webhook to resume the interaction messages
            # also yeah, the interaction-followup is a webhook message, and its permissions are same as the @everyone, so yeah discord fucked it up for us!

            # -- "cool placeholder :>?" -- #

            if await db.get_channel(interaction.user.id, interaction.channel_id, interaction.guild_id):
                selected_user = select.values[0]
                if selected_user.id == interaction.user.id:
                    return await interaction.respond("You can't edit yourself 🗿", ephemeral=True, delete_after=5)
                elif selected_user.id == interaction.client.user.id:
                    return await interaction.respond("You can't edit me bro 💀", ephemeral=True, delete_after=5)
                elif selected_user.id == interaction.guild.owner_id:
                    return await interaction.respond("So, actually you want to get banned 🗿, you're trying to edit the owner?, lol", ephemeral=True, delete_after=5)
                # -- Done from the goofy ahh return messages 💀 -- #
                if not selected_user.guild:
                    return await interaction.respond("This user is not a member of this guild.", ephemeral=True, delete_after=5)
                elif selected_user.bot:
                    return await interaction.respond(f"Dear {interaction.user.mention}, if you have that thing called \"Eyes ✨\" you will be able to see that user is a bot!", ephemeral=True, delete_after=5)
                    # better way? :>
                await interaction.respond("Select an option to edit this user.", view=Views.UserSelector(user=interaction.user, edit_user=selected_user), ephemeral=True)
            else:
                return await interaction.respond("You are not this channel owner.", ephemeral=True, delete_after=5)


# bruh, typically i typed everything without internet connection, all the thank to egypt
# ~~when it back i'll start a debugging session, i mean no code start working from the first time lol~~ <- it was kinda works ;3
