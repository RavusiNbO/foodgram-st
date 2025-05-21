FROM python:3.12

WORKDIR /app

COPY requirements.txt .

RUN pip install Django==5.1.7 django-cors-headers==4.7.0 django-rest-framework==0.1.0 djangorestframework==3.15.2
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

WORKDIR /app/foodgram

RUN python manage.py collectstatic


CMD ["gunicorn", "--bind", "0.0.0.0:8000", "foodgram.wsgi"]
