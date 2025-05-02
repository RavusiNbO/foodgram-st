FROM python:3.12

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

WORKDIR /app/foodgram

RUN python manage.py collectstatic


CMD ["gunicorn", "--bind", "0.0.0.0:8000", "foodgram.wsgi"]
