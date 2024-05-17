from python:3.11.6-alpine


# Настройка FastAPI

COPY ./ $HOME/app/

WORKDIR $HOME/app/

RUN pip install -r requirements.txt

RUN pip install uvicorn

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"] # Запуск FastAPI
