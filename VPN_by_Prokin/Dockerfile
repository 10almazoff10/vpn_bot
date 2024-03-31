# syntax=docker/dockerfile:1

FROM python:latest
WORKDIR /src/VPN_by_Prokin/
ADD requirements.txt /src/
RUN pip install --no-cache-dir -r /src/requirements.txt

COPY ./ /src/VPN_by_Prokin/

ADD --chmod=755 run.sh /src/VPN_by_Prokin/

CMD [ "/src/VPN_by_Prokin/run.sh"]