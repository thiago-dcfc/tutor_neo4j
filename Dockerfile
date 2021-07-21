FROM python:3.9.6-slim-buster

RUN apt-get update && apt-get install -qq -y \
  build-essential sudo curl --fix-missing --no-install-recommends \
  && curl -sL https://deb.nodesource.com/setup_12.x | sudo -E bash - \
  && apt install nodejs -y

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

EXPOSE 5000

COPY . .

VOLUME /static

RUN cd /app/tutor/static && npm install

CMD [ "neo4j", "start", "&&", "sleep", "15", "&&", "flask", "run" ]