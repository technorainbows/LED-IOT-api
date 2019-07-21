
// var apiURL = 'http://127.0.0.1:5000/light'
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
// fetch("http://127.0.0.1:5000/light/true", {"credentials":"omit","headers":{"accept":"application/json","content-type":"application/json"},"referrer":"http://127.0.0.1:5000/","referrerPolicy":"no-referrer-when-downgrade","body":null,"method":"POST","mode":"cors"})

// 	.then(function(response) {
// 		console.log(response);
// 		return response.json();

// 	})
// 	.then(function(myJson){
// 		console.log(JSON.stringify(myJson));
// 	});



// GET
fetch("http://127.0.0.1:5000/light", {"credentials":"omit","headers":{"accept":"application/json"},"referrer":"http://127.0.0.1:5000/","referrerPolicy":"no-referrer-when-downgrade","body":null,"method":"GET","mode":"cors"})


	.then(function(response) {
		console.log(response);
		return response.json();

	})
	.then(function(myJson){
		console.log(JSON.stringify(myJson));
	});