#! /usr/bin/env bash
set -e

echo "########################## in docker-prestart file ###################"

# cert_file=temp_cert.crt
# key_file=testing.key

# echo "######## Generate HTTPS certificates from environment ###########"
# # touch /app/certificates/test.crt
# mkdir -p /app/certificates

# echo "#### create files #####"
# # rm /app/certificates/$cert_file.crt
# touch /app/certificates/$cert_file

# # rm /app/certificates/$key_file
# touch /app/certificates/$key_file

# echo "# check variables exist"
# echo $API_CERTIFICATE_B64   

# echo $API_CERTIFICATE_B64 | base64 -di > /app/certificates/$cert_file
# # mv /app/certificates/temp_cert.pem /app/certificates/testing.pem
# cat /app/certificates/$cert_file

# # cat /app/certificates/testing.key
# echo $API_KEY_B64 | base64 -di > /app/certificates/$key_file
# # mv /app/certificates/temp_key.key /app/certificates/testing.key
# cat /app/certificates/$key_file

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
            "https://lights.ashleynewton.net", "http://lights.ashleynewton.net", "http://localhost:80/authorization-code/callback", "http://localhost:3002/authorization-code/callback", "http://localhost:3002/index.html", "http://localhost:3002/", "http://localhost:3002", "http://localhost:80", "http://localhost:80/api", "http://localhost:80/private", "http://localhost"
        ],
        "allowed_users": ["i@ashleynewton.net", "guest@ashleynewton.net"],
        "cid": "$CLIENT_ID",
        "aud": "default",
        "auth_token": "$AUTH_TOKEN"
    }
}
EOF




cat /app/client_secrets.json


########### add https to nginx config ##############
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