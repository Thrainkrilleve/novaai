from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, DateTime, Text, Integer
from datetime import datetime
from config import settings

# Database engine
engine = create_async_engine(settings.database_url, echo=False)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

class Conversation(Base):
    """Store conversation history"""
    __tablename__ = "conversations"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    role: Mapped[str] = mapped_column(String(20))  # 'user' or 'assistant'
    content: Mapped[str] = mapped_column(Text)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    has_image: Mapped[bool] = mapped_column(default=False)
    session_id: Mapped[str] = mapped_column(String(100), nullable=True)

class ScreenEvent(Base):
    """Store screen capture events for learning"""
    __tablename__ = "screen_events"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    description: Mapped[str] = mapped_column(Text)
    action_taken: Mapped[str] = mapped_column(Text, nullable=True)
    user_feedback: Mapped[str] = mapped_column(String(50), nullable=True)

class WebActivity(Base):
    """Store web browsing activity"""
    __tablename__ = "web_activity"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    url: Mapped[str] = mapped_column(String(500))
    action: Mapped[str] = mapped_column(String(100))  # navigate, click, type, etc.
    details: Mapped[str] = mapped_column(Text, nullable=True)

async def init_db():
    """Initialize database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_session() -> AsyncSession:
    """Get database session"""
    async with async_session_maker() as session:
        yield session

async def save_message(role: str, content: str, has_image: bool = False, session_id: str = None):
    """Save a message to conversation history"""
    async with async_session_maker() as session:
        msg = Conversation(
            role=role,
            content=content,
            has_image=has_image,
            session_id=session_id
        )
        session.add(msg)
        await session.commit()

async def get_conversation_history(limit: int = 50, session_id: str = None):
    """Get recent conversation history"""
    from sqlalchemy import select
    
    async with async_session_maker() as session:
        query = select(Conversation).order_by(Conversation.timestamp.desc()).limit(limit)
        if session_id:
            query = query.where(Conversation.session_id == session_id)
        
        result = await session.execute(query)
        messages = result.scalars().all()
        
        # Return in chronological order
        return [
            {"role": msg.role, "content": msg.content, "timestamp": msg.timestamp}
            for msg in reversed(messages)
        ]

async def clear_conversation_history(session_id: str = None):
    """Clear conversation history for a session"""
    from sqlalchemy import delete
    
    async with async_session_maker() as session:
        if session_id:
            query = delete(Conversation).where(Conversation.session_id == session_id)
        else:
            query = delete(Conversation)
        
        await session.execute(query)
        await session.commit()

async def get_conversation_count(session_id: str = None) -> int:
    """Get total number of messages in conversation"""
    from sqlalchemy import select, func
    
    async with async_session_maker() as session:
        query = select(func.count(Conversation.id))
        if session_id:
            query = query.where(Conversation.session_id == session_id)
        
        result = await session.execute(query)
        return result.scalar() or 0

async def get_conversation_summary(session_id: str, message_range: tuple = None):
    """Get a range of conversation messages for summarization"""
    from sqlalchemy import select
    
    async with async_session_maker() as session:
        query = select(Conversation).where(Conversation.session_id == session_id).order_by(Conversation.timestamp)
        
        if message_range:
            start, end = message_range
            query = query.offset(start).limit(end - start)
        
        result = await session.execute(query)
        messages = result.scalars().all()
        
        return [
            {"role": msg.role, "content": msg.content, "timestamp": msg.timestamp}
            for msg in messages
        ]

