FROM python:3.7-buster

WORKDIR /workdir

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY models /models/

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000"]