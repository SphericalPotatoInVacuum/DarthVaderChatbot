FROM python:3.10

WORKDIR /chatbot

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY configs configs/
COPY src src/

CMD ["python3", "src/main.py"]
