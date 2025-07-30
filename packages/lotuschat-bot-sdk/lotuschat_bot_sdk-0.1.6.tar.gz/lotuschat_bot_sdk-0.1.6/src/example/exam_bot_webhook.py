from flask import Flask

from exam_const import TOKEN_STICKER_DOWNLOAD_BOT
from src.sdk.control import ChatBot
from src.sdk.control.bot import ChatBotListener
from src.sdk.model.data import Message
from src.sdk.utility.logger import log_verbose, log_debug, log_info


# Class testing
class Test:
    bot = ChatBot(
        name="Python Bot - Test message event",
        token=TOKEN_STICKER_DOWNLOAD_BOT
    )

    class HandlerListener(ChatBotListener):
        def on_message_raw_received(self, message: Message):
            log_info(f"receive message {message.update_id}")
            detail = message.messageDetail
            if detail:
                log_debug(f"{detail.from_user.username} send message: {detail.text}")
                log_verbose(detail)

        def on_message_received(self, chat_id: int, text: str):
            log_info(f"receive message {text} from {chat_id}")

        def on_command(self, command: int, args: list):
            log_info(f"receive command {command} with arguments {args}")

    def on_temp_command(self, args: list,chat_id: int, message: Message):
        log_info(f"function{self} handle temp command with arguments {args} from {chat_id}")
        log_debug(f"{message}")

    def run(self):
        log_info(f"create bot[{self}] to test send message")
        log_debug(self.bot)

        log_info("setting listener & receive message event")
        listener = self.HandlerListener()
        self.bot.set_listener(listener)
        self.bot.set_on_command("/temp", self.on_temp_command)


# Running
control = Test()

app = Flask(__name__)


@app.route("/", methods=["POST"])
def lc_webhook():
    return control.bot.web_hook()


if __name__ == "__main__":
    control.run()
    app.run(port=4800)
