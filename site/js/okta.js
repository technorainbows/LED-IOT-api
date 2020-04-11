var oktaSignIn = new OktaSignIn({
    baseUrl: "https://dev-635623.okta.com",
    clientId: '0oa1518xwoMoaewF64x6',
    redirectUri: "http://lights.ashleynewton.net/index.html",
    authParams: {
        issuer: 'default',
        responseType: ['token', 'id_token'],
        display: 'page',
        // pkce: 'true'
    }
});
var oktaDomain = "https://dev-635623.okta.com"
var clientId = "0oa1518xwoMoaewF64x6"

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
                document.getElementById("messageBox").innerHTML = "Hello, " + idToken.claims.email + "! You just logged in! :)";
                // document.getElementById("main-content")
                // $("main-content").toggle();
                console.log('Hello, ' + idToken.claims.email);
                // $('#main-content').toggle(display);
                $('#main-content').show();
                // callMessagesApi(token.accessToken);
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
                // console.log("poop");
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


// function callMessagesApi2() {
//     var accessToken = oktaSignIn.authClient.tokenManager.get("accessToken");
//     console.log("callMessagesApi");

//     if (!accessToken) {
//         console.log("no accessToken to send to API");
//         return;
//     }

//     console.log("making api request with token: ", accessToken);
//     // Make the request using jQuery
//     fetch('http://localhost:8080/api', {

//         "headers:" {
//             Authorization: 'Bearer ' + accessToken
//         },
//         success: function(response) {
//             // Received messages!
//             console.log('Messages', response);
//         },
//         error: function(response) {
//             console.error(response);
//         }
//     });
// }

// function callMessagesApi(accessToken){
//     var url = 'http://localhost:8080/api';

//     fetch(url, {
//         "credentials": "omit",
//         "headers": {
//             "accept": "application/json",
//             "content-type": "application/json",
//             "Access-Control-Allow-Origin'": "*'"
//         },
//         "referrer": url,
//         "referrerPolicy": "no-referrer-when-downgrade",
//         // "body": JSON.stringify(paramValue),
//         "method": "POST",
//         "mode": "cors",
//     })

//     .then(function(response) {
//         // console.log(response);
//         return response.json();

//     })
//     .then(function(myJson) {
//         // console.log(JSON.stringify(myJson));
//     });


// }





// (function(global) {
//     var oktaSignIn = new OktaSignIn({
//         baseUrl: "https://dev-635623.okta.com",
//         el: '#okta-login-container',
//         clientId: "0oa1387dtuitnTRh54x6",
//         redirectUri: "http://localhost:3002/index.html",
//         getAccesstoken: true,
//         authParams: {
//             issuer: "https://dev-635623.okta.com/oauth2/default",
//             responseType: ['token', 'id_token'],
//             display: 'page'
//         }

//     });


// oktaSignIn.showSignInToGetTokens({
//     clientId: '0oa1387dtuitnTRh54x6',

//     // must be in the list of redirect URIs enabled for the OIDC app
//     redirectUri: 'http://localhost:3002/index.html',

//     // Return an access token from the authorization server
//     getAccessToken: true,

//     // Return an ID token from the authorization server
//     getIdToken: true,
//     scope: 'openid profile'
// });


//     if (oktaSignIn.hasTokensInUrl()) {
//         console.log("has token in url");
//         console.log(res);
//         // signIn.tokenManager.add('my_id_token', res);


//         oktaSignIn.authClient.token.parseFromUrl(
//             function success(tokens) {
//                 // Save the tokens for later use, e.g. if the page gets refreshed:
//                 // Add the token to tokenManager to automatically renew the token when needed
//                 console.log("got tokens");

//                 tokens.forEach(token => {
//                     if (token.idToken) {

//                         signIn.tokenManager.add('idToken', token);
//                         console.log("got id token");
//                     }
//                     if (token.accessToken) {
//                         signIn.tokenManager.add('accessToken', token);
//                         console.log("got accesstoken");
//                     }
//                 });

