(function(global) {

    // set up namespace for our utility
    var apiUtils = {};

    /*
     * TODO: UPDATE - WILL NOT WORK ANYMORE
     * Sends POST request to URL+paramRoute with provided paramValue
     */
    apiUtils.postRequest = function(url, paramRoute, paramValue) {
            // url = apiURL + "/" + state;
            url += ("/" + paramRoute + "/" + paramValue);
            // url += paramRoute;
            console.log('POST request: ' + url)
            fetch(url, {
                    "credentials": "omit",
                    "headers": {
                        "accept": "application/json",
                        "content-type": "application/json",
                        "Access-Control-Allow-Origin'": "*'"
                    },
                    "referrer": url,
                    "referrerPolicy": "no-referrer-when-downgrade",
                    // "body": JSON.stringify(paramValue),
                    "method": "POST",
                    "mode": "cors",
                })

                .then(function(response) {
                    // console.log(response);
                    return response.json();

                })
                .then(function(myJson) {
                    // console.log(JSON.stringify(myJson));
                });

        };



    /*
     * Sends PUT request to URL/deviceID with provided paramID and paramValue
     */
    apiUtils.putRequest = function(url, deviceID, paramID, paramValue) {
            // url = apiURL + "/" + state;
            url += ("/" + deviceID);
            console.log('PUT request: ' + url)
            var responseBody = {}
            responseBody[paramID]=JSON.stringify(paramValue);
            console.log('PUT body:' + JSON.stringify(responseBody))
            fetch(url, {
                    "credentials": "omit",
                    "headers": {
                        "accept": "application/json",
                        "content-type": "application/json",
                        "Access-Control-Allow-Origin": "*'"
                    },
                    "referrer": url,
                    "referrerPolicy": "no-referrer-when-downgrade",
                    "body": JSON.stringify(responseBody),
                    "method": "PUT",
                    "mode": "cors",
                })

                .then(function(response) {
                    // console.log(response);
                    return response.json();

                })
                .then(function(myJson) {
                    // console.log(JSON.stringify(myJson));
                });

        };








    /*
     * Requests data from api and returns json object to responseHandler provided. If fetch fails, errorHandler funcion is called.
     * Success/fail state of fetch is also passed to updateServerStatus function. 
     */

    apiUtils.getData = async function(url, deviceID, responseHandler, errorHandler) {
        // url = apiURL;
        url += ("/" + deviceID);
        // url += paramRoute;
        console.log('GET request:' + url)
        // GET
        const rec = fetch(url, {
            "credentials": "omit",
            "headers": {
                "accept": "application/json",
                // "Access-Control-Allow-Origin'": "*'"
            },
            "referrer": url,
            "referrerPolicy": "no-referrer-when-downgrade",
            "body": null,
            "method": "GET",
            "mode": "cors"
        });

        // console.log('request started.');
        // console.dir(rec);

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


        // console.log('response recieved');
        // console.dir(res);

        // if no error, then get response 
        let device = await res.json();
        // console.log("device returned: ", device);
        // let state = device[1]['onState'];
        // console.log("state = ", state);
        updateServerStatus(true);
        responseHandler(device);

    };



    function updateServerStatus(status) {
        // console.log("updating server status: " + status);

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