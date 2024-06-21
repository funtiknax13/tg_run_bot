import asyncio

from db import DBmanager
import datetime
import time
from config import config


import os
from dotenv import load_dotenv


dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=dotenv_path)

db_connect = DBmanager(os.getenv('DB_NAME'), config())
data = [{"user_id": 1, "track": "images/tracks/track01.txt",
         "run_date": datetime.datetime.strptime('05.06.2024', '%d.%m.%Y').date(),
         "distance": 15.11, "run_time": datetime.datetime.strptime('01:06:31', '%H:%M:%S').time(),
         "create_date": datetime.datetime.now(), "description": "Легкая тренировка", "sneakers": None, "is_moderate":
         False}]


async def test_db_work():
    item = data[0]
    # await db_connect.add_run(item['user_id'], item['track'], item['run_date'], item['distance'], item['run_time'],
    #                          datetime.datetime.now(), item["description"], item["sneakers"], item["is_moderate"])

    run_list = await db_connect.get_run_list(1)
    print(run_list)

#     run_time_seconds = item["run_time"].hour * 3600 + item["run_time"].minute * 60 + item["run_time"].second
#     pace_seconds = run_time_seconds / item["distance"]
#     if pace_seconds // 3600 > 0:
#         pace = time.strftime('%H:%M:%S', time.gmtime(pace_seconds))
#     else:
#         pace = time.strftime('%M:%S', time.gmtime(pace_seconds))
#     with open(item["track"], 'r') as image:
#         track_info = image.read()
#     message = f"""
# Run date: {datetime.datetime.strftime(item["run_date"], '%d.%m.%Y')}
# Run track: {track_info}
# Run distance: {item["distance"]} km
# Run time: {item["run_time"]}
# Pace: {pace}
# """
#     print(message)


async def main():
    await db_connect.create_table()
    await test_db_work()


asyncio.run(main())
