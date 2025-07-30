from src.example.exam_const import TOKEN_STICKER_DOWNLOAD_BOT, CHAT_ID_SINGLE, CHAT_ID_GROUP
from src.sdk.control import ChatBot
from src.sdk.utility.logger import log_debug, log_info

class Test:
    bot = ChatBot(
        name="Python Bot - Test message event",
        token=TOKEN_STICKER_DOWNLOAD_BOT
    )

    def run(self):
        log_info("send message to person")
        self.bot.send_message(
            chat_id=CHAT_ID_SINGLE,
            text="python bot send message to person"
        )

        log_info("send message to group")
        self.bot.send_message(
            chat_id=CHAT_ID_GROUP,
            text="python bot send message to group"
        )

Test().run()