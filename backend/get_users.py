import asyncio
from tortoise import Tortoise
from app.db.databases import TORTOISE_ORM
from app.models.users import User

async def run():
    await Tortoise.init(config=TORTOISE_ORM)
    users = await User.all().limit(5)
    for user in users:
        print(f"Email: {user.email}, Name: {user.name}")
    await Tortoise.close_connections()

if __name__ == "__main__":
    asyncio.run(run())
