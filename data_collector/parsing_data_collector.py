import requests
from bs4 import BeautifulSoup, ResultSet

from classes.schedule_record import ScheduleRecord
from data_collector.abstract_data_collector import AbstractDataCollector

import re

from utils import get_text_from_element_or_default


class ParsingDataCollector(AbstractDataCollector):
    MAIN_SCHEDULE_URL = 'http://www.osu.ru/pages/schedule/'
    HANDLER_SCHEDULE_URL = 'http://www.osu.ru/pages/schedule/index.php'

    DATE_REGEX = re.compile(r'(?P<numeric>\d+\.\d+\.\d+)\((?P<alphabetic>[\wа-яА-Я]+)\)')

    @classmethod
    def __parse_options_container(cls, soup: BeautifulSoup, container_id: str) -> ResultSet:
        container = soup.find(id=container_id)

        return container.find_all('option')[1:]

    def get_departments_dict(self) -> dict[str, int]:
        soup = BeautifulSoup(requests.get(self.MAIN_SCHEDULE_URL, verify=False).text, 'lxml')

        departments_options = self.__parse_options_container(soup, 'facult')

        departments_dict = dict()

        for option in departments_options:
            departments_dict[option['title']] = int(option['value'])

        return departments_dict

    def get_departments_streams_dict(self, department_id: int) -> dict[str, int]:
        request = requests.post(self.HANDLER_SCHEDULE_URL,
                                verify=False,
                                data={'who': 1,
                                      'what': 1,
                                      'request': 'potok',
                                      'filial': 1,
                                      'mode': 'full',
                                      'facult': department_id})

        html_text = request.text

        soup = BeautifulSoup(html_text, 'lxml')

        streams_options = self.__parse_options_container(soup, 'potok')

        streams_dict = dict()

        for option in streams_options:
            streams_dict[option.text] = int(option['value'])

        return streams_dict

    def get_groups_dict(self, department_id: int, stream_id: int) -> dict[str, int]:
        request = requests.post(self.HANDLER_SCHEDULE_URL,
                                verify=False,
                                data={'who': 1,
                                      'what': 1,
                                      'request': 'group',
                                      'filial': 1,
                                      'mode': 'full',
                                      'facult': department_id,
                                      'potok': stream_id})

        html_text = request.text

        soup = BeautifulSoup(html_text, 'lxml')

        groups_options = self.__parse_options_container(soup, 'group')

        groups_dict = dict()

        for option in groups_options:
            groups_dict[option.text] = int(option['value'])

        return groups_dict

    def get_schedule(self, group_id: int) -> dict[str, list[ScheduleRecord]]:
        request = requests.get(f'http://www.osu.ru/pages/schedule/?who=1&what=1&filial=1&group={group_id}&mode=full',
                               verify=False)

        html_text = request.text

        soup = BeautifulSoup(html_text, 'lxml')

        schedule_rows = soup.find_all('tr')[1:]

        schedule_dict = dict()

        for schedule_row in schedule_rows:
            date_row = schedule_row.find('td')

            if date_row is None:
                continue

            date_match = self.DATE_REGEX.match(date_row.text)

            if date_match is None:
                continue

            numeric_date_value = date_match.group('numeric')

            records_rows = schedule_row.find_all('td')[1:]

            schedule_dict[numeric_date_value] = list()

            for record_row in records_rows:
                if len(record_row.text.strip()) == 0:
                    continue

                if 'asd' in record_row.get('class'):
                    for sub_row in record_row.find_all('td'):
                        if len(sub_row.text.strip()) == 0:
                            continue

                        class_name = sub_row.find('span')['title']
                        class_type = sub_row.find(class_='lestype').text

                        class_room = get_text_from_element_or_default(sub_row.find(class_='aud'),
                                                                      'Аудитория не указана')
                        teacher_name = get_text_from_element_or_default(sub_row.find(class_='p'),
                                                                        'Преподаватель не указан')

                        record_id = sub_row['pare_id']

                        schedule_record = ScheduleRecord(int(record_id),
                                                         class_name,
                                                         class_room,
                                                         class_type,
                                                         teacher_name)

                        schedule_dict[numeric_date_value].append(schedule_record)
                else:
                    class_name = record_row.find('span')['title']

                    class_room = get_text_from_element_or_default(record_row.find(class_='aud'),
                                                                  'Аудитория не указана')
                    class_type = get_text_from_element_or_default(record_row.find(class_='lestype'),
                                                                  'Не указано')

                    teacher_name = get_text_from_element_or_default(record_row.find(class_='p'),
                                                                    'Преподаватель не указан')
                    record_id = record_row['pare_id']

                    schedule_record = ScheduleRecord(int(record_id),
                                                     class_name,
                                                     class_room,
                                                     class_type,
                                                     teacher_name)

                    schedule_dict[numeric_date_value].append(schedule_record)

        return schedule_dict
