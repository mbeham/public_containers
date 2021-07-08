FROM python:3.9-alpine

WORKDIR /app
ADD main.py /app
ADD requirements.txt /app

RUN python -m pip install -r requirements.txt

CMD [ "python", "./main.py" ]