FROM python:3.12-slim

WORKDIR /app

ENV PARENT_DIR=".."

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "app/main.py"]
