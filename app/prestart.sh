#! /usr/bin/env bash
set -e

echo "########################## in docker-prestart file ###################"

######## create client_secrets.json file from environment ###########
cat > /app/client_secrets.json <<EOF
{
    "web": {
        "client_id": "$CLIENT_ID",
        "client_secret": "$CLIENT_SECRET",
        "auth_uri": "https://dev-635623.okta.com/oauth2/default/v1/authorize",
        "token_uri": "https://dev-635623.okta.com/oauth2/default/v1/token",
        "issuer": "https://dev-635623.okta.com/oauth2/default",
        "userinfo_uri": "https://dev-635623.okta.com/oauth2/default/userinfo",
        "token_introspection_uri": "https://dev-635623.okta.com/oauth2/default/v1/introspect",
        "redirect_uris": [
            "https://lights.ashleynewton.net", "http://lights.ashleynewton.net", "http://localhost:3000/index.html", "http://localhost:3002/", "http://localhost:3000", "http://localhost:80", "http://localhost"
        ],
        "allowed_users": ["i@ashleynewton.net", "guest@ashleynewton.net"],
        "cid": "$CLIENT_ID",
        "aud": "default",
        "auth_token": "$AUTH_TOKEN",
        "keys_uri": "https://dev-635623.okta.com/oauth2/default/v1/keys"
    }
}
EOF


cat /app/client_secrets.json


########### use if adding https to nginx config ##############
# cat > /etc/nginx/conf.d/https.conf <<EOF

# server {
#     listen 443 ssl;
#     server_name localhost;
#     ssl_certificate /app/certificates/$cert_file;
#     ssl_certificate_key /app/certificates/$key_file;
#     location / {
#         try_files \$uri @app;
#     }
#     location @app {
#         include uwsgi_params;
#         uwsgi_pass unix:///tmp/uwsgi.sock;
#     }
#     location /static {
#         alias /app/static;
#     }
# }

# EOF

# ls -la

# cat  /etc/nginx/nginx.conf

#exec "$@"