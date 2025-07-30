from dataclasses import dataclass
from typing import Optional


@dataclass
class FromUser:
    id: int
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_bot: Optional[bool] = None
    profile_photos: Optional[dict] = None


@dataclass
class Chat:
    id: int
    type: str
    username: Optional[str] = None
    title: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    photo: Optional[dict] = None


@dataclass
class MessageDetail:
    message_id: int
    from_user: FromUser
    chat: Chat
    date: int
    text: Optional[str] = None
    entities: Optional[dict] = None

    @staticmethod
    def from_dict(data: dict) -> "MessageDetail":
        return MessageDetail(
            message_id=data["message_id"],
            from_user=FromUser(**data["from"]),
            chat=Chat(**data["chat"]),
            date=data["date"],
            text=data.get("text"),
            entities=data.get("entities"),
        )


@dataclass()
class Message:
    update_id: int
    messageDetail: Optional[MessageDetail] = None

    @staticmethod
    def from_dict(data: dict) -> "Message":
        result = Message(
            update_id=data["update_id"],
        )
        detail=  data.get("message")
        if detail:
            result.messageDetail = MessageDetail.from_dict(detail)
        return result
