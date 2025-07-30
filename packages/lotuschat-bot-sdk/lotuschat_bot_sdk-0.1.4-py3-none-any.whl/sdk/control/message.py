import requests

from sdk.control.bot import FAILED_REQUEST
from sdk.utility.logger import log_info, log_warning, log_debug, log_verbose

def message_action(cls):
    def get_messages(self, offset: int, limit: int):
        log_info(f"Getting messages with {offset}: {limit}")
        url = f"{self.domain}{self.token}/getUpdates"
        payload = {
            "offset": offset,
            "limit": limit
        }
        log_debug(payload)
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            json = response.json()
            log_verbose(json)
            return json
        except requests.RequestException as e:
            log_warning(FAILED_REQUEST.format("get_messages", e))
            return None

    def send_message(self, chat_id: int, text: str, parse_mode: str = "HTML"):
        log_info(f"Sending message to {chat_id}: {text}")
        url = f"{self.domain}{self.token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode
        }
        log_debug(f"payload: {payload}")
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            json = response.json()
            log_verbose(json)
            return json
        except requests.RequestException as e:
            log_warning(FAILED_REQUEST.format("send_message", e))
            return None

    def send_document(self, chat_id: int, file_path: str, caption: str = None):
        log_info(f"Logging in user {chat_id}: {file_path} - {caption}")
        url = f"{self.domain}{self.token}/sendDocument"
        with open(file_path, 'rb') as file:
            files = {"document": file}
            data = {
                "chat_id": f"{chat_id}",
            }
            if caption:
                data['caption'] = caption
            log_debug(data)
            try:
                response = requests.post(url, data=data, files=files)
                response.raise_for_status()
                json = response.json()
                log_verbose(json)
                return json
            except requests.RequestException as e:
                log_warning(FAILED_REQUEST.format("send_document", e))
                return None

    cls.get_messages = get_messages
    cls.send_message = send_message
    cls.send_document = send_document
