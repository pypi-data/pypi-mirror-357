from flask import Flask

from example.exam_const import TOKEN_STICKER_DOWNLOAD_BOT
from sdk.control.bot import ChatBot
from sdk.control.bot import ChatBotListener
from sdk.model.data import Message
from sdk.utility.logger import log_verbose, log_debug, log_info


# Class testing
class Test:
    bot = ChatBot(
        name="Python Bot - Test message event",
        token=TOKEN_STICKER_DOWNLOAD_BOT
    )

    class HandlerListener(ChatBotListener):
        def on_message_received(self, message: Message):
            log_info(f"receive message {message.update_id}")
            detail = message.messageDetail
            if detail:
                log_debug(f"{detail.from_user.username} send message: {detail.text}")
                log_verbose(detail)

    def run(self):
        log_info(f"create bot[{self}] to test send message")
        log_debug(self.bot)

        log_info("setting listener & receive message event")
        listener = self.HandlerListener()
        self.bot.set_listener(listener)


# Running
control = Test()

app = Flask(__name__)


@app.route("/", methods=["POST"])
def lc_webhook():
    return control.bot.web_hook()


if __name__ == "__main__":
    control.run()
    app.run(port=4800)
