FROM python:3

WORKDIR /usr/src/app

RUN pip install --no-cache-dir flask

COPY bin/web.py .

CMD [ "python", "./web.py" ]
