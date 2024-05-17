# OsuScheduleApi

Api для работы с расписанием ОГУ.

## Установка:

#### Скопировать репозиторий:

git clone https://github.com/KalbinVV/OsuScheduleApi.git

#### Перейти в каталог:

cd OsuScheduleApi

### Через Docker:

#### Запустить API через docker-compose:

docker-compose up

### Без установки Docker:
Необходимо установить Python 3.11

#### Установка необходимых библиотек:

pip install -r requirements.txt

pip install uvicorn

#### Запуск сервера Uvicorn:

uvicorn main:app

### Get методы:

#### /faculties
Возвращает список доступных факультетов/институтов
#### /courses
Возвращает список доступных потоков
#### /groups
Возвращает список доступных групп
#### /departments
Возвращает список доступных кафедр
#### /teachers
Возвращает список преподавателей определенной кафедрв
#### /student_schedule
Возвращает расписание для определенной группы
#### /teacher_schedule
Возвращает расписание для преподавателя

### Зависимости:
fastapi~=0.103.2

requests~=2.31.0

keydb~=0.0.1

beautifulsoup4~=4.12.2

lxml~=4.9.3

### KeyDB

Для организации кэша был использован форк redis - KeyDB