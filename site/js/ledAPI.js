(function(global) {

    var dc = {}; // namespace for document content

    // var apiUrl = 'http://lvh.me:5000'
    // var apiUrl = 'http://10.0.0.59:5000/light' // ip address at home
    var apiUrl = 'http://192.168.2.54:5000/light' // ip address when at CDA

    // var apiURL = 'https://jsonplaceholder.typicode.com/posts' // test external json server
    console.log('ledAPI running');



    document.addEventListener("DOMContentLoaded", function(event) {

        // showLoading("#main-content");
        $apiUtils.getData(apiUrl, "on", updateLedState);
        // console.log("var ledState = " + lightState.);


        function updateLedState(light) {
        	console.log("light.ledState = " + light.ledState);

            switch (light.ledState) {
                case true:
                	console.log("light on");
                	// $(#ledOn).
                    // $("#ledON").setAttribute('active');
                    document.querySelector('#ledON').closest('label').classList.add('active')
                    document.querySelector('#ledOFF').closest('label').classList.remove('active')
                    break;
                case false:
                	console.log("light off");
                    // $("#ledOFF").setAttribute('active');
                    document.querySelector('#ledOFF').closest('label').classList.add('active')
                    document.querySelector('#ledON').closest('label').classList.remove('active')
                    break;
            }
        }

    });



    // when btn-ledState is clicked, calls postData to update ledState on API
    $(document).ready(function() {

        $("#btn-ledState :input").change(function() {
            console.log(this.id); // points to the clicked input button
            switch (this.id) {
                case "ledON":
                    $apiUtils.postRequest(apiUrl, 'on', 'true');
                    break;
                case "ledOFF":
                    $apiUtils.postRequest(apiUrl, 'on', 'false');
                    break;
            }

        });


    });


})(window);





    // // Convenience function for inserting innerHTML for 'select'
    // var insertHtml = function(selector, html) {
    //     var targetElem = document.querySelector(selector);
    //     targetElem.innerHTML = html;
    // };

    // // Show loading icon inside element identified by 'selector'.
    // var showLoading = function(selector) {
    //     var html = "<div class='text-center'>";
    //     html += "<img src='images/ajax-loader.gif'></div>";
    //     insertHtml(selector, html);
    // };

    // // Return substitute of '{{propName}}'
    // // with propValue in given 'string'
    // var insertProperty = function(string, propName, propValue) {
    //     var propToReplace = "{{" + propName + "}}";
    //     string = string
    //         .replace(new RegExp(propToReplace, "g"), propValue);
    //     return string;
    // };

