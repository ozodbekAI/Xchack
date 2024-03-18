from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import UUID4
from sqlalchemy import insert, select
from asyncpg.exceptions import UniqueViolationError, ForeignKeyViolationError
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.auth_schemas import UserCreate, RoomCreate, GroupCreate
from app.models.auth_models import User, Room, Group
from database import get_session
from app.managers.recoginition_manager import add_embedding_in_json
from asyncpg.exceptions import UniqueViolationError
from engine import reset_database



router = APIRouter(
    prefix="/api",
    tags=["Operations"]
)




@router.post("/group")
async def add_group(groupdata: GroupCreate, session: AsyncSession = Depends(get_session)):
    try:
        stmt = insert(Group).values(**groupdata.dict())
        await session.execute(stmt)
        await session.commit()

        return {
            "status": "success",
            }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "status": 500,
                "msg": f"Error {e}"
            }
        )


@router.post("/user")
async def add_user(userdata: UserCreate, session: AsyncSession = Depends(get_session)):
    try:
        # Check if the specified group_id exists in the groups table
        existing_group = await session.execute(select(Group).where(Group.id == userdata.group_id))
        if not existing_group.scalar_one_or_none():
            raise HTTPException(
                status_code=400,
                detail={"msg": f"Group with ID {userdata.group_id} does not exist"}
            )

        # Create a new user object
        new_user = User(
            group_id=userdata.group_id,
            username=userdata.username,
            status=[]
        )

        # Add the new user to the session
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)

        # Return the new user id and other data
        return {"status": "ok", "data": new_user} # dict(https://f810-213-230-86-33.ngrok-free.app) funksiyasini qo'shing
    except UniqueViolationError:
        raise HTTPException(
            status_code=400,
            detail={"msg": f"User with username {userdata.username} already exists"}
        )
    except ForeignKeyViolationError:
        raise HTTPException(
            status_code=400,
            detail={"msg": f"Invalid group_id provided: {userdata.group_id}"}
        )
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=500,
            detail={"msg": f"Server error {e}"}
        )



@router.post("/room")
async def add_room(new_operations: RoomCreate, session: AsyncSession = Depends(get_session)):
    try:
        stmt = insert(Room).values(**new_operations.dict())
        print(stmt)
        await session.execute(stmt)
        await session.commit()
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "msg": f"Server error {e}",
            }
        )

@router.post("/uploadfile/")
async def create_upload_file(user_id: UUID4, file: UploadFile = File(...), session: AsyncSession = Depends(get_session)):
    try:
        with open(f"imgs/{file.filename}", "wb") as f:
            f.write(file.file.read())
        
        name = await session.execute(select(User.username).where(User.id == user_id))

        embedding = await add_embedding_in_json(img_name=file.filename, name=name.scalar())

        #await session.execute(update(User).where(User.id == user_id).values(embeddings=embedding))

        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "msg": f"Server error {e}",
            }
        )

@router.get("/group/{group_id}")
async def get_group(group_id: UUID4, session: AsyncSession = Depends(get_session)):
    try:
        group = await session.execute(select(Group).where(Group.id == group_id))
        group_data = group.scalar_one()
        return {
            "status": "ok",
            "data":group_data
            }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "msg": f"Server error {e}",
            }
        )

@router.get("/users/gorup_id/{group_id}")
async def get_users_from_id(group_id: UUID4, session: AsyncSession = Depends(get_session)):
    try:
        # Assuming you have a User model with a foreign key 'group_id' referencing the Group model
        stmt = select(User).join(Group).where(Group.id == group_id)
        
        users = await session.execute(stmt)
        users_data = users.scalars().all()

        return {
            "status": "ok",
            "data": users_data
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "msg": f"Server error {e}",
            }
        )

@router.get("/user/{user_id}")
async def get_user(user_id: UUID4, session: AsyncSession = Depends(get_session)):
    try:
        user = await session.execute(select(User).where(User.id == user_id))
        user_data = user.scalar_one()
        return {
            "status": "ok",
            "data":user_data
            }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "msg": f"Server error {e}",
            }
        )

@router.get("/room/{room_id}")
async def get_room(room_id: UUID4, session: AsyncSession = Depends(get_session)):
    try:
        room = await session.execute(select(Room).where(Room.room_id == room_id))
        room_data = room.scalar_one()
        return {
            "status": "ok",
            "data":room_data
            }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "msg": f"Server error {e}",
            }
        )
    
@router.get("/rooms")
async def get_all_rooms(session: AsyncSession = Depends(get_session)):
    try:
        result = await session.execute(select(Room))
        rooms = result.scalars().all()  # Fetch all Room entries as a list
        return {
            "status": "ok",
            "data": rooms
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "msg": f"Server error {e}",
            }
        )
    
@router.get("/groups")
async def get_all_rooms(session: AsyncSession = Depends(get_session)):
    try:
        result = await session.execute(select(Group))
        rooms = result.scalars().all()  # Fetch all Room entries as a list
        return {
            "status": "ok",
            "data": rooms
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "msg": f"Server error {e}",
            }
        )

@router.get("/users")
async def get_all_rooms(session: AsyncSession = Depends(get_session)):

    try:
        result = await session.execute(select(User))
        rooms = result.scalars().all()  # Fetch all Room entries as a list
        return {
            "status": "ok",
            "data": rooms
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "msg": f"Server error {e}",
            }
        )

@router.delete("/deleteall")
async def delete_database():
    try:
        result = await reset_database()
        return {
            "status": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "msg": f"Server error {e}",
            }
        )

