from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

engine = create_async_engine(
    url="postgresql+asyncpg://postgres:postgres@localhost:5432/postgres",
    echo=False,
    future=True,
)

async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)



async def get_session() -> AsyncSession:  # type: ignore
    async with async_session_maker() as session:
        yield session

@asynccontextmanager
async def get_session_context() -> AsyncSession:  # type: ignore
    async with async_session_maker() as session:
        yield session

