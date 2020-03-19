FROM tiangolo/uwsgi-nginx-flask:python3.7

COPY ./app /app
COPY ./load_secrets.sh /app
# RUN chmod +x load_secrets.sh
# COPY ./docker-entrypoint.sh ./prestart.sh
# RUN chmod +x prestart.sh

RUN ls -la

# RUN cat prestart.sh

# RUN cat ./client_secrets.json
RUN  python -m pip install -r /app/requirements.txt
# RUN bash | ./load_secrets.sh cat ./client_secrets.json



###EVERYTHING ABOVE THIS LINE RUNS DURING BUILDING OF THE IMAGE.
### EVERYTHING BELOW THIS LINE RUNS AT "RUNTIME"

#CMD [bash | load_secrets.sh cat ./client_secrets.json 
#CMD 1: load the secrets from the env to the json. 2: run the normal CMD.

#CMD ashleys_new_launch.sh old_cmd_thingy_that_you_will_have_to_find_out.sh  

# ENTRYPOINT ["docker-entrypoint.sh"]

# CMD ["prestart.sh"] 

