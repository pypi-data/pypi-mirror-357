from typing import List
from uuid import UUID
from datetime import datetime

from sqlalchemy import select, delete, and_
from sqlalchemy.ext.asyncio import AsyncSession

from leodb.models.account.conversation import Conversation
from leodb.models.account.message import Message
from leodb.schemas.conversation import MessageCreate
from .base_repository import BaseRepository
from leodb.core.config import settings
from leodb.schemas.conversation import MessageRead

class MessageRepository(BaseRepository[Message, MessageCreate, None, MessageRead]):

    def __init__(self, db: AsyncSession, model: type[Message]):
        super().__init__(db, model, MessageRead)

    async def add_message(self, *, conversation_id: UUID, obj_in: MessageCreate) -> MessageRead:
        """
        Adds a new message to a conversation and handles related logic:
        1. Updates the conversation's last_updated_at timestamp.
        2. Creates the new message.
        3. Truncates old messages if the conversation exceeds the configured limit.
        All operations are part of the same transaction managed by the UnitOfWork.
        """
        # 1. Update conversation timestamp
        conversation = await self._session.get(Conversation, conversation_id)
        if not conversation:
            raise ValueError(f"Conversation with id {conversation_id} not found.")
        conversation.last_updated_at = datetime.utcnow()

        # 2. Create the new message
        # Note: le nom du champ dans le modèle est meta_data
        db_obj = Message(
            conversation_id=conversation_id,
            role=obj_in.role,
            content=obj_in.content,
            meta_data=obj_in.metadata
        )
        self._session.add(db_obj)
        
        # 3. Truncate old messages
        # This part is complex and requires careful handling of session state.
        # We flush to get the new message_id and ensure the count is correct.
        await self._session.flush()

        # Check if truncation is needed
        max_messages = settings.POSTGRES_MAX_MESSAGES_PER_CONVERSATION # Assuming this setting exists
        if max_messages and max_messages > 0:
            # Subquery to find the IDs of messages to delete
            subquery = (
                select(Message.message_id)
                .where(Message.conversation_id == conversation_id)
                .order_by(Message.created_at.desc())
                .offset(max_messages)
                .scalar_subquery()
            )
            # Delete statement
            delete_stmt = delete(Message).where(Message.message_id.in_(subquery))
            await self._session.execute(delete_stmt)

        await self._session.flush()
        await self._session.refresh(db_obj)
        return self.read_schema.from_orm(db_obj)

    async def get_history(self, *, conversation_id: UUID, limit: int) -> List[MessageRead]:
        """
        Gets the most recent messages from a conversation.
        """
        # To get the N most recent messages in chronological order, we need a subquery.
        # 1. Find the N most recent messages.
        subquery = (
            select(self._model.message_id)
            .where(self._model.conversation_id == conversation_id)
            .order_by(self._model.created_at.desc())
            .limit(limit)
            .scalar_subquery()
        )
        # 2. Select those messages and order them chronologically.
        stmt = (
            select(self._model)
            .where(self._model.message_id.in_(subquery))
            .order_by(self._model.created_at.asc())
        )
        result = await self._session.execute(stmt)
        db_objs = result.scalars().all()
        return [self.read_schema.from_orm(db_obj) for db_obj in db_objs]

    async def get_all_by_conversation_and_user(
        self, *, conversation_id: UUID, user_id: str, limit: int = 100
    ) -> List[MessageRead]:
        """
        Gets the most recent messages from a conversation, ensuring the user
        is the owner of the conversation.
        """
        # Subquery to get the most recent message IDs for the given conversation
        # while also checking for ownership via a join.
        subquery = (
            select(self._model.message_id)
            .join(Conversation, self._model.conversation_id == Conversation.conversation_id)
            .where(
                and_(
                    Conversation.conversation_id == conversation_id,
                    Conversation.user_id == user_id
                )
            )
            .order_by(self._model.created_at.desc())
            .limit(limit)
            .scalar_subquery()
        )

        # Main query to fetch the full message objects and order them chronologically
        stmt = (
            select(self._model)
            .where(self._model.message_id.in_(subquery))
            .order_by(self._model.created_at.asc())
        )
        
        result = await self._session.execute(stmt)
        db_objs = result.scalars().all()
        return [self.read_schema.from_orm(db_obj) for db_obj in db_objs]