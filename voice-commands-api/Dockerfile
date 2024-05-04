FROM python:3.12.3-slim

WORKDIR /app
COPY ./requirements.txt /app

RUN apt-get update && apt-get install -y ffmpeg
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

ENV FLASK_APP=api.py

CMD ["python", "-u", "api.py"]
