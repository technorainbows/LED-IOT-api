var host;

if (window.location.hostname === 'localhost') {
    host = "http://" + window.location.host;
} else {
    host = "http://lights.ashleynewton.net";
}

var oktaSignIn = new OktaSignIn({
    baseUrl: "https://dev-635623.okta.com",
    clientId: '0oa1518xwoMoaewF64x6',
    redirectUri: host + "/index.html",
    authParams: {
        issuer: 'default',
        responseType: ['token', 'id_token'],
        display: 'page',
        // pkce: 'true'
    }
});
var oktaDomain = "https://dev-635623.okta.com"
var clientId = "0oa1518xwoMoaewF64x6"

$('#main-content').hide();

if (oktaSignIn.hasTokensInUrl()) {
    console.log("has token in url");
    // console.log(res.claims)
    oktaSignIn.authClient.token.parseFromUrl().then(function success(tokens) {
            // Save the tokens for later use, e.g. if the page gets refreshed:
            // Add the token to tokenManager to automatically renew the token when needed

            tokens.forEach(token => {
                if (token.idToken) {
                    // console.log("id token found");
                    // console.log(token.idToken);

                    oktaSignIn.authClient.tokenManager.add('idToken', token);
                }
                if (token.accessToken) {
                    // console.log("access token found");
                    // console.log(token.accessToken);
                    // callMessagesApi(token.accessToken);
                    oktaSignIn.authClient.tokenManager.add('accessToken', token);
                    localStorage.setItem('accessToken', token.accessToken);
                    // console.log("about to set token in storage");
                    console.log("setting token in storage: ", localStorage.getItem('accessToken'));


                }
            });

            // Say hello to the person who just signed in:
            oktaSignIn.authClient.tokenManager.get('idToken').then(function(idToken) {
                // document.getElementById("messageBox").innerHTML = "Hello, " + idToken.claims.email + "! You just logged in! :)";
                // document.getElementById("main-content")
                // $("main-content").toggle();
                console.log('Hello, ' + idToken.claims.email);
                // $('#main-content').toggle(display);
                $('#main-content').show();
                // callMessagesApi(token.accessToken);

                window.location.hash = '';
                window.location.reload();


            });




            // Remove the tokens from the window location hash
            window.location.hash = '';

        },
        function error(err) {
            // handle errors as needed
            console.error(err);
        }
    );
} else {
    oktaSignIn.authClient.session.get().then(function(res) {
        // Session exists, show logged in state.

        if (res.status === 'ACTIVE') {
            console.log("already logged in respone: ", res)
            console.log('Welcome back, ' + res.login);
            var accessToken = localStorage.getItem('accessToken');
            console.log("got accessToken: ", accessToken);
            // document.getElementById("messageBox").innerHTML = "Hello, " + res.login + "! You are *still* logged in! :)";
            $('#main-content').show();
            // callMessagesApi(accessToken);
            return;
        }

        // No session, show the login form and hide main content
        $('#main-content').hide();
        oktaSignIn.renderEl({ el: '#okta-login-container' },
            function success(res) {
                // Nothing to do in this case, the widget will automatically redirect
                // the user to Okta for authentication, then back to this page if successful
                // $('#main-content').hide();
                // console.log("not logged in");
            },
            function error(err) {
                // handle errors as needed
                console.error(err);
            }
        );
    });
}

function callMessagesApi(accessToken) {
    // var accessToken = oktaSignIn.authClient.tokenManager.get("accessToken");
    console.log("callMessagesApi");

    if (!accessToken) {
        console.log("no accessToken to send to API");
        return;
    }

    console.log("making api request with token: ", accessToken);
    // Make the request using jQuery
    $.ajax({

        url: 'https://api.ashleynewton.net/Devices',
        type: 'GET',
        withCredentials: true,
        dataType: 'json',
        contentType: 'application/json',
        headers: {
            "Access-Control-Allow-Origin": "*",
            "Authorization": "Bearer " + accessToken,
            "Content-Type": "application/json",
            "Accept": "application/json"
        },
        success: function(response) {
            // Received messages!
            console.log('Messages', response);
        },
        error: function(response) {
            console.error(response);
        }
    });
}