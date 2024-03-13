# syntax=docker/dockerfile:1

FROM python:latest
WORKDIR /src/
ADD requirements.txt /src/
RUN pip install --no-cache-dir -r requirements.txt

ADD * /src/

ADD run.sh /src/

CMD [ "./run.sh"]