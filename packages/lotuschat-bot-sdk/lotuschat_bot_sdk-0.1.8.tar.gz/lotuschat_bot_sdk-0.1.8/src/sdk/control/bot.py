from dataclasses import dataclass
from typing import List, Optional

from flask import request

from ..model.data import Message, Entity
from ..utility.logger import log_info, log_debug

FAILED_REQUEST = "Api[{}] request failed. Error: {}}"
TYPE_BOT_COMMAND = "bot_command"
TYPE_UNKNOWN = "unknown"
TEXT_TYPE = "text"

def is_not_empty(s: str) -> bool:
    return bool(s and s.strip())

class ParseModeType:
    MARKDOWN = "Markdown"
    HTML = "HTML"


@dataclass
class Argument:
    text: str
    type: str
    entity: Optional[Entity] = None


class ChatBot:
    _domain = "http://bot.lotuschat.vn/bot"
    _command_listeners = {}

    def __init__(self, name, token):
        self.name = name
        self.token = token
        self._all_message_listener = None
        self._all_message_listener_no_command = None
        self._all_command_listener = None

    def __str__(self):
        return f"Chatbot name[{self.name}] - token[{self.token}] - url[{self._domain}]"

    def set_on_messages(self, callback, is_get_command=True):
        log_info(f"register get all message")
        if is_get_command:
            self._all_message_listener = callback
        else:
            self._all_message_listener_no_command = callback

    def set_on_commands(self, callback):
        self._all_command_listener = callback

    def set_on_command(self, command: str, callback):
        log_info(f"register command {command}")
        self._command_listeners[command] = callback

    def web_hook(self):
        result_for_lc = "", 200
        result = request.get_json()
        if result:
            log_info(f"get message")
            message = Message.from_dict(result)
            detail = message.message_detail
            # verify message empty
            if detail is None:
                log_debug("empty message")
                return result_for_lc
            log_debug(message)

            # send raw message
            log_info(f"send text for all message lístener")
            text = detail.text
            if self._all_message_listener:
                self._all_message_listener(text, detail.chat.id, message=message)

            # check command message
            log_info(f"check message is command")
            entities = detail.entities
            is_command = False
            if entities:
                for entity in entities:
                    if entity.type == TYPE_BOT_COMMAND and entity.offset == 0:
                        is_command = True
                        break
            if is_command:
                log_info(f"extract command")
                parts = self._command_extract(text=text, entities=entities)
                if not parts:
                    if self._all_message_listener_no_command:
                        self._all_message_listener_no_command(text, detail.chat.id, message=message)
                    return result_for_lc
                command = parts[0]
                args = parts[1:]

                log_info(f"send command via listeners")
                if self._all_command_listener:
                    self._all_command_listener(command.text, args, detail.chat.id, message=message)
                listener = self._command_listeners.get(command.text)
                if listener:
                    listener(args, detail.chat.id, message)
            else:
                log_info(f"send message no command listener")
                if self._all_message_listener_no_command:
                    self._all_message_listener_no_command(text, detail.chat.id, message=message)
        return result_for_lc

    def _command_extract(self, text: str, entities: list[Entity]) -> list[Argument]:
        log_info(f"{self} extract text @text")
        entities = sorted(entities, key=lambda e: e.offset)
        result = []
        cursor = 0

        for entity in entities:
            if entity.type == TYPE_UNKNOWN:
                continue

            # Add plain text before the entity
            if cursor < entity.offset:
                temp = text[cursor:entity.offset].strip()
                if is_not_empty(temp):
                    result.append(Argument(temp, TEXT_TYPE, None))

            # Add the entity chunk
            end = entity.offset + entity.length
            temp = text[entity.offset:end].strip()
            result.append(Argument(temp, entity.type, entity))
            cursor = end

        # Add trailing text after last entity
        if cursor < len(text):
            temp = text[cursor:].strip()
            if is_not_empty(temp):
                result.append(Argument(temp, TEXT_TYPE, None))

        return result



    # interface message.py
    def get_messages(self, offset: int, limit: int):
        """Stub for IDE. Implemented in message.py."""

    def send_message(self, chat_id: int, text: str, parse_mode: str = "HTML", reply_id: int = None):
        """Stub for IDE. Implemented in message.py."""

    def send_document(self, chat_id: int, file_path: str, caption: str = None, reply_id: int = None):
        """Stub for IDE. Implemented in message.py."""
