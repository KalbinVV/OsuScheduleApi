import json
import datetime

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from classes.schedule_record_encoder import ScheduleRecordEncoder
from data_collector.parsing_data_collector import ParsingDataCollector

app = FastAPI()
data_collector = ParsingDataCollector()


@app.get('/')
def redirect_to_docs():
    return RedirectResponse("/docs")


@app.get('/departments_dict')
def get_departments_dict():
    return data_collector.get_departments_dict()


@app.get('/departments_streams_dict')
def get_departments_streams_dict(department_id: int):
    return data_collector.get_departments_streams_dict(department_id)


@app.get('/groups_dict')
def get_groups_dict(department_id: int, stream_id: int):
    return data_collector.get_groups_dict(department_id, stream_id)


@app.get('/schedule')
def get_all_schedule(group_id: int):
    return json.dumps(data_collector.get_schedule(group_id),
                      cls=ScheduleRecordEncoder,
                      ensure_ascii=False)


@app.get('/schedule_today')
def get_today_schedule(group_id: int):
    today = datetime.date.today()

    formatted_date = today.strftime("%d.%m.%Y")

    schedule = data_collector.get_schedule(group_id)

    today_schedule = schedule[formatted_date] if formatted_date in schedule else []

    return json.dumps(today_schedule, cls=ScheduleRecordEncoder, ensure_ascii=False)


@app.get('/schedule_tomorrow')
def get_tomorrow_schedule(group_id: int):
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)

    formatted_date = tomorrow.strftime("%d.%m.%Y")

    schedule = data_collector.get_schedule(group_id)

    tomorrow_schedule = schedule[formatted_date] if formatted_date in schedule else []

    return json.dumps(tomorrow_schedule, cls=ScheduleRecordEncoder, ensure_ascii=False)


@app.get('/schedule_week')
def get_week_schedule(group_id: int):
    today = datetime.date.today()

    days = [today + datetime.timedelta(days=i) for i in range(7)]

    formatted_days = [day.strftime("%d.%m.%Y") for day in days]

    schedule_dict = data_collector.get_schedule(group_id)

    week_schedule_dict = dict()

    for day in formatted_days:
        week_schedule_dict[day] = schedule_dict[day] if day in schedule_dict else []

    return json.dumps(week_schedule_dict, cls=ScheduleRecordEncoder, ensure_ascii=False)


@app.get('/schedule_at')
def get_schedule_at(group_id: int, date: str):
    schedule = data_collector.get_schedule(group_id)

    schedule_at_day = schedule[date] if date in schedule else []

    return json.dumps(schedule_at_day, cls=ScheduleRecordEncoder, ensure_ascii=False)