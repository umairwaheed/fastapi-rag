FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8

WORKDIR /opt/code

COPY ./requirements.txt /opt/code/requirements.txt

RUN pip install -U pip && pip install --no-cache-dir -r /opt/code/requirements.txt

COPY ./app /opt/code/app
COPY ./scripts/create_admin.py /opt/code/scripts/

CMD ["fastapi", "run", "app/main.py", "--port", "80"]
