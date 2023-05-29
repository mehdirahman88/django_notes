FROM python:3.9

ENV PYTHONUNBUFFERED=1

WORKDIR /django-notes-app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

# Run migrations and start server
CMD python3 manage.py makemigrations && python3 manage.py migrate && python3 manage.py runserver 0.0.0.0:8000









