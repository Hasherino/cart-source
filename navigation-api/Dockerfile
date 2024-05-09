FROM python:3.12.3-slim

WORKDIR /app
COPY ./requirements.txt /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    bzip2 \
    g++ \
    git \
    graphviz \
    libgl1-mesa-glx \
    libhdf5-dev \
    openmpi-bin \
    wget \
    python3-tk && \
    rm -rf /var/lib/apt/lists/*
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

ENV FLASK_APP=api.py

CMD ["python", "-u", "api.py"]
