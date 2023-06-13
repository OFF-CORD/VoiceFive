import aiosqlite


database_file = 'voice.db' # mhm, i think json might be better :>
#                          ^^^^^^ following up to this point, i hate my ideas, fuck json ._.

# database tables: channels, guilds, rejected_users
# channels schema: CREATE TABLE "channels" ("user_id" INTEGER,"channel_id" INTEGER, "guild_id" INTEGER)
# guilds schema: CREATE TABLE "guilds" ("guild_id" INTEGER,"vc_id" INTEGER, "vc_category_id" INTEGER,"channel_limit" INTEGER, "channel_bitrate" INTEGER)
# rejected_users schema: CREATE TABLE "rejected_users" ("user_id" INTEGER,"channel_id" INTEGER, "guild_id" INTEGER)


class DataBase():
    """PREPARE YOURSELF TO SEE THE MOST DUMBEST CLASS EVER!""" # FIXME... pls :3
    def __init__(self):
        pass

    @classmethod
    async def get_guild(self, guild_id):
        async with aiosqlite.connect(database_file) as db:
            async with db.execute("SELECT * FROM guilds WHERE guild_id = ?", (guild_id,)) as cursor:
                return await cursor.fetchone()
    @classmethod
    async def create_channel(self, user_id, channel_id, guild_id):
        async with aiosqlite.connect(database_file) as conn:
            async with conn.execute("INSERT INTO channels VALUES (?,?,?)", (user_id, channel_id, guild_id)) as cursor:
                await conn.commit()
                return
    @classmethod
    async def delete_channel(self, user_id, channel_id, guild_id):
        async with aiosqlite.connect(database_file) as conn:
            async with conn.execute("DELETE FROM channels WHERE user_id = ? AND channel_id = ? AND guild_id = ?", (user_id, channel_id, guild_id)) as cursor:
                await conn.commit()
                return
    @classmethod
    async def get_channel(self, user_id, channel_id, guild_id):
        async with aiosqlite.connect(database_file) as conn:
            if not user_id:
                async with conn.execute("SELECT * FROM channels WHERE channel_id = ? AND guild_id = ?", (channel_id, guild_id,)) as cursor:
                    return await cursor.fetchone()
            else:
                async with conn.execute("SELECT * FROM channels WHERE user_id = ? AND channel_id = ? AND guild_id = ?", (user_id, channel_id, guild_id)) as cursor:
                    return await cursor.fetchone()

    @classmethod
    async def get_rejected_user(self, user_id, channel_id, guild_id):
        async with aiosqlite.connect(database_file) as conn:
            async with conn.execute("SELECT * FROM rejected_users WHERE user_id = ? AND channel_id = ? AND guild_id = ?", (user_id, channel_id, guild_id)) as cursor:
                return await cursor.fetchone()
    @classmethod
    async def add_user_to_rejected(self, user_id, channel_id, guild_id):
        async with aiosqlite.connect(database_file) as conn:
            async with conn.execute("INSERT INTO rejected_users VALUES (?,?,?)", (user_id, channel_id, guild_id)) as cursor:
                await conn.commit()
                return
    @classmethod
    async def remove_user_from_reject(self, user_id, channel_id, guild_id):
        async with aiosqlite.connect(database_file) as conn:
            async with conn.execute("DELETE FROM rejected_users WHERE user_id = ? AND channel_id = ? AND guild_id = ?", (user_id, channel_id, guild_id)) as cursor:
                await conn.commit()
                return

    @classmethod
    async def add_guild(self, guild_id, vc_id, vc_category_id, channel_limit, channel_bitrate):
        async with aiosqlite.connect(database_file) as conn:
            async with conn.execute("INSERT INTO guilds VALUES (?,?,?,?,?)", (guild_id, vc_id, vc_category_id, channel_limit, channel_bitrate)) as cursor:
                await conn.commit()
                return
    @classmethod
    async def remove_guild(self, guild_id, vc_id):
        async with aiosqlite.connect(database_file) as conn:
            async with conn.execute("DELETE FROM guilds WHERE guild_id = ? AND vc_id = ?", (guild_id, vc_id,)) as cursor:
                await conn.commit()
                return
    @classmethod
    async def get_guilds(self, guild_id):
        async with aiosqlite.connect(database_file) as conn:
            async with conn.execute("SELECT * FROM guilds WHERE guild_id = ?", (guild_id,)) as cursor:
                return await cursor.fetchall()