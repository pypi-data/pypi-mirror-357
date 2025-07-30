from dataclasses import dataclass
from typing import List, Optional, Union


@dataclass
class Entity:
    offset: int
    length: int
    type: str
    url: Optional[str] = None
    user: Optional[Union[str, dict]] = None


@dataclass
class User:
    id: int
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None
    profile_photos: Optional[str] = None


@dataclass
class Chat:
    id: int
    type: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None


@dataclass
class MessageDetail:
    message_id: int
    from_user: User
    chat: Chat
    date: int
    text: Optional[str] = None
    entities: Optional[List[Entity]] = None


@dataclass
class Message:
    update_id: int
    message_detail: Optional[MessageDetail] = None

    @staticmethod
    def from_dict(data: dict) -> "Message":
        msg = data.get("message")
        message_detail = None
        if msg:
            from_user = User(**msg["from"])
            chat = Chat(**msg["chat"])
            raw_entities = msg.get("entities")
            entities = [Entity(**e) for e in raw_entities] if raw_entities else None
            message_detail = MessageDetail(
                message_id=msg["message_id"],
                from_user=from_user,
                chat=chat,
                date=msg["date"],
                text=msg.get("text"),
                entities=entities
            )
        return Message(update_id=data["update_id"], message_detail=message_detail)

