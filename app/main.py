import asyncio
from datetime import datetime, timedelta
from fastapi import FastAPI
import uvicorn
from app.routers.auth_router import router as router_operation
from imutils.video import VideoStream
import imutils
import cv2
from app.managers.recoginition_manager import update_user_seen, get_user_names, add_attendance
from app.controllers.functions import Functions
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Xcheck")
app.include_router(router_operation)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

display_width = 1080
data_to_update = {}
recognition = Functions()

async def update_database():
    global data_to_update
    new_data = {}
    if data_to_update:
        try:
            for name, items in data_to_update.items():
                if sum(items) >= 5:
                    new_data[name] = 1
                else:
                    new_data[name] = 0
                    
            print("Data",new_data)
            await update_user_seen(new_data)

            data_to_update = {}  
        except Exception as e:
            print(f"Database update error: {e}")

async def add_in_array(data, index, names_dict):
    global data_to_update

    
    print(data)
    for i in data:
        name, time_found = i.get("name"), i.get("found_time")
        if name in list(names_dict.keys()) and time_found == datetime.utcnow().strftime('%Y-%m-%d %H:%M'):
            
            names_dict[name][index] = 1

    data_to_update = names_dict
    return data_to_update

async def video_processing_loop():
    cap = VideoStream(src=0).start() #"rtsp://192.168.1.77/stream1"
    await asyncio.sleep(2.0)  # Allow the camera sensor to warm up
    names = await get_user_names()

    while True:
        today = datetime.now().date()
        start_time = datetime.combine(today, datetime.strptime("13:00", "%H:%M").time())
        end_time = datetime.combine(today, datetime.strptime("15:47", "%H:%M").time())
        current_time = datetime.now()
        interval_seconds = 3 

        if current_time < start_time:
            time_until_start = start_time - current_time
            await asyncio.sleep(time_until_start.total_seconds())

        elif start_time <= current_time < end_time:
            names_dict = {name: [0] * 10 for name in names}

            for i in range(10):
                frame = cap.read()
                frame = imutils.resize(frame, width=display_width)
                result = recognition.get_found_labels(frame)
                data_to_update = await add_in_array(result, i, names_dict)
                print(data_to_update)
                await asyncio.sleep(interval_seconds)

            await update_database()

        if current_time >= end_time:
            # Call add_attendance(names) after processing is done for the day.
            await add_attendance(names)

            # Wait until the next day's start time.
            tomorrow = today + timedelta(days=1)
            start_time = datetime.combine(tomorrow, start_time.time())
            end_time = datetime.combine(tomorrow, end_time.time())
            time_until_next_start = start_time - datetime.now()
            await asyncio.sleep(time_until_next_start.total_seconds())

    cap.stop()
    cv2.destroyAllWindows()



def start_video_thread():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    asyncio.gather(video_processing_loop())

@app.on_event("startup")
async def startup_event():
    start_video_thread()

if __name__ == "__main__":
    uvicorn.run(app=app, host="127.0.0.1", port=8000)
