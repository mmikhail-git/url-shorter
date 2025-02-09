import datetime
from sqlalchemy import TIMESTAMP, func
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Mapped, mapped_column

# Use `asyncpg` as the driver for PostgreSQL
engine = create_async_engine(
    'postgresql+asyncpg://postgres:mysecretpassword@localhost:5432/shortener',
    echo=False
)

# Create an async sessionmaker
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_db():
    # Create a new async session
    db = AsyncSessionLocal()
    try:
        yield db
    finally:
        await db.close()


class Base(DeclarativeBase):
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
