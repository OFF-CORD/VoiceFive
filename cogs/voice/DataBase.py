"""
Database Quering Helper For VoiceFive Cog

DataBaseUtil | DataBase.py

DataBase Info:
    ╚voice.db
        ║
        ╠═ channels
        ║   ╠═ user_id 
        ║   ╠═ channel_id
        ║   ╚═ guild_id
        ║
        ╠═ guilds
        ║   ╠═ guild_id
        ║   ╠═ vc_id
        ║   ╠═ vc_category_id
        ║   ╠═ channel_limit
        ║   ╚═ channel_bitrate
        ║
        ╚═ rejected_users <- Unused

"""
import aiosqlite

DATABASE_FILE = 'voice.db'

class DataBase():
    """PREPARE YOURSELF TO SEE THE MOST DUMBEST CLASS EVER!""" # FIXME...
    def __init__(self):
        pass
    
    @classmethod
    async def create_conn(self):
        return await aiosqlite.connect(DATABASE_FILE)

    @classmethod
    async def get_guild(self, guild_id):
        db = await self.create_conn()
        async with db.execute("SELECT * FROM guilds WHERE guild_id = ?", (guild_id,)) as cursor:
            return await cursor.fetchall()

    @classmethod
    async def create_channel(self, user_id, channel_id, guild_id):
        db = await self.create_conn()
        async with db.execute("INSERT INTO channels VALUES (?,?,?)", (user_id, channel_id, guild_id)):
            return await db.commit()

    @classmethod
    async def delete_channel(self, user_id, channel_id, guild_id):
        db = await self.create_conn()
        async with db.execute("DELETE FROM channels WHERE user_id = ? AND channel_id = ? AND guild_id = ?", (user_id, channel_id, guild_id)):
            return await db.commit()

    @classmethod
    async def get_channel(self, user_id, channel_id, guild_id):
        query, values = ("SELECT * FROM channels WHERE channel_id = ? AND guild_id = ?", (channel_id, guild_id,)) if not user_id else ("SELECT * FROM channels WHERE user_id = ? AND channel_id = ? AND guild_id = ?", (user_id, channel_id, guild_id))
        db = await self.create_conn()
        async with db.execute(query, values) as cursor:
            return await cursor.fetchone()

    @classmethod
    async def get_rejected_user(self, user_id, channel_id, guild_id):
        db = await self.create_conn()
        async with db.execute("SELECT * FROM rejected_users WHERE user_id = ? AND channel_id = ? AND guild_id = ?", (user_id, channel_id, guild_id)) as cursor:
            return await cursor.fetchone()

    @classmethod
    async def add_user_to_rejected(self, user_id, channel_id, guild_id):
        db = await self.create_conn()
        async with db.execute("INSERT INTO rejected_users VALUES (?,?,?)", (user_id, channel_id, guild_id)):
            return await db.commit()

    @classmethod
    async def remove_user_from_reject(self, user_id, channel_id, guild_id):
        db = await self.create_conn()
        async with db.execute("DELETE FROM rejected_users WHERE user_id = ? AND channel_id = ? AND guild_id = ?", (user_id, channel_id, guild_id)):
            return await db.commit()

    @classmethod
    async def add_guild(self, guild_id, vc_id, vc_category_id, channel_limit, channel_bitrate):
        db = await self.create_conn()
        async with db.execute("INSERT INTO guilds VALUES (?,?,?,?,?)", (guild_id, vc_id, vc_category_id, channel_limit, channel_bitrate)):
            return await db.commit()

    @classmethod
    async def remove_guild(self, guild_id, vc_id):
        db = await self.create_conn()
        async with db.execute("DELETE FROM guilds WHERE guild_id = ? AND vc_id = ?", (guild_id, vc_id,)):
            return await db.commit()
