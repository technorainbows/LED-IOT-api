FROM tiangolo/uwsgi-nginx-flask:python3.7

COPY ./app /app
# COPY ./load_secrets.sh /app

RUN ls -la

RUN  python -m pip install -r /app/requirements.txt


