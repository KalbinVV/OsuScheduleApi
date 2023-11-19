import json
from typing import Any

from classes.schedule_record import ScheduleRecord


class ScheduleRecordEncoder(json.JSONEncoder):
    def default(self, obj: Any) -> Any:
        if isinstance(obj, ScheduleRecord):
            return obj.__dict__

        return json.JSONEncoder.default(self, obj)
