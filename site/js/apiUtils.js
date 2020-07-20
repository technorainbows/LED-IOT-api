// TODO: Add "displayErrorOnPage" function
// ?: Should postRequest, putRequest, and getRequest be merged to reduce code repetition?

(function(global) {

    // set up namespace for our utility
    var apiUtils = {};
    var accessToken = localStorage.getItem('accessToken');
    if (accessToken != null) {
        console.debug("got accesstoken in apiutils: ", accessToken);
    } else { console.warn("no accesstoken"); }

    /*
     * Sends POST request to URL+paramRoute with provided paramValue
     */
    apiUtils.postRequest = function(url, paramRoute, paramValue) {
        url += ("/" + paramRoute + "/" + paramValue);
        console.debug('POST request: ' + url)
        fetch(url, {
            "credentials": "omit",
            "headers": {
                "accept": "application/json",
                "content-type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Authorization": "Bearer " + accessToken
            },
            "referrer": url,
            "referrerPolicy": "no-referrer-when-downgrade",
            "method": "POST",
            "mode": "cors",
        })

        .then(function(response) {
                console.debug(response);
                return response.json();

            })
            .then(function(myJson) {
                console.debug(JSON.stringify(myJson));
            });

    };


    /*
     * Sends PUT request to URL/deviceID with provided paramID and paramValue
     */
    apiUtils.putRequest = function(url, deviceID, paramID, paramValue) {
        url += ("/" + deviceID);
        console.debug('PUT request: ' + url)
        var responseBody = {}
        if (paramID == 'name') {
            console.debug("param is name");
            responseBody[paramID] = paramValue;
        } else {
            responseBody[paramID] = JSON.stringify(paramValue);
        }

        console.debug('PUT body:' + JSON.stringify(responseBody))
        fetch(url, {
            "credentials": "omit",
            "headers": {
                "accept": "application/json",
                "content-type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Authorization": "Bearer " + accessToken
            },
            "referrer": url,
            "referrerPolicy": "no-referrer-when-downgrade",
            "body": JSON.stringify(responseBody),
            "method": "PUT",
            "mode": "cors",
        })

        .then(function(response) {
                console.debug("Response received - ", response);
                return response.json();

            })
            .then(function(myJson) {
                console.debug(JSON.stringify(myJson));
            });

    };


    apiUtils.getParam = async function(url, deviceID, parameter) {
        url += ("/" + deviceID);
        console.debug('GET request:' + url)
        const rec = fetch(url, {
            "credentials": "omit",
            "headers": {
                "accept": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Authorization": "Bearer " + accessToken
            },
            "referrer": url,
            "referrerPolicy": "no-referrer-when-downgrade",
            "body": null,
            "method": "GET",
            "mode": "cors"
        });

        let res;
        try {
            res = await rec;
        } catch (error) {
            console.error("Error caught!")
            console.error(error);
            updateServerStatus(false);
            return
        }

        // if no error, then get response
        let device;
        try {
            device = await res.json();
            console.debug("device returned: ", device);
            let paramReq = device[1][parameter];
            console.debug("parameter = ", paramReq);
            updateServerStatus(true);
            console.debug("")
            return paramReq;
        } catch (error) {
            console.error("Error caught!!! - ", error);
            updateServerStatus(false);
            return
        }

    };

    /*
     * Requests data from api and returns json object to responseHandler provided. If fetch fails, errorHandler funcion is called.
     * Success/fail state of fetch is also passed to updateServerStatus function. 
     */

    apiUtils.getData = async function(url, deviceID, responseHandler,
        errorHandler) {

        // TODO: is there a better place to check for accessToken?
        if (!accessToken) {
            updateServerStatus(false);
            errorHandler();
            return;
        }

        url += ("/" + deviceID);
        const rec = fetch(url, {
            "credentials": "omit",
            "headers": {
                "accept": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Authorization": "Bearer " + accessToken

            },
            "referrer": url,
            "referrerPolicy": "no-referrer-when-downgrade",
            "body": null,
            "method": "GET",
            "mode": "cors"
        });

        let res;
        try {
            res = await rec;
        } catch (error) {
            console.error("Error caught!!! - ", error);
            updateServerStatus(false);
            errorHandler();
            return
        }

        // if no error, then get response
        let device = await res.json();

        updateServerStatus(true);
        responseHandler(device);

    };

    function updateServerStatus(status) {
        console.debug("updating server status: " + status);

        if (status) {
            $('#icon-disconnected').hide();
            $('#icon-connected').show();
        } else {
            $('#icon-disconnected').show();
            $('#icon-connected').hide();
        }
    }

    // Expose utility to the global object
    global.$apiUtils = apiUtils;

})(window);