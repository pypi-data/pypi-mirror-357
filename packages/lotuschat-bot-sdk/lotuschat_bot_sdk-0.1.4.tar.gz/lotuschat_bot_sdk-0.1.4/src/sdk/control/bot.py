from abc import abstractmethod, ABC

from flask import request

from sdk.model.data import Message
from sdk.utility.logger import log_info

FAILED_REQUEST = "Api[{}] request failed. Error: {}}"


class ChatBotListener(ABC):
    @abstractmethod
    def on_message_received(self, message: Message):
        pass

class ChatBot:
    domain = "http://bot.lotuschat.vn/bot"

    def __init__(self, name, token):
        self._listener = None
        self.name = name
        self.token = token

    def __str__(self):
        return f"Chatbot name[{self.name}] - token[{self.token}] - url[{self.domain}]"

    def set_listener(self, listener: ChatBotListener):
        log_info(f"Running instance {self}")
        self._listener = listener

    def web_hook(self):
        result = request.get_json()
        if result:
            message = Message.from_dict(result)
            if self._listener:
                self._listener.on_message_received(message=message)
        return "", 200

    # interface message.py
    def get_messages(self, offset: int, limit: int):
        """Stub for IDE. Implemented in message.py."""
    def send_message(self, chat_id: int, text: str, parse_mode: str = "HTML"):
        """Stub for IDE. Implemented in message.py."""
    def send_document(self, chat_id: int, file_path: str, caption: str = None):
        """Stub for IDE. Implemented in message.py."""
