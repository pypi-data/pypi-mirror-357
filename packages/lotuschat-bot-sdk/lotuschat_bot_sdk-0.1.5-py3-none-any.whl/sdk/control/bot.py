from abc import abstractmethod, ABC

from flask import request

from ..model.data import Message
from ..utility.logger import log_info, log_warning

FAILED_REQUEST = "Api[{}] request failed. Error: {}}"
TYPE_BOT_COMMAND = "bot_command"

class ParseModeType:
    MARKDOWN = "Markdown"
    HTML = "HTML"

class ChatBotListener(ABC):
    @abstractmethod
    def on_message_raw_received(self, message: Message):  pass

    @abstractmethod
    def on_message_received(self, chat_id: int, text: str):  pass

    @abstractmethod
    def on_command(self, command: int, args: []):  pass

class ChatBot:
    _domain = "http://bot.lotuschat.vn/bot"
    _command_listeners = {}

    def __init__(self, name, token):
        self._listener = None
        self.name = name
        self.token = token

    def __str__(self):
        return f"Chatbot name[{self.name}] - token[{self.token}] - url[{self._domain}]"

    def set_listener(self, listener: ChatBotListener):
        log_info(f"running instance {self}")
        self._listener = listener

    def set_on_command(self, command: str, callback):
        log_info(f"register command {command}")
        self._command_listeners[command] = callback

    def web_hook(self):
        result_for_lc = "", 200
        result = request.get_json()
        if result:
            message = Message.from_dict(result)
            detail = message.messageDetail
            # verify message empty
            if detail is None:
                log_warning("empty message")
                return result_for_lc

            # send raw message
            text = detail.text
            if self._listener:
                log_info("send raw message")
                self._listener.on_message_raw_received(message=message)
                self._listener.on_message_received(chat_id=detail.chat.id, text=text)

            # check command message
            entities = detail.entities
            if entities is None:
                return result_for_lc
            is_command = None
            for entity in entities:
                if entity.get("type") == TYPE_BOT_COMMAND and entity.get("offset") == 0:
                    is_command = True
                    break
            if is_command:
                parts = text.strip().split()
                if not parts:
                    return result_for_lc
                command = parts[0]  # e.g. /send
                args = parts[1:]
                if self._listener:
                    self._listener.on_command(command=command, args= args)
                listener = self._command_listeners.get(command)
                if listener:
                    listener(args, detail.chat.id, message)

        return result_for_lc


    # interface message.py
    def get_messages(self, offset: int, limit: int):
        """Stub for IDE. Implemented in message.py."""
    def send_message(self, chat_id: int, text: str, parse_mode: str = "HTML", reply_id: int = None):
        """Stub for IDE. Implemented in message.py."""
    def send_document(self, chat_id: int, file_path: str, caption: str = None, reply_id: int = None):
        """Stub for IDE. Implemented in message.py."""
