FROM python:3.9-slim

# Настройка виртуального окружения
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Подтягиваем исходники
COPY --chown=root:root src /root/application
WORKDIR /root/application

# Установка зависимостей
RUN pip install -r requirements.txt
RUN chmod +x create_db.py
RUN chmod +x run.py

ENV SECRET_KEY 71C9xqqxCZ

# Запуск сервера
CMD ["python", "create_db.py"]
CMD ["python", "run.py"]