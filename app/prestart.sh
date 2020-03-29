#! /usr/bin/env bash
set -e

echo "########################## in docker-prestart file ###################"

######## Generate HTTPS certificates from environment ###########
# touch /app/certificates/test.crt
cat > /app/certificates/testing.crt <<EOF
$API_CERTIFICATE
EOF

cat > /app/certificates/testing.key <<EOF
$API_KEY
EOF

cat /app/certificates/testing.crt
cat /app/certificates/testing.key

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
            "http://localhost:80/authorization-code/callback", "http://localhost:3002/authorization-code/callback", "http://localhost:3002/index.html", "http://localhost:3002/", "http://localhost:3002", "http://localhost:80", "http://localhost:80/api", "http://localhost:80/private", "http://localhost"
        ],
        "allowed_users": ["i@ashleynewton.net"],
        "cid": "$CLIENT_ID",
        "aud": "default",
        "auth_token": "$AUTH_TOKEN"
    }
}
EOF




cat /app/client_secrets.json


########### add https to nginx config ##############
cat > /etc/nginx/conf.d/https.conf <<EOF

server {
    listen 443 ssl;
    server_name localhost;
    ssl_certificate /app/certificates/testing.crt;
    ssl_certificate_key /app/certificates/testing.key;
    location / {
        try_files \$uri @app;
    }
    location @app {
        include uwsgi_params;
        uwsgi_pass unix:///tmp/uwsgi.sock;
    }
    location /static {
        alias /app/static;
    }
}

EOF

ls -la

cat  /etc/nginx/nginx.conf

#exec "$@"