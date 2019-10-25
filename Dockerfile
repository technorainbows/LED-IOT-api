FROM tiangolo/uwsgi-nginx-flask:python3.7

COPY ./app /app

# WORKDIR /app

# EXPOSE 5000
# EXPOSE 80
# EXPOSE 8080

# RUN python --version

RUN  pip3 install redis flask_restplus flask_cors
