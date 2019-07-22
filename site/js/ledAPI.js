var apiURL = 'http://127.0.0.1:5000/light'
// var apiURL = 'https://jsonplaceholder.typicode.com/posts'
console.log('ledAPI called');


// $(document).ready(function() {
// 	$.ajax({
// 		url: 'apiURL',
// 		type:"GET",
// 		// contentType: "application/json",
// 		// dataType: 'json'
// 		success: function(result){
// 		console.log(result)
// 	},
// 	error:function(error){
// 		console.log('Error $(error)')
// 	}

// 	})
// })



// const Http = new XMLHttpRequest();
// const url = apiURL;
// Http.open("GET", url);
// Http.send();

// Http.onreadystatechange = (e) => {
//     console.log(Http.responseText)
// }



// fetch('apiURL')
// POST 

// postData(apiURL, {answer: 42})
//   .then(data => console.log(JSON.stringify(data))) // JSON-string from `response.json()` call
//   .catch(error => console.error(error));

// function postData(url = '', data = {}) {
// Default options are marked with *
// return 

// fetch(apiURL, {
//     method: 'POST', // *GET, POST, PUT, DELETE, etc.
//     mode: 'cors', // no-cors, cors, *same-origin
//     cache: 'no-cache', // *default, no-cache, reload, force-cache, only-if-cached
//     credentials: 'same-origin', // include, *same-origin, omit
//     headers: {
//         'Content-Type': 'application/json',
//         // 'Content-Type': 'application/x-www-form-urlencoded',
//     },
//     redirect: 'follow', // manual, *follow, error
//     referrer: 'no-referrer', // no-referrer, *client
//     body: JSON.stringify({'true'}), // body data type must match "Content-Type" header
// })
// .then(response => response.json()); // parses JSON response into native JavaScript objects 
// }
console.log('POST request:')
fetch("http://lvh.me:5000/light/true", {
        "credentials": "omit",
        "headers": {
            "accept": "application/json",
            // "content-type": "application/json",
            // "Access-Control-Allow-Origin'":"*'"
        },
        "referrer": "http://lvh.me:5000/",
        "referrerPolicy": "no-referrer-when-downgrade",
        "body": JSON.stringify('true'),
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


console.log('GET request:')
// GET
fetch("http://lvh.me:5000/light", { "credentials": "omit", "headers": { "accept": "application/json",
	// "Access-Control-Allow-Origin'":"*'" 
}, "referrer": "http://lvh.me:5000/", "referrerPolicy": "no-referrer-when-downgrade", "body": null, "method": "GET", "mode": "cors" })


    .then(function(response) {
        console.log(response);
        return response.json();

    })
    .then(function(myJson) {
        console.log(JSON.stringify(myJson));
    });