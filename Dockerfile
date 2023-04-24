# установка базового образа (host OS)
FROM python:3.9-slim-buster
# установка рабочей директории в контейнере
WORKDIR /code
# копирование файла зависимостей в рабочую директорию
COPY requirements.txt .
# установка зависимостей
RUN pip install -r requirements.txt
# копирование содержимого локальной директории src в рабочую директорию
COPY ./src ./src
# копирование необходимых файлов
COPY ./db ./db
COPY ./res ./res
COPY ./scripts ./scripts
COPY ./sql ./sql
COPY ./tokens ./tokens
COPY ./utils ./utils

# создание директорий
RUN mkdir ./logs

# команда, выполняемая при запуске контейнера
CMD [ "python", "src/bot.py"]
