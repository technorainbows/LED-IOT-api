// (function(global) {
var apiURL = 'http://lvh.me:5000/light'
// var apiURL = 'https://jsonplaceholder.typicode.com/posts'
console.log('ledAPI running');



// $(document).addEventListener("DOMContentLoaded", function (event) {
	


// when btn-ledState is clicked, calls postData to update ledState on API
$(document).ready(function() {

    $("#btn-ledState :input").change(function() {
        console.log(this.id); // points to the clicked input button
        switch(this.id) {
        	case "ledON":
        		postData('true');
        		break;
        	case "ledOFF":
        		postData('false');
        		break;
        }

    });


});

// Posts state to API when called 
function postData(state) {
    url = apiURL + "/" + state;
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
            "body": JSON.stringify(state),
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

}

// Gets ledState from api
function getData() {
    url = apiURL;
    console.log('GET request:' + url)
    // GET
    fetch(url, {
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
        })


        .then(function(response) {
            console.log(response);
            return response.json();

        })
        .then(function(myJson) {
            console.log(JSON.stringify(myJson));
        });
}

// postData('true');
// getData();

// })(window);