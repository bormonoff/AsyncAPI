FROM python:3.10-alpine

RUN apk update && \
    apk add --no-cache build-base gcc python3-dev libffi-dev py3-pip

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    LANG=C.UTF-8 \
    APP_HOME=/src

WORKDIR $APP_HOME

ARG GID=1000
ARG UID=1000
ARG USER=async_api
RUN addgroup -g $GID -S $USER  \
    && adduser -S $USER -G $USER --disabled-password --uid "$UID"

RUN pip install --upgrade pip poetry

COPY --chown=$USER:$USER ./pyproject.toml pyproject.toml
RUN poetry export -f requirements.txt --output requirements.txt
RUN pip install -r requirements.txt --no-cache-dir

COPY --chown=$USER:$USER ./src $APP_HOME

USER $USER

ENTRYPOINT ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
