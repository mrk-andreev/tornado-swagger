ARG PY_VERSION
FROM python:$PY_VERSION
WORKDIR /opt/app

RUN apt update -qq && apt install -y make -qq
COPY requirements.txt .
COPY requirements-dev.txt .
RUN pip install  --default-timeout=1000 --prefer-binary --no-cache-dir -r ./requirements-dev.txt
COPY . .