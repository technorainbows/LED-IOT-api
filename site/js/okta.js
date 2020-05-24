var host;
var oktaDomain = "https://dev-635623.okta.com"
var clientId = "0oa1518xwoMoaewF64x6"

/* Set host address dynamically. */
if (window.location.hostname === 'localhost') {
    host = "http://" + window.location.host;
} else {
    host = "http://lights.ashleynewton.net";
}

/* Okta Widget parameters */
var oktaSignIn = new OktaSignIn({
    baseUrl: "https://dev-635623.okta.com",
    clientId: clientId,
    redirectUri: host + "/index.html",
    authParams: {
        issuer: 'default',
        responseType: ['token', 'id_token'],
        display: 'page',
    }
});


/* By default, hide content until user is logged in. */
$('#main-content').hide();
$('#server-navbar').hide();

/* If token in URL, a user has just logged in, so extract it. If not, 
 * check if user is already logged in and get saved tokens, otherwise direct user to log in. */
if (oktaSignIn.hasTokensInUrl()) {
    console.info("has token in url. claims: ", res.claims);
    oktaSignIn.authClient.token.parseFromUrl().then(function success(tokens) {
            // Save the tokens for later use, e.g. if the page gets refreshed:
            // Add the token to tokenManager to automatically renew the token when needed

            tokens.forEach(token => {
                if (token.idToken) {
                    oktaSignIn.authClient.tokenManager.add('idToken', token);
                }
                if (token.accessToken) {
                    oktaSignIn.authClient.tokenManager.add('accessToken', token);
                    localStorage.setItem('accessToken', token.accessToken);
                    console.info("setting token in storage: ", localStorage.getItem('accessToken'));


                }
            });

            // Say hello to the person who just signed in:
            oktaSignIn.authClient.tokenManager.get('idToken').then(function(idToken) {
                console.info('Hello, ' + idToken.claims.email);
                $('#main-content').show();

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
            var accessToken = localStorage.getItem('accessToken');
            console.info("got accessToken: ", accessToken);
            $('#main-content').show();
            $('#server-navbar').show();
            return;
        }

        // No session, show the login form and hide main content
        $('#main-content').hide();
        $('#server-navbar').hide();
        oktaSignIn.renderEl({ el: '#okta-login-container' },
            function success(res) {
                // Nothing to do in this case, the widget will automatically redirect
                // the user to Okta for authentication, then back to this page if successful
                console.info("not logged in");
            },
            function error(err) {
                // handle errors as needed
                console.error(err);
            }
        );
    });
}