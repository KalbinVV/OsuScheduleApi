import json

from classes.schedule_record import ScheduleRecord
from classes.schedule_record_decoder import ScheduleRecordDecoder
from classes.schedule_record_encoder import ScheduleRecordEncoder
from data_collector.parsing_data_collector import ParsingDataCollector

from redis import StrictRedis

rs = StrictRedis(host="localhost", decode_responses=False)


class CachedParsingDataCollector(ParsingDataCollector):
    def get_schedule(self, group_id: int) -> dict[str, list[ScheduleRecord]]:
        redis_key = f'student-schedule:{group_id}'

        if rs.exists(redis_key):
            return json.loads(rs.get(redis_key).decode())

        response = super().get_schedule(group_id)

        rs.set(redis_key, json.dumps(response, cls=ScheduleRecordEncoder))

        return response
