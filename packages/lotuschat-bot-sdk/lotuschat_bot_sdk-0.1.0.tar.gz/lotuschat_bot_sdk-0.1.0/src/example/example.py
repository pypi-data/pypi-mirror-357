from src.sdk import ChatBot

token_verify_api_bot = "6443221:BdbRzOPPCDCwh7Fi7M3PeSSv9gkoSdTiJLWJf7u7"
token_sticker_download_bot = "6091897:nLXBSHjyhvksecdvq1IlQN8OZNQ7jQjvDFDP22yd"

single_chat_id = 777005
group_chat_id = -2226446

bot = ChatBot(
    name="Python Bot",
    token=token_sticker_download_bot
)
print(bot)
bot.send_message(
    chat_id=single_chat_id,
    text="python bot send message"
)
