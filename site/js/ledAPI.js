(function(global) {

    var dc = {}; // namespace for document content

    // var apiUrl = 'http://lvh.me:5000'
    var apiUrl = 'http://10.0.0.59:5000/light' // ip address at home
    // var apiUrl = 'http://192.168.2.54:5000/light' // ip address when at CDA

    // var apiURL = 'https://jsonplaceholder.typicode.com/posts' // test external json server
    // console.log('ledAPI running');


    /************* 
    * UI VARIABLES
    *************/

	var brightSlider = document.getElementById('slider-brightness');


    /* Every X seconds send get request to server to check if connected/in sync. 
     * If connected, main content is updated/enabled, otherwise main-content is disabled.
     */
    function checkConnection() {
        $apiUtils.getData(apiUrl, "on", updateMainContent, disableMainContent);
        setTimeout(checkConnection, 5000);
    }

    /*
     * Initiates connection with API and also listens for events 	
     */
    function startLoadingPage() {

        console.log("Initializing client.");

        // show loading UI / message
        // showLoading("#main-content");

        // connect to API (get request)
        $apiUtils.getData(apiUrl, "on", updateMainContent, disableMainContent);


        // when btn-ledState is clicked, calls postData to update ledState on API
        $("#btn-ledState :input").change(function() {

            // console.log("User input received, now starting API request.");
            // console.log(this.id); // points to the clicked input button
            switch (this.id) {
                case "ledON":
                    $apiUtils.postRequest(apiUrl, 'on', 'true');
                    break;
                case "ledOFF":
                    $apiUtils.postRequest(apiUrl, 'on', 'false');
                    break;
            }

        });


        $('input[name=slider-brightness]').change('mousestop', function() {
        	var value = this.value;
        	value=value.toString();
            console.log("POSTING brightness value: ", value);
            $apiUtils.postRequest(apiUrl,'brightness',value);
        });

		$(document).on('input change', '#slider-brightness', function() {
			var sValue = $(this).val();
			console.log("sValue changed: " + sValue);
		    $('#brightness-value').html( sValue );
		    
		});
		// var brightSlider = $"#slider-brightness";
	
    // brightSlider.oninput = function() {
    //     console.log("slider value = ", brightSlider.value);
    // }
    // var sliderVal = document.getElementById('slider-brightness').value;
    // console.log("sliderVal = ", sliderVal);
    //       // console.log($("#slider-brightness").value);
    // (function(){
    // 	var brightVal = this.getValue();
    // 	console.log("brightness slider changed: " + brightVal);
    // 	// $apiUtils.postRequest(apiUrl,'brightness',this.input);
    // })


    }



    /*
     *   Call this function with a successful response from the server (at end of API request)
     *   When this is called, you know that the server is happy. When this function is done, the page should reflect that it's ready for more user interaction
     * 	To rephrase that, at the end of this function the state of UI is "ready"
     */
    function updateMainContent(lightProps) {
        updateOnButton(lightProps);
        // TODO: update other properties as added
        $("#main-content").show("slow");

        // console.log("Page updated from server, ready for user input.");

    }

    /*
     * Call this function when the server is no longer connected. This will hide all content in "#main-content".
     */
    function disableMainContent() {
        console.log("disabling main content");
        $("#main-content").hide("slow");

    }


    function updateOnButton(lightProps) {
        // console.log("light.ledState = " + lightProps.ledState);

        switch (lightProps.ledState) {
            case true:
                // console.log("light on");
                // $(#ledOn).
                // $("#ledON").setAttribute('active');
                $('#ledON').closest('label').toggleClass('active', true);

                $('#ledOFF').closest('label').toggleClass('active', false);

                // $('#ledON').closest('label').classList.add('active');                
                // document.querySelector('#ledON').closest('label').classList.add('active')
                // document.querySelector('#ledOFF').closest('label').classList.remove('active')
                break;
            case false:
                // console.log("light off");
                $('#ledON').closest('label').toggleClass('active', false);
                $('#ledOFF').closest('label').toggleClass('active', true);

                // document.querySelector('#ledOFF').closest('label').classList.add('active')
                // document.querySelector('#ledON').closest('label').classList.remove('active')
                break;
        }
    }



    // TODO: ADD ERROR RENDERING FUNCTIONALITY TO UI



    document.addEventListener('DOMContentLoaded', startLoadingPage);
    checkConnection();





})(window);