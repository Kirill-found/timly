import asyncio
from pyrogram import Client
import os
from dotenv import load_dotenv

load_dotenv()

async def main():
    app = Client(
        os.getenv("SESSION_NAME", "stars_userbot"),
        api_id=int(os.getenv("API_ID")),
        api_hash=os.getenv("API_HASH"),
        phone_number=os.getenv("PHONE_NUMBER")
    )

    async with app:
        me = await app.get_me()
        print(f"✅ UserBot запущен как @{me.username if me.username else me.first_name}")
        await app.send_message("me", "UserBot готов к работе!")
        print("Отправлено тестовое сообщение")

if __name__ == "__main__":
    asyncio.run(main())
