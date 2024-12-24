FROM python:3.13.1-slim-bookworm

WORKDIR /usr/local/app

COPY requirements.txt ./

RUN pip3 install --no-cache-dir -r requirements.txt

COPY src/ ./

CMD [ "python3", "main.py" ]
