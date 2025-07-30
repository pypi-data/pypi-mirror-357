from telethon import (
    TelegramClient,
    events,
)

# Remember to use your own values from my.telegram.org!
api_id = 5462912
api_hash = (
    "cb2cc32eb88af00c3450193c7504d480"
)
client = TelegramClient(
    "anon", api_id, api_hash
)


@client.on(events.NewMessage)
async def handler(event):
    # event.input_chat may be None, use event.get_input_chat()
    chat = await event.get_input_chat()
    sender = await event.get_sender()
    buttons = await event.get_buttons()

    print(event.chat_id)
    print(event.message)
    # await client.send_message(-570374810, "message recieved")

    if hasattr(event.chat, "title"):
        if (
            event.chat.title
            == "VIP ( BSB+KSB)"
        ):
            notification_message = (
                "auto-forwarding from VIP ( BSB+KSB):"
                + event.chat.title
            )
            await client.send_message(
                -570374810,
                notification_message,
            )
            await client.send_message(
                -570374810,
                event.message,
            )


async def main():
    # Getting information about yourself
    me = await client.get_me()

    # "me" is a user object. You can pretty-print
    # any Telegram object with the "stringify" method:
    print(me.stringify())

    # When you print something, you see a representation of it.
    # You can access all attributes of Telegram objects with
    # the dot operator. For example, to get the username:
    username = me.username
    print(username)
    print(me.phone)

    # You can print all the dialogs/conversations that you are part of:
    async for (
        dialog
    ) in client.iter_dialogs():
        print(
            dialog.name,
            "has ID",
            dialog.id,
        )


with client:
    client.loop.run_forever()
