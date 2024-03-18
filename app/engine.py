from sqlalchemy import engine_from_config, text
from app.models.auth_models import Base
from database import engine


async def reset_database():
    tables = [
        "users",
        "groups",
        "rooms",
    ]
    try:

        async with engine.begin() as connection:
            for table in tables:
                await connection.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE;"))

            await connection.run_sync(Base.metadata.create_all)
            return {
                "status": "ok",
                "msg": "Database successfully cleared!"    
                }
    except Exception as e:
        return {
            "status": 500,

        }

