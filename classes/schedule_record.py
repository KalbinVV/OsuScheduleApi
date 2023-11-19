from dataclasses import dataclass


# Объект, отражающий запись о занятии
# class_id = номер пары
# class_name = названия дисциплины
# class_room = номер аудитории
# class_type = вид занятия (лекция, лабораторная работа, практика)
# teacher_name = имя преподавателя
@dataclass
class ScheduleRecord:
    class_id: int
    class_name: str
    class_room: str
    class_type: str
    teacher_name: str
