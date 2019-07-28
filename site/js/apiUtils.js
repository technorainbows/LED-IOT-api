(function (global) {
	
// set up namespace for our utility
var apiUtils = {};


// Sends POST request to URL+paramRoute with provided paramValue
apiUtils.postRequest =
function (url,paramRoute, paramValue) {
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


// Requests data from api and returns json object to responseHandler provided
apiUtils.getData = async function  (url, paramRoute, responseHandler) {
    // url = apiURL;
    // url += ("/" + paramRoute);
    // url += paramRoute;
    console.log('GET request:' + url)
    // GET
    const res = await fetch(url, {
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

    let light = await res.json();
    console.log("light resp: " + light);
    let state = light.ledState;
    console.log("state = " + state);
    responseHandler(light);
   
};

 // let ledState = light.map(paramRoute.ledState);
    // console.log("ledState = " + ledState);
    // return ledState;

  //   light = light.map()
  //   console.log(light);
  // .then(res => res.json())
  // .then(res => console.log(res))
  // .then(res => res.map(light => light.ledState))
  // .then(ledState => console.log(ledState));

   //  .then(response=>response.json())
   //  // .then(light=>console.log(light))
   //  .then(myJson=>JSON.stringify(myJson))
  	// .then (myJson=>console.log(myJson));
    // .then(myJson=>return(myJson));

		// // .then(response=>response.json())    
  //       .then(function(response) {
  //           console.log(response.json());
  //           // var test = response.json();
  //           console.log(light.ledsState);

  //           http://10.0.0.59:5000/light
  //           // return light;
  //           // return response.json();

  //       })
        // .then(function(myJson) {
        //     // console.log(JSON.stringify(myJson));
        //     console.log(myJson);
            // return myJson;
        	// return JSON.stringify(myJson);
        // })
        ;
// };






// Expose utility to the global object
global.$apiUtils = apiUtils;


})(window);







