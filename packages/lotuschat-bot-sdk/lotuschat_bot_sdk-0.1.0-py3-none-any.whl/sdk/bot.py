class ChatBot:
    domain = "http://bot.lotuschat.vn/bot"

    def __init__(self, name, token):
        self.name = name
        self.token = token

    def __str__(self):
        return f"Chatbot name[{self.name}] - token[{self.token}] - url[{self.domain}]"