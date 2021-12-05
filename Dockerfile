FROM python:3.9-slim-buster

WORKDIR /src

ENV PYTHONUNBUFFERED=1

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

ENTRYPOINT ["python", "balancer.py"]