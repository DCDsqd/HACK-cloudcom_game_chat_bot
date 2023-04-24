# установка базового образа (host OS)
FROM python:3.9-slim-buster
# установка рабочей директории в контейнере
WORKDIR /code
# копирование файла зависимостей в рабочую директорию
COPY requirements.txt .
# установка зависимостей
RUN pip install -r requirements.txt
# копирование содержимого локальной директории src в рабочую директорию
COPY src/ .
# команда, выполняемая при запуске контейнера
CMD [ "python", "./admin.py", "./bot.py", "./common_func.py", "./customization.py", "./database.py", "./duels.py", "./equipment.py", "./friends.py", "./game.py", "./menu_chain.py", "./time_control.py" ]
COPY . .