FROM python:3.7

RUN pip install -r requirements.txt

COPY ./app /app

CMD ["python3", "/app/main.py"]
