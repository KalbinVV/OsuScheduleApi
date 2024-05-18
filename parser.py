import abc
import ast
import re
from datetime import timedelta
from typing import Any, Optional

import requests

import config
from cache_decorator import key_db_cache
from models import Faculty, Course, Group, ScheduleRecord, Department, Teacher

from bs4 import BeautifulSoup

from utils import get_text_from_element_or_none


class AbstractParser(abc.ABC):
    @classmethod
    @abc.abstractmethod
    def get_faculties_list(cls) -> list[Faculty]:
        ...

    @classmethod
    @abc.abstractmethod
    def get_courses_list(cls, faculty_id: int) -> list[Course]:
        ...

    @classmethod
    @abc.abstractmethod
    def get_groups_list(cls, faculty_id: int, course_id: int) -> list[Group]:
        ...

    @classmethod
    @abc.abstractmethod
    def get_departments_list(cls, faculty_id: int) -> list[Department]:
        ...

    @classmethod
    @abc.abstractmethod
    def get_teachers_list(cls, department_id: int) -> list[Teacher]:
        ...

    @classmethod
    @abc.abstractmethod
    def get_student_schedule(cls, group_id: int) -> dict[str, list[ScheduleRecord]]:
        ...

    @classmethod
    @abc.abstractmethod
    def get_teacher_schedule(cls, teacher_id: int) -> dict[str, list[ScheduleRecord]]:
        ...


class Parser(AbstractParser):
    DATE_REGEX = re.compile(r'(?P<numeric>\d+\.\d+\.\d+)\((?P<alphabetic>[\wа-яА-Я]+)\)')

    @staticmethod
    def __get_schedule_data(request_value_name: str, who_id: int = 1, **kwargs) -> Any:
        data = {
            'who': who_id,
            'what': '1',
            'request': request_value_name
        }

        for arg in kwargs:
            data[arg] = kwargs[arg]

        response = requests.post(config.url, headers=config.headers, data=data)
        decoded_content = response.content.decode(encoding=config.charset)
        decoded_content = ast.literal_eval(decoded_content)

        return decoded_content

    @classmethod
    def __parse_schedule_data_list(cls, request_value_name: str, class_type: type,
                                   list_data_dict: Optional[dict[str, str]] = None, who_id: int = 1,
                                   **kwargs) -> list[Any]:
        if list_data_dict is None:
            list_data_dict = dict()

        info_dict = cls.__get_schedule_data(request_value_name, who_id, **kwargs)

        objects_list = []

        for object_info in info_dict['list']:
            data_object = class_type(**{data_object_key: object_info[parser_key]
                                        for data_object_key, parser_key in list_data_dict.items()})

            objects_list.append(data_object)

        return objects_list

    @classmethod
    @key_db_cache(ttl=timedelta(hours=8))
    def get_faculties_list(cls) -> list[Faculty]:
        return cls.__parse_schedule_data_list('facult', Faculty, {'id': 'id',
                                                                  'name': 'title',
                                                                  'short_name': 'name'})

    @classmethod
    @key_db_cache(timedelta(hours=8))
    def get_courses_list(cls, faculty_id: int) -> list[Course]:
        return cls.__parse_schedule_data_list('potok', Course, {'id': 'id',
                                                                'name': 'name'},
                                              facult=faculty_id)

    @classmethod
    @key_db_cache(timedelta(hours=8))
    def get_groups_list(cls, faculty_id: int, course_id: int) -> list[Group]:
        return cls.__parse_schedule_data_list('group', Group, {'id': 'id',
                                                               'name': 'name'},
                                              facult=faculty_id, potok=course_id)

    @classmethod
    @key_db_cache(timedelta(hours=8))
    def get_departments_list(cls, faculty_id: int) -> list[Department]:
        return cls.__parse_schedule_data_list('kafedra', Department, {'id': 'id',
                                                                      'name': 'title',
                                                                      'short_name': 'name'},
                                              who_id=2, facult=faculty_id)

    @classmethod
    @key_db_cache(timedelta(hours=8))
    def get_teachers_list(cls, department_id: int) -> list[Teacher]:
        return cls.__parse_schedule_data_list('prep', Teacher, {'id': 'id',
                                                                'name': 'title',
                                                                'short_name': 'name'},
                                              who_id=2, kafedra=department_id)

    @classmethod
    def __get_schedule(cls, **params) -> dict[str, list[ScheduleRecord]]:
        request = requests.get('http://www.osu.ru/pages/schedule/', params=params, verify=False)

        html_text = request.text

        soup = BeautifulSoup(html_text, 'lxml')

        schedule_rows = soup.find_all('tr')[1:]

        schedule_dict = dict()

        for schedule_row in schedule_rows:
            date_row = schedule_row.find('td')

            if date_row is None:
                continue

            date_match = cls.DATE_REGEX.match(date_row.text)

            if date_match is None:
                continue

            numeric_date_value = date_match.group('numeric')

            records_rows = schedule_row.find_all('td')[1:]

            schedule_set = set()
            schedule_dict[numeric_date_value] = schedule_set

            for record_row in records_rows:
                if len(record_row.text.strip()) == 0:
                    continue

                if 'asd' in record_row.get('class'):
                    for sub_row in record_row.find_all('td'):
                        if len(sub_row.text.strip()) == 0:
                            continue

                        name = sub_row.find('span')['title']
                        discipline_type = sub_row.find(class_='lestype').text

                        auditorium = get_text_from_element_or_none(sub_row.find(class_='aud'))
                        teacher_name = get_text_from_element_or_none(sub_row.find(class_='p'))

                        record_id = sub_row['pare_id']

                        schedule_record = ScheduleRecord(id=int(record_id),
                                                         name=name,
                                                         auditorium=auditorium,
                                                         discipline_type=discipline_type,
                                                         teacher_name=teacher_name)

                        schedule_set.add(schedule_record)
                else:
                    name = record_row.find('span')['title']

                    auditorium = get_text_from_element_or_none(record_row.find(class_='aud'))
                    discipline_type = get_text_from_element_or_none(record_row.find(class_='lestype'))

                    teacher_name = get_text_from_element_or_none(record_row.find(class_='p'))
                    record_id = record_row['pare_id']

                    schedule_record = ScheduleRecord(id=int(record_id),
                                                     name=name,
                                                     auditorium=auditorium,
                                                     discipline_type=discipline_type,
                                                     teacher_name=teacher_name)

                    schedule_set.add(schedule_record)

            schedule_dict[numeric_date_value] = sorted(list(schedule_set), key=lambda obj: obj.id)

        return schedule_dict

    @classmethod
    @key_db_cache(ttl=timedelta(hours=1))
    def get_student_schedule(cls, group_id: int) -> dict[str, list[ScheduleRecord]]:
        return cls.__get_schedule(who=1, group=group_id)

    @classmethod
    @key_db_cache(ttl=timedelta(hours=1))
    def get_teacher_schedule(cls, teacher_id: int) -> dict[str, list[ScheduleRecord]]:
        return cls.__get_schedule(who=2, prep=teacher_id)
