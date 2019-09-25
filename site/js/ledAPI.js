(function(global) {

    var dc = {}; // namespace for document content

    // var apiUrl = 'http://lvh.me:5000'
    var apiUrl = 'http://10.0.0.59:5000/Devices' // ip address at home
    // var apiUrl = 'http://192.168.2.54:5000/light' // ip address when at CDA

    // var apiURL = 'https://jsonplaceholder.typicode.com/posts' // test external json server
    // console.log('ledAPI running');
    var deviceID = ''
    var devices = []
    var lastDevice = ''

    /************
     * DEVICE INFO
     ************/
    var brightness;
    var ledState;
    // var name = "AshleyRoom"

    var jsonString = ''
    /************* 
     * UI VARIABLES
     *************/

    var brightSlider = document.getElementById('slider-brightness');


    /* Every X seconds send get request to server to check if connected/in sync. 
     * If connected, main content is updated/enabled, otherwise main-content is disabled.
     */
    function checkConnection() {
        // Get list of devices online/available
        $apiUtils.getData(apiUrl + "/HB", "", updateDeviceList, disableMainContent);

        // // if current device is in heartbeat list, get device info

        // $apiUtils.getData(apiUrl, deviceID, updateMainContent, disableMainContent);
        setTimeout(checkConnection, 5000);
    }

    /*
     * Initiates connection with API and also listens for events 	
     */
    function startLoadingPage() {

        console.log("Initializing client.");
        checkConnection();
        // show loading UI / message
        // showLoading("#main-content");

        // $apiUtils.getData(apiUrl+"/HB","",updateDeviceList, disableMainContent);

        // // connect to API (get request) and update or disable main content depending on response
        // $apiUtils.getData(apiUrl, deviceID, updateMainContent, disableMainContent);
        // checkConnection();

        /* when btn-ledState is clicked, calls postData to update ledState on API */
        $("#btn-ledState :input").change(function() {

            // console.log("User input received, now starting API request.");
            // console.log(this.id); // points to the clicked input button
            switch (this.id) {
                case "ledON":
                    $apiUtils.putRequest(apiUrl, deviceID, 'onState', true);
                    break;
                case "ledOFF":
                    $apiUtils.putRequest(apiUrl, deviceID, 'onState', false);
                    break;
            }

        });

        /*  monitors brightness slider changes */
        $('input[name=slider-brightness]').change('mousestop', function() {
            var value = Number(this.value);
            // value=value.toInteg();
            console.log("PUT request brightness value: ", value);
            $apiUtils.putRequest(apiUrl, deviceID, 'brightness', value);
        });

        $(document).on('input change', '#slider-brightness', function() {
            var sValue = $(this).val();
            console.log("sValue changed: " + sValue);
            $('#brightness-value').html(sValue);

        });



        /* when a btn-device button is clicked, change deviceID to ID of clicked button and enable/update corresponding content */
        $(document).on('click', '.btn-device', function(event) {
            //Process button click event
            console.log("device selected: ", this.id);
            lastDevice = deviceID;
            deviceID = this.id
            // deviceID = (this.id).slice(3, this.id.length);
            $('#currentDeviceLabel').html(deviceID);
            console.log("deviceID set to: ", deviceID);
            $('#currentDeviceLabel').show();
            if (lastDevice == deviceID) {
	            $("#slider-brightness").prop('disabled',false);
            } else {
            	$apiUtils.getData(apiUrl, deviceID, updateMainContent, disableMainContent);
                $("#slider-brightness").prop('disabled',false);
   
            	// $("#parameter-UI").show();
            }
        });


    }



    /*
     *   Call this function with a successful response from the server (at end of API request)
     *   When this is called, you know that the server is happy. When this function is done, the page should reflect that it's ready for more user interaction
     * 	To rephrase that, at the end of this function the state of UI is "ready"
     */
    function updateMainContent(device) {
        updateOnButton(device);
        updateBrightSlider(device);
        // TODO: update other properties as added
        // $("#main-content").show("slow");
    	// $('#main-content').removeClass('look-disabled');
    	$('#main-content').toggleClass('look-disabled', false);
        console.log("Page updated from server, ready for user input.");

    }

    /*
     * Call this function when the server is no longer connected. This will hide all content in "#main-content".
     */
    function disableMainContent() {
        // console.log("disabling main content");
        // $("#main-content").hide("slow");
    	$('#main-content').toggleClass('look-disabled', true);
    	// $('#main-content').removeClass('look-enabled');
    }


    function updateOnButton(device) {
        // console.log("light.ledState = " + lightProps.ledState);
        // console.log("updateOnButton state received: ", device[1]['onState']);
        switch (device[1]['onState']) {
            case "true":
                // console.log("light on");
                $('#ledON').closest('label').toggleClass('active', true);
                $('#ledOFF').closest('label').toggleClass('active', false);
                break;
            case "false":
                // console.log("light off");
                $('#ledON').closest('label').toggleClass('active', false);
                $('#ledOFF').closest('label').toggleClass('active', true);
                break;
        }
    }


    function updateBrightSlider(device) {
        var brightVal = device[1]['brightness']
        // console.log("brightVal for slider: ", brightVal);
        $('#brightness-value').html(brightVal);
        $('#slider-brightness').val(brightVal);
        // $('#slider-brightness').slider('refresh');
        // $('#slider-brightness').html(brightVal);
    }

    function updateDeviceList(newDevices) {
        // compare new devices with old devices and insert new devices or delete devices

        // console.log("devices = ", devices);
        // console.log("newDevices = ", newDevices);
        newDevices.sort();

        var remove = [];
        var add = [];


        // Identify old devices no longer online and remove
        for (var i in devices) {
            if (newDevices.indexOf(devices[i]) === -1) remove.push(devices[i]);
        }
        // console.log("remove = ", remove)
        remove.forEach(removeDevice);

        // Hide parameter UI and current device label if not online (e.g., no heartbeat)
        if (newDevices.includes(("hb_" + deviceID)) == false) {
            $("#currentDeviceLabel").hide();
            // $("#parameter-UI").hide();
            // $(".slider-brightness").prop('disabled',true);
        	$('#brightness').toggleClass('look-disabled', true);
        	// $('#brightness').removeClass('look-enabled');   
            // console.log("hiding currentDeviceLabel");
        }
        else {
        	// console.log("getting/showing currentDeviceLabel and parameters");
        	
        	// if current device is in heartbeat list, get device info
			$apiUtils.getData(apiUrl, deviceID, updateMainContent, disableMainContent);

        	$("#currentDeviceLabel").show();
        	$('#brightness').toggleClass('look-disabled', false);
        	// $('#brightness').removeClass('look-disabled');   
        	// $(".slider-brightness").prop('disabled',false);
   
        	// $("#parameter-UI").show();
		}

        // Identify new devices received in order to add
        for (var i in newDevices) {
            if (devices.indexOf(newDevices[i]) === -1) add.push(newDevices[i]);
        }
        add.forEach(insertDevice);

        // Set devices with newDevices
        devices = newDevices;

        // $('#main-content').removeClass('look-disabled');
    	$('#main-content').toggleClass('look-disabled', false);
    }

    function insertDevice(device, index) {
    	device = device.slice(3, device.length)
        $("<input/>").attr({ type: "button", class: "btn-device", id: device, value: device }).appendTo("#deviceList");

    }

    function removeDevice(device, index) {
    	device = device.slice(3, device.length)
        // console.log("Removing ", device)
        $("#" + device).remove();

    }

    function updateCurrentDevice(newID) {

    }

    // TODO: ADD ERROR RENDERING FUNCTIONALITY TO UI



    document.addEventListener('DOMContentLoaded', startLoadingPage);
    checkConnection();





})(window);