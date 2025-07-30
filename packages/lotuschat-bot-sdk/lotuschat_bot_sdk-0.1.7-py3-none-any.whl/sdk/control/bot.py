from abc import abstractmethod, ABC

from flask import request

from ..model.data import Message
from ..utility.logger import log_info, log_warning

FAILED_REQUEST = "Api[{}] request failed. Error: {}}"
TYPE_BOT_COMMAND = "bot_command"


class ParseModeType:
    MARKDOWN = "Markdown"
    HTML = "HTML"


class ChatBot:
    TYPE_GET_ALL_MESSAGE = "/lotuschat_bot_get_all_message"
    TYPE_GET_ALL_MESSAGE_WITHOUT_COMMAND = "/lotuschat_bot_get_all_message_without_command"
    TYPE_GET_ALL_COMMAND = "/lotuschat_bot_get_all_command"

    _domain = "http://bot.lotuschat.vn/bot"
    _command_listeners = {}

    def __init__(self, name, token):
        self.name = name
        self.token = token

    def __str__(self):
        return f"Chatbot name[{self.name}] - token[{self.token}] - url[{self._domain}]"

    def set_on_messages(self, callback, is_get_command=True):
        log_info(f"register get all message")
        if is_get_command:
            self._command_listeners[self.TYPE_GET_ALL_MESSAGE] = callback
        else:
            self._command_listeners[self.TYPE_GET_ALL_MESSAGE_WITHOUT_COMMAND] = callback

    def set_on_commands(self, callback):
        self._command_listeners[self.TYPE_GET_ALL_COMMAND] = callback

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
            all_message_listener = self._command_listeners.get(self.TYPE_GET_ALL_MESSAGE)
            if all_message_listener:
                all_message_listener(text, detail.chat.id, message=message)

            # check command message
            entities = detail.entities
            is_command = False
            if entities:
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

                all_command_listener = self._command_listeners.get(self.TYPE_GET_ALL_COMMAND)
                if all_command_listener:
                    all_command_listener(command, args, detail.chat.id, message=message)

                listener = self._command_listeners.get(command)
                if listener:
                    listener(args, detail.chat.id, message)
            else:
                all_message_without_command_listener = self._command_listeners.get(self.TYPE_GET_ALL_MESSAGE_WITHOUT_COMMAND)
                if all_message_without_command_listener:
                    all_message_without_command_listener(text, detail.chat.id, message=message)
        return result_for_lc

    # interface message.py
    def get_messages(self, offset: int, limit: int):
        """Stub for IDE. Implemented in message.py."""

    def send_message(self, chat_id: int, text: str, parse_mode: str = "HTML", reply_id: int = None):
        """Stub for IDE. Implemented in message.py."""

    def send_document(self, chat_id: int, file_path: str, caption: str = None, reply_id: int = None):
        """Stub for IDE. Implemented in message.py."""
