import datetime

from fastapi import FastAPI


from models import Faculty, Course, Group, ScheduleRecord, Department, Teacher
from parser import Parser

app = FastAPI()

parser = Parser()


@app.get('/faculties', summary='Получить список институтов/факультетов', tags=['Расписание'])
async def get_faculties() -> list[Faculty]:
    return parser.get_faculties_list()


@app.get('/courses', summary='Получить список курсов', tags=['Расписание'])
async def get_courses(faculty_id: int) -> list[Course]:
    return parser.get_courses_list(faculty_id)


@app.get('/groups', summary='Получить список групп', tags=['Расписание'])
async def get_groups(faculty_id: int, course_id: int) -> list[Group]:
    return parser.get_groups_list(faculty_id, course_id)


@app.get('/departments', summary='Получить список кафедр', tags=['Расписание'])
async def get_departments(faculty_id: int) -> list[Department]:
    return parser.get_departments_list(faculty_id)


@app.get('/teachers', summary='Получить список преподавателей', tags=['Расписание'])
async def get_teachers(department_id: int) -> list[Teacher]:
    return parser.get_teachers_list(department_id)


@app.get('/student_schedule', summary='Получить расписание группы', tags=['Расписание'])
async def get_student_schedule(group_id: int) -> dict[str, list[ScheduleRecord]]:
    return parser.get_student_schedule(group_id)


@app.get('/teacher_schedule', summary='Получить расписание преподавателя', tags=['Расписание'])
async def get_teacher_schedule(teacher_id: int) -> dict[str, list[ScheduleRecord]]:
    return parser.get_teacher_schedule(teacher_id)
