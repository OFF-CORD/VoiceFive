"""Database Quering Helper For VoiceFive."""
"""
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

DATABASE_FILE = "voice.db"

COMMIT = "commit"
FETCHONE = "fetchone"
FETCHALL = "fetchall"


class DataBase:
    """Pretty dumb `class` to handle the db calls"""

    def __init__(self):
        pass

    @classmethod
    async def create_conn(self):
        return await aiosqlite.connect(DATABASE_FILE)

    @classmethod
    async def execute(self, query: str, values: tuple, type: str):
        db = await self.create_conn()
        cr = await db.execute(query, values)
        return (
            await db.commit()
            if type == COMMIT
            else await cr.fetchone()
            if type == FETCHONE
            else await cr.fetchall()
        )

    @classmethod
    async def get_guild(self, guild_id):
        return await self.execute(
            query="SELECT * FROM guilds WHERE guild_id = ?",
            values=(guild_id,),
            type=FETCHALL,
        )

    @classmethod
    async def create_channel(self, user_id, channel_id, guild_id):
        return await self.execute(
            query="INSERT INTO channels VALUES (?,?,?)",
            values=(user_id, channel_id, guild_id),
            type=COMMIT,
        )

    @classmethod
    async def delete_channel(self, user_id, channel_id, guild_id):
        return await self.execute(
            query="DELETE FROM channels WHERE user_id = ? AND channel_id = ? AND guild_id = ?",
            values=(user_id, channel_id, guild_id),
            type=COMMIT,
        )

    @classmethod
    async def get_channel(self, user_id, channel_id, guild_id):
        query, values = (
            (
                "SELECT * FROM channels WHERE channel_id = ? AND guild_id = ?",
                (
                    channel_id,
                    guild_id,
                ),
            )
            if not user_id
            else (
                "SELECT * FROM channels WHERE user_id = ? AND channel_id = ? AND guild_id = ?",
                (user_id, channel_id, guild_id),
            )
        )
        return await self.execute(
            query=query,
            values=values,
            type=FETCHONE,
        )

    @classmethod
    async def get_rejected_user(self, user_id, channel_id, guild_id):
        return await self.execute(
            query="SELECT * FROM rejected_users WHERE user_id = ? AND channel_id = ? AND guild_id = ?",
            values=(user_id, channel_id, guild_id),
            type=FETCHONE,
        )

    @classmethod
    async def add_user_to_rejected(self, user_id, channel_id, guild_id):
        return await self.execute(
            query="INSERT INTO rejected_users VALUES (?,?,?)",
            values=(user_id, channel_id, guild_id),
            type=COMMIT,
        )

    @classmethod
    async def remove_user_from_reject(self, user_id, channel_id, guild_id):
        return await self.execute(
            query="DELETE FROM rejected_users WHERE user_id = ? AND channel_id = ? AND guild_id = ?",
            values=(user_id, channel_id, guild_id),
            type=COMMIT,
        )

    @classmethod
    async def add_guild(
        self, guild_id, vc_id, vc_category_id, channel_limit, channel_bitrate
    ):
        return await self.execute(
            query="INSERT INTO guilds VALUES (?,?,?,?,?)",
            values=(guild_id, vc_id, vc_category_id, channel_limit, channel_bitrate),
            type=COMMIT,
        )

    @classmethod
    async def remove_guild(self, guild_id, vc_id):
        return await self.execute(
            query="DELETE FROM guilds WHERE guild_id = ? AND vc_id = ?",
            values=(
                guild_id,
                vc_id,
            ),
            type=COMMIT,
        )
