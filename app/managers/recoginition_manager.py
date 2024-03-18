import json
from app.models.auth_models import Group, Room, User
from sqlalchemy import text
from database import get_session, async_session_maker
from app.models.auth_models import User  # Ensure this import matches your project structure
from database import get_session  # Assuming this provides AsyncSession context
from app.controllers.functions import Functions

func = Functions()




  
async def add_user(userdata):
    async with get_session() as session:
        try:
            user = User(
                username=userdata.get("username"), 
                group_id=userdata.get("group_id"),
                embeddings=userdata.get("embeddings"), 
                image_url=userdata.get('image_url'),
                image_path=userdata.get("image_path"),
            )
            session.add(user)
            await session.commit()
            session.refresh(user)
        except IOError:
            raise


async def add_group(groupdata):
    async with get_session() as session:
        try:
            group = Group(
                science_name=groupdata.get("science_name"),
                room_id=groupdata.get("room_id"),
                lesson_start_time=groupdata.get("lesson_start_time"),
                lesson_end_time=groupdata.get("lesson_end_time")
            )
            
            session.add(group)
            await session.commit()
            session.refresh(group)
        except IOError:
            raise


async def add_room(roomdata):
    async with get_session() as session:
        try:
            room = Room(
                camera_url=roomdata.get("camera_url")
            )
            
            session.add(room)
            await session.commit()
            await session.refresh()
        except IOError:
            raise


async def update_user_seen(user_data):
    try:
        async with async_session_maker() as session:
            async with session.begin():
                for name, status in user_data.items():
                    result = await session.execute(
                        text("SELECT status FROM users WHERE username = :name"), {"name": name}
                    )
                    existing_statuses = result.scalar()

                    if existing_statuses is not None:
                        # Handle existing statuses (assuming status is a list in the database)
                        updated_statuses = existing_statuses + [status]
                        await session.execute(
                            text("UPDATE users SET status = :updated_statuses WHERE username = :name"),
                            {"updated_statuses": updated_statuses, "name": name},
                        )
                    else:
                        # Handle the case where there are no existing statuses
                        await session.execute(
                            text("UPDATE users SET status = :status WHERE username = :name"),
                            {"status": [status], "name": name},
                        )

                await session.commit()

        return True
    except Exception as e:
        print(f"Database update error: {e}")
        # Handle the exception appropriately
        return False
    

async def get_user_names():
    try:
        async with async_session_maker() as session:
            query = text("SELECT username FROM users;")
            result = await session.execute(query)
            return result.scalars().all()
    except Exception as e:
        print(f"Error fetching user names: {e}")
        return []
    

async def add_attendance(names):
    print("WORK")
    try:
        async with async_session_maker() as session:
            async with session.begin():
                for name in names:
                    result = await session.execute(
                        text("SELECT status FROM users WHERE username = :name"), {"name": name}
                    )
                    existing_statuses = result.scalar()

                    if sum(existing_statuses) >= len(existing_statuses) // 2:
                        attendance_status = "came"
                    else:
                        attendance_status = "not came"

                    await session.execute(
                        text("UPDATE users SET attendance = :updated_status WHERE username = :name"),
                        {"updated_status": attendance_status, "name": name},
                    )

                    await session.execute(
                        text("UPDATE users SET status = :empty_array WHERE username = :name"),
                        {"empty_array": [], "name": name},
                    )

                await session.commit()

    except Exception as e:
        print(f"Database update error: {e}")
        # Handle the exception appropriately
        return False


async def add_embedding_in_json(img_name, name):
    new_data = {}
    embedding = func.get_image_embedding(img_path=f"imgs/{img_name}")
    new_data[name] = embedding
    
    json_file_path = "/home/ozodbek/Face recoginition/faces.json"

    try:
        with open(json_file_path, 'r') as file:
            existing_data = json.load(file)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        # Handle file not found or JSON decode errors
        existing_data = {}

    # Update existing_data with new_data
    existing_data.update(new_data)

    with open(json_file_path, 'w') as file:
        json.dump(existing_data, file, indent=4)

    


    return embedding
