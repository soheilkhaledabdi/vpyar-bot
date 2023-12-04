from pyrogram import Client



api_id = 29365133
api_hash = "722d0eb612a789286c0ed9966c473ddf"
bot_token = "6724802635:AAFA_s30tuoprHHjG9Gbf-Z6VJ4lDOVQo-4"
 
app = Client(
    "bot_test",
    api_id=api_id, 
    api_hash=api_hash,
    bot_token=bot_token,
    plugins=dict(root="plugins")
)

app.run()