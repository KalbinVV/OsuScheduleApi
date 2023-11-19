import json
import typing

from classes.schedule_record import ScheduleRecord


class ScheduleRecordJsonDict(typing.TypedDict):
    class_id: int
    class_name: str
    class_room: str
    class_type: str
    teacher_name: str


class ScheduleRecordDecoder(json.JSONDecoder):
    def __init__(self, **kwargs):
        kwargs["object_hook"] = self.object_hook
        super().__init__(**kwargs)

    @staticmethod
    def object_hook(obj):
        schedule_record = ScheduleRecord(int(obj['class_id']),
                                         obj['class_name'],
                                         obj['class_room'],
                                         obj['class_type'],
                                         obj['teacher_name'])

        return schedule_record
