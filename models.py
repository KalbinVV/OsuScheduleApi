from typing import Optional

from pydantic import BaseModel


class Faculty(BaseModel):
    id: int
    name: str
    short_name: str


class Course(BaseModel):
    id: int
    name: str


class Group(BaseModel):
    id: int
    name: str


class Department(BaseModel):
    id: int
    name: str
    short_name: str


class Teacher(BaseModel):
    id: int
    name: str
    short_name: str


class ScheduleRecord(BaseModel):
    id: int
    name: str
    auditorium: Optional[str]
    discipline_type: Optional[str]
    teacher_name: Optional[str]

    def __hash__(self):
        return hash(f'{self.id}{self.name}{self.auditorium}{self.discipline_type}{self.teacher_name}')