//                 // Say hello to the person who just signed in:
//                 var idToken = signIn.tokenManager.get('idToken');
//                 // var accessToken = "poop";
//                 var accessToken = signIn.tokenManager.get('access_token');
//                 console.log('Hello, ' + idToken.claims.email);
//                 document.getElementById("messageBox").innerHTML = "Hello, " + idToken.claims.email + "! You just logged in! :)";
//                 if (accessToken) {
//                     console.log("Here's your access token: " + accessToken.accessToken);
//                 }
//                 // Remove the tokens from the window location hash
//                 window.location.hash = '';
//             },
//             function error(err) {
//                 // handle errors as needed
//                 console.error(err);
//             }
//         );
//     } else {
//         oktaSignIn.authClient.session.get().then(function(res) {
//             console.log("does not have token in url");
//             // Session exists, show logged in state.
//             if (res.status === 'ACTIVE') {
//                 console.log('POOP Welcome back, ' + res.login);
//                 document.getElementById("messageBox").innerHTML = "Hello, " + res.login + "! You are *still* logged in! :)";
//                 // console.log("POOP Here's your accessToken: " + accessToken);
//                 if (accessToken) {
//                     console.log("Here's your access token: ");
//                     console.log(accessToken.accessToken);
//                 }
//                 return;
//             }
//             // No session, show the login form
//             oktaSignIn.renderEl({ el: '#okta-login-container' },
//                 function success(res) {
//                     // Nothing to do in this case, the widget will automatically redirect
//                     // the user to Okta for authentication, then back to this page if successful
//                 },
//                 function error(err) {
//                     // handle errors as needed
//                     console.error(err);
//                 }
//             );
//         });
//     }


// })(window);

// (function(global) {
//     var yourOktaDomain = "https://dev-635623.okta.com"
//     var oktaDashboardUrl = "https://dev-635623.okta.com/home/oidc_client/0oa1387dtuitnTRh54x6/aln177a159h7Zf52X0g8"
//     var clientID = "0oa1387dtuitnTRh54x6"
//     var redirectUri = "http://localhost:3002"

//     var signIn = new OktaSignIn({
//         baseUrl: 'https://dev-635623.okta.com'
//     });
//     signIn.renderEl({
//         el: '#widget-container'
//     }, function success(res) {
//         if (res.status === 'SUCCESS') {
//             console.log('Do something with this sessionToken', res.session.token);
//             res.session.setCookieAndRedirect(oktaDashboardUrl);
//         } else {
//             // The user can be in another authentication state that requires further action.
//             // For more information about these states, see:
//             //   https://github.com/okta/okta-signin-widget#rendereloptions-success-error
//         }
//     });

//     var signIn = new OktaSignIn({
//         baseUrl: 'https://dev-635623.okta.com',
//         el: '#widget-container',
//         authParams: {
//             issuer: 'https://dev-635623.okta.com/oauth2/default'
//         }
//     });

//     signIn.showSignInToGetTokens({
//         clientId: '0oa1387dtuitnTRh54x6',

//         // must be in the list of redirect URIs enabled for the OIDC app
//         // redirectUri: 'http://localhost:3002',

//         // Return an access token from the authorization server
//         getAccessToken: true,

//         // Return an ID token from the authorization server
//         getIdToken: true,
//         scope: 'openid profile'
//     });

//     var accessToken = signIn.tokenManager.get('access_token');

//     //        if (!accessToken) {
//     // This means that the user is not logged in
//     //          console.log("user not logged in");
//     //        return;
//     //  }


//     // If we get here, the user just logged in.
//     if (accessToken) {
//         //function success(res) {
//         var idToken = signIn.tokenManager.get('id_token');
//         //var accessToken = res[0];
//         //var idToken = res[1]

//         signIn.tokenManager.add("accessToken", accessToken);
//         signIn.tokenManager.add("idToken", idToken);

//         window.location.hash = "";
//         document.getElementById("messageBox").innerHTML = "Hello, " + idToken.claims.email + "! You just logged in! :)";
//     } else {
//         signIn.session.get(function(res) {
//             // If we get here, the user is already signed in.
//             if (res.status === 'ACTIVE') {
//                 document.getElementById("messageBox").innerHTML = "Hello, " + res.login + "! You are *still* logged in! :)";
//                 return;
//             }

//             // If we get here, the user is not logged in, so we should show the sign-in form.
//             signIn.renderEl({
//                     el: '#widget-container'
//                 },
//                 function success(res) {},
//                 function error(err) {
//                     console.error(err);
//                 }
//             );
//         });
//     }

// })(window);