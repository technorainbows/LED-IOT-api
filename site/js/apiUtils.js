(function(global) {

    // set up namespace for our utility
    var apiUtils = {};

    /*
    * Sends POST request to URL+paramRoute with provided paramValue
    */
    apiUtils.postRequest =
        function(url, paramRoute, paramValue) {
            // url = apiURL + "/" + state;
            url += ("/" + paramRoute + "/" + paramValue);
            // url += paramRoute;
            console.log('POST request: ' + url)
            fetch(url, {
                    "credentials": "omit",
                    "headers": {
                        "accept": "application/json",
                        // "content-type": "application/json",
                        // "Access-Control-Allow-Origin'":"*'"
                    },
                    "referrer": url,
                    "referrerPolicy": "no-referrer-when-downgrade",
                    "body": JSON.stringify(paramValue),
                    "method": "POST",
                    "mode": "cors",
                })

                .then(function(response) {
                    console.log(response);
                    return response.json();

                })
                .then(function(myJson) {
                    console.log(JSON.stringify(myJson));
                });

        };








    /*
    * Requests data from api and returns json object to responseHandler provided. If fetch fails, errorHandler funcion is called.
    * Success/fail state of fetch is also passed to updateServerStatus function. 
    */

    apiUtils.getData = async function(url, paramRoute, responseHandler, errorHandler) {
        // url = apiURL;
        // url += ("/" + paramRoute);
        // url += paramRoute;
        console.log('GET request:' + url)
        // GET
        const rec = fetch(url, {
            "credentials": "omit",
            "headers": {
                "accept": "application/json",
                // "Access-Control-Allow-Origin'":"*'" 
            },
            "referrer": url,
            "referrerPolicy": "no-referrer-when-downgrade",
            "body": null,
            "method": "GET",
            "mode": "cors"
        });

        console.log('request started.');
        console.dir(rec);

        let res;
        try {
            res = await rec; // if there is an error there will be a problem
        } catch (error) {
            console.error("Error caught!")
            console.error(error);

            // TODO: write "displayErrrorOnPage" functoion and call that here
            updateServerStatus(false);
            errorHandler();
            return
        }


        console.log('response recieved');
        console.dir(res);

        // if no error, then get response 
        let light = await res.json();
        console.log("light resp: ", light);
        let state = light.ledState;
        console.log("state = ", state);
        updateServerStatus(true);
        responseHandler(light);

    };



    function updateServerStatus(status) {
        console.log("updating server status: " + status);

        if (status) {
            $('#serverStatus').toggleClass('btn-danger', false);
            $('#serverStatus').toggleClass('btn-success', true);
        } else {
            $('#serverStatus').toggleClass('btn-danger', true);
            $('#serverStatus').toggleClass('btn-success', false);
            
        }
    }





    // Expose utility to the global object
    global.$apiUtils = apiUtils;


})(window);