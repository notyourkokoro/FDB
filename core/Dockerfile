FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONFAULTHANDLER 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update &&  \
    apt-get install -y --no-install-recommends  \
    curl  \
    && apt-get clean  \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip uv

RUN uv venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /srv/app
COPY requirements.txt .

RUN uv pip sync ./requirements.txt
