#!/bin/bash
set -e




cat > ~/code/LED-IOT-api/client_secrets.json <<EOF
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
        "aud": "$AUD"
    }
}
EOF