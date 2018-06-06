FROM python:3.6-alpine

ENV FLASK_APP vifi.py
ENV FLASK_CONFIG production

RUN adduser -D vifi
USER vifi

WORKDIR /home/vifi

COPY requirements requirements
RUN python -m venv venv
RUN venv/bin/pip install -r requirements/docker.txt

COPY app app
COPY migrations migrations
COPY vifi.py config.py boot.sh ./

# run-time configuration
EXPOSE 5000
ENTRYPOINT ["./boot.sh"]
