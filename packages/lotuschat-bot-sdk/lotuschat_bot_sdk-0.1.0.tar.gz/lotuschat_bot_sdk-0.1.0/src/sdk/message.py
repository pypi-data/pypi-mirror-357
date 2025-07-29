import requests


def _message_action(cls):
    def send_message(self, chat_id: int, text: str, parse_mode: str = "HTML"):
        print(f"Sending message to {chat_id}: {text}")
        url = f"{self.domain}{self.token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode
        }
        print(payload)
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()  # Raise an exception for HTTP errors
            json = response.json()
            print(json)
            return json
        except requests.RequestException as e:
            print(f"Failed to send message: {e}")
            return None

    def send_document(self, chat_id: int, file_path: str, caption: str = None):
        print(f"Logging in user {chat_id}: {file_path} - {caption}")
        url = f"{self.domain}{self.token}/sendDocument"
        with open(file_path, 'rb') as file:
            files = {"document": file}
            data = {
                "chat_id": f"{chat_id}",
            }
            if caption:
                data['caption'] = caption
            print(data)
            try:
                response = requests.post(url, data=data, files=files)
                response.raise_for_status()
                return response.json()
            except requests.RequestException as e:
                print(f"Failed to send document: {e}")
                return None

    cls.send_message = send_message
    cls.send_document = send_document
