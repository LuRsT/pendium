FROM alpine:latest

RUN apk add --update python py-pip git

RUN git clone https://github.com/LuRsT/Pendium.git /pendium
RUN pip install -r /pendium/requirements.txt

EXPOSE 5000

CMD python /pendium/run.py
