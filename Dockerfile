FROM python:3
ENV PYTHONUNBUFFERED=1
RUN pip install pipenv
WORKDIR /code
COPY . /code/
RUN pipenv install --system --dev --pre --ignore-pipfile
