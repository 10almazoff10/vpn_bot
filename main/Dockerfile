# syntax=docker/dockerfile:1

FROM python:latest
WORKDIR /src/
ADD requirements.txt /src/
RUN apt update && apt install cron -y 
RUN service cron start
RUN pip install --no-cache-dir -r requirements.txt

ADD config.py /src/
ADD dbcon.py /src/
ADD main.py /src/
ADD messages.py /src/
ADD outline_api_reqests.py /src/
ADD tg_keyboard.py /src/
ADD backend.py /src/
ADD run.sh /src/

CMD [ "./run.sh"]