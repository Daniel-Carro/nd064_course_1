FROM python:3.8-slim

WORKDIR /app

COPY . .

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

RUN python init_db.py

EXPOSE 3111

CMD ["python", "app.py"]