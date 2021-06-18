FROM python:3.9

RUN mkdir -p /usr/src/pythonyansound/

COPY . /usr/src/pythonyansound/

WORKDIR /usr/src/pythonyansound/

RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /usr/src/pythonyansound/pythonyanssound/
