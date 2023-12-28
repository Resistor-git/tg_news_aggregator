FROM python:3.12-alpine
LABEL authors="Resistor"
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE 1
RUN pip install pip --upgrade
COPY . .
RUN pip install -r requirements.txt --no-cache-dir
CMD ["python3", "bot_pyrogram.py"]