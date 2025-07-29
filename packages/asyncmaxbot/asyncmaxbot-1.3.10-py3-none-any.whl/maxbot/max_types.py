"""
Типы данных для MaxBot
Совместимы с Max API
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Union, Any, TYPE_CHECKING
from enum import Enum
from dataclasses import dataclass

if TYPE_CHECKING:
    from .bot import Bot

# ===============================================================
#  Модели данных API (Pydantic)
# ===============================================================

class AttachmentPayload(BaseModel):
    """Внутренняя полезная нагрузка вложения."""
    url: Optional[str] = None
    photo_id: Optional[Union[str, int]] = None
    id: Optional[Union[str, int]] = None
    fileId: Optional[Union[str, int]] = None
    sticker_id: Optional[str] = None
    title: Optional[str] = None
    emoji: Optional[str] = None
    token: Optional[str] = None
    model_config = {"extra": "allow"}

class AttachmentThumbnail(BaseModel):
    """Превью для вложения (например, у видео)."""
    url: Optional[str] = None

class BaseAttachment(BaseModel):
    """Базовая модель для любого типа вложения."""
    type: str
    payload: Optional[AttachmentPayload] = None
    url: Optional[str] = None
    file_id: Optional[str] = None
    filename: Optional[str] = None
    size: Optional[int] = None
    mime_type: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    duration: Optional[int] = None
    performer: Optional[str] = None
    title: Optional[str] = None
    thumbnail: Optional[AttachmentThumbnail] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    emoji: Optional[str] = None

    def __getattr__(self, name):
        if self.payload and hasattr(self.payload, name):
            return getattr(self.payload, name)
        return self.model_extra.get(name)
    
    @classmethod
    def validate_attachment(cls, attachment_data: dict) -> bool:
        """
        Валидирует структуру вложения на основе реальных данных MaxBot API.
        
        :param attachment_data: Словарь с данными вложения
        :return: True если структура валидна
        """
        if not isinstance(attachment_data, dict):
            return False
        
        if 'type' not in attachment_data:
            return False
        
        attachment_type = attachment_data['type']
        
        # Вложения с payload (image, file, audio, video, sticker)
        if attachment_type in ['image', 'file', 'audio', 'video', 'sticker']:
            if 'payload' not in attachment_data:
                return False
            payload = attachment_data['payload']
            if not isinstance(payload, dict):
                return False
            
            # Валидация по типу
            if attachment_type == 'image':
                return 'photo_id' in payload and 'token' in payload
            elif attachment_type == 'file':
                return 'fileId' in payload and 'token' in payload
            elif attachment_type in ['audio', 'video']:
                return 'token' in payload
            elif attachment_type == 'sticker':
                return 'token' in payload
        
        # Вложения без payload (location, share)
        elif attachment_type == 'location':
            return 'latitude' in attachment_data and 'longitude' in attachment_data
        elif attachment_type == 'share':
            return 'url' in attachment_data
        
        return False
    
    @classmethod
    def get_payload_for_sending(cls, attachment_data: dict) -> dict:
        """
        Извлекает payload для отправки вложения.
        
        :param attachment_data: Словарь с данными вложения
        :return: Словарь payload для отправки
        """
        if not cls.validate_attachment(attachment_data):
            raise ValueError(f"Invalid attachment structure: {attachment_data}")
        
        attachment_type = attachment_data['type']
        
        # Для вложений с payload
        if attachment_type in ['image', 'file', 'audio', 'video', 'sticker']:
            return attachment_data['payload']
        
        # Для вложений без payload (location, share)
        elif attachment_type == 'location':
            return {
                'latitude': attachment_data['latitude'],
                'longitude': attachment_data['longitude']
            }
        elif attachment_type == 'share':
            return {
                'url': attachment_data['url'],
                'title': attachment_data.get('title')
            }
        
        raise ValueError(f"Unsupported attachment type: {attachment_type}")

class User(BaseModel):
    """Представление пользователя Max API."""
    user_id: int
    name: str = ""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_bot: bool = False
    last_activity_time: Optional[int] = 0

class Chat(BaseModel):
    """Представление чата Max API."""
    chat_id: int
    chat_type: str
    user_id: Optional[int] = None

class MessageBody(BaseModel):
    """Тело сообщения, содержащее текст и вложения."""
    mid: str
    seq: int
    text: Optional[str] = None
    attachments: Optional[List[BaseAttachment]] = None

class Message(BaseModel):
    """Представление сообщения Max API."""
    recipient: Chat
    sender: User
    timestamp: int
    body: MessageBody

class Update(BaseModel):
    """
    Представление входящего обновления от API.
    Это корневой объект, который получает Dispatcher.
    """
    message: Message
    update_type: str
    timestamp: int
    marker: Optional[int] = None
    user_locale: Optional[str] = None
    model_config = {"extra": "allow"}

# ===============================================================
#  Старые и вспомогательные классы (могут быть неактуальны)
# ===============================================================

class UpdateType(Enum):
    """Типы обновлений в Max API"""
    MESSAGE = "message"
    CALLBACK_QUERY = "callback_query"
    CHAT_MEMBER = "chat_member"
    MESSAGE_CREATED = "message_created"

class CallbackQuery(BaseModel):
    """(Не используется) Представление callback-запроса."""
    id: str
    from_user: User
    message: Optional[Message] = None
    data: Optional[str] = None

# ===============================================================
#  Класс Context
# ===============================================================

class Context:
    """
    Класс Контекста. Главный инструмент для работы внутри обработчиков.

    Предоставляет удобный доступ ко всем данным обновления (сообщение,
    пользователь, чат) и методы для ответа пользователю.
    """
    
    def __init__(self, update: Update, bot: 'Bot'):
        self.update = update
        self.bot = bot
    
    @property
    def message(self) -> Optional[Message]:
        """Объект `Message` из обновления."""
        return self.update.message

    @property
    def user(self) -> Optional[User]:
        """Объект `User`, отправивший сообщение."""
        return self.update.message.sender if self.message else None

    @property
    def chat(self) -> Optional[Chat]:
        """Объект `Chat`, в котором пришло сообщение."""
        return self.update.message.recipient if self.message else None

    @property
    def date(self) -> int:
        """Timestamp сообщения."""
        return self.update.timestamp

    @property
    def text(self) -> Optional[str]:
        """Текст сообщения."""
        return self.message.body.text if self.message and self.message.body else None
    
    @property
    def chat_id(self) -> Optional[int]:
        """ID чата, в котором пришло сообщение."""
        return self.chat.chat_id if self.chat else None
    
    @property
    def user_id(self) -> Optional[int]:
        """ID пользователя, отправившего сообщение."""
        return self.user.user_id if self.user else None
    
    async def reply(self, text: str, **kwargs):
        """
        Удобный метод для ответа в тот же чат, откуда пришло сообщение.

        :param text: Текст ответного сообщения.
        :param kwargs: Дополнительные параметры для `bot.send_message`.
        """
        if not self.chat_id:
            raise ValueError("No chat_id to reply to")
        return await self.bot.send_message(text, chat_id=self.chat_id, **kwargs)
    
    async def answer(self, text: str, **kwargs):
        """Алиас для `reply`."""
        return await self.reply(text, **kwargs)

    async def edit_message(self, text: str, **kwargs):
        """
        Редактирует текущее сообщение (то, которое вызвало этот хендлер).

        :param text: Новый текст сообщения.
        :param kwargs: Дополнительные параметры для `bot.edit_message`.
        """
        if not self.message or not self.message.body or not self.message.body.mid:
            raise ValueError("Cannot edit message: message ID not found in context.")
        # `edit_message` в bot.py не принимает message_id в kwargs, а как отдельный параметр
        return await self.bot.edit_message(message_id=self.message.body.mid, text=text, **kwargs)

    async def delete_message(self, **kwargs):
        """
        Удаляет текущее сообщение (то, которое вызвало этот хендлер).
        
        :param kwargs: Дополнительные параметры для `bot.delete_message`.
        """
        if not self.message or not self.message.body or not self.message.body.mid:
            raise ValueError("Cannot delete message: message ID not found in context.")
        # `delete_message` в bot.py не принимает kwargs
        return await self.bot.delete_message(message_id=self.message.body.mid)

    async def get_members(self, **kwargs):
        """
        Получает список участников текущего чата.

        :param kwargs: Дополнительные параметры для `bot.get_chat_members`.
        """
        if not self.chat_id:
            raise ValueError("No chat_id to get members from")
        return await self.bot.get_chat_members(self.chat_id, **kwargs)

    async def send_action(self, action: str):
        """
        Отправляет действие в текущий чат.

        :param action: Тип действия (например, 'typing').
        """
        if not self.chat_id:
            raise ValueError("No chat_id to send action to")
        return await self.bot.send_action(self.chat_id, action)

    async def pin_message(self, message_id: Optional[str] = None, **kwargs):
        """
        Закрепляет сообщение в текущем чате.
        Если message_id не указан, закрепляет текущее сообщение.

        :param message_id: ID сообщения для закрепления.
        :param kwargs: Дополнительные параметры для `bot.pin_message`.
        """
        if not self.chat_id:
            raise ValueError("No chat_id to pin message in")
        
        msg_id_to_pin = message_id or (self.message.body.mid if self.message and self.message.body else None)
        if not msg_id_to_pin:
            raise ValueError("No message_id to pin")
            
        return await self.bot.pin_message(self.chat_id, msg_id_to_pin, **kwargs)

    async def unpin_message(self, message_id: str):
        """
        Открепляет сообщение в текущем чате.

        :param message_id: ID сообщения для открепления.
        """
        if not self.chat_id:
            raise ValueError("No chat_id to unpin message in")
        return await self.bot.unpin_message(self.chat_id, message_id)

    async def leave_chat(self):
        """
        Бот покидает текущий чат.
        """
        if not self.chat_id:
            raise ValueError("No chat_id to leave")
        return await self.bot.leave_chat(self.chat_id)

    async def add_members(self, user_ids: List[int]):
        """
        Добавляет участников в текущий чат.

        :param user_ids: Список ID пользователей.
        """
        if not self.chat_id:
            raise ValueError("No chat_id to add members to")
        return await self.bot.add_chat_members(self.chat_id, user_ids)

    @property
    def has_attachments(self) -> bool:
        """True, если в сообщении есть хотя бы одно вложение."""
        return bool(self.attachments)

    @property
    def attachments(self) -> Optional[List[BaseAttachment]]:
        """Список вложений в сообщении."""
        return self.message.body.attachments if self.message and self.message.body else None

    @property
    def images(self) -> List[BaseAttachment]:
        """Возвращает список вложений-изображений."""
        if not self.has_attachments:
            return []
        return [att for att in self.attachments if att.type == "image"] 