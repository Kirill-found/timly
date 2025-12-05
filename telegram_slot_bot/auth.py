from pyrogram import Client
import asyncio

app = Client("stars_userbot",
    api_id=28668805,
    api_hash="5bd18c34314bf74adfd2066dcc21b2bb")

async def auth():
    await app.start()
    me = await app.get_me()
    print(f"Авторизован как: {me.first_name}")
    await app.stop()

asyncio.run(auth())