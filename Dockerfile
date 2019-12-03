FROM python:3.7-slim
LABEL maintainer="bob.coggeshall@gmail.com"
RUN mkdir /home/tinyurl
WORKDIR /home/tinyurl
COPY . .
COPY app/ app/
RUN pip3 install -r requirements.txt
EXPOSE 60000
#ENTRYPOINT ["python3","./run.py"]

