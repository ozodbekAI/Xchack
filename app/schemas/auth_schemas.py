from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, UUID4


class UserCreate(BaseModel):
    group_id : UUID4
    username : str
    last_active: Optional[list] = []

class RoomCreate(BaseModel):
    room_name: str
    camera_url: str

class GroupCreate(BaseModel):
    science_name: str
    room_id: UUID4
    day_time: str
    lesson_start_time: Optional[datetime]
    lesson_end_time: Optional[datetime]
