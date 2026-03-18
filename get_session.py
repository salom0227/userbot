from telethon.sync import TelegramClient
from telethon.sessions import StringSession

api_id = 38747645
api_hash = "d2d51ce0d95dbc1fdd2bfd5b7752fc72"

with TelegramClient(StringSession(), api_id, api_hash) as client:
    print("\n\nSESSION STRING:\n")
    print(client.session.save())
    print("\n")
