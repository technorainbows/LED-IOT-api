(function(global) {

    var dc = {}; // namespace for document content

    var apiUrl = 'http://lvh.me:5000/Devices'
    // var apiUrl = 'http://10.0.0.59:5000/Devices' // ip address at home
    // var apiUrl = 'http://192.168.2.54:5000/Devices' // ip address when at CDA

    // var apiURL = 'https://jsonplaceholder.typicode.com/posts' // test external json server
    // console.log('ledAPI running');
    var deviceID = '' // current device
    var devices = [] // devices online
    var lastDevice = ''

    var nameMaxLength = 15;

    /************
     * DEVICE INFO
     ************/
    var brightness;
    var ledState;
    var deviceNames = []
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
       
    	$('#main-content').toggleClass('look-disabled', true);
    	
    }


    /*
     * Initiates connection with API and also listens for events 	
     */
    function startLoadingPage() {

    	// ****  force main content to always be enabled for debugging purposes
    	// updateMainContent(device);


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
                	console.log("PUT request: onState ON");
                    $apiUtils.putRequest(apiUrl, deviceID, 'onState', true);
                    break;
                case "ledOFF":
                	console.log("PUT request: onState OFF");
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
            deviceID = this.id;
            // deviceID = (this.id).slice(3, this.id.length);
            $('#currentDeviceLabel').html(this.value);
            // $('#currentDeviceValue').html(this.value);

            console.log("deviceID set to: ", deviceID);
            $('#currentDeviceLabel').show();
            if (lastDevice == deviceID) {
            	$('#brightness').toggleClass('look-disabled', false);
	            // $("#slider-brightness").prop('disabled',false);
            } else {
            	$apiUtils.getData(apiUrl, deviceID, updateMainContent, disableMainContent);
                // $("#slider-brightness").prop('disabled',false);
                $('#brightness').toggleClass('look-disabled', false);
   
            	// $("#parameter-UI").show();
            }
        });

        // $("#device-name").submit(function(event){
        // 	console.log("device name submitted: ", $("input-name"));
        // 	// $apiUtils.putRequest(apiUrl,deviceID,'name',this.value);
        // });


        /* Change name of device */
 		$('form').on('submit', function changeDeviceName(event) {
            
            // Prevent the page from reloading
            event.preventDefault();
            
            // Set the text-output span to the value of the first input
            var $input = $(this).find('input');
            var input = $input.val();
            // console.log("device name submitted: ", input, " length: ", input.length);
            // input=input.trim();
            // console.log("device trimmed: ", input, "length = ", input.length);
            // $('#text-output').text("You typed: " + input);
        	// update device name with api
        	$apiUtils.putRequest(apiUrl,deviceID,'name',input);
        	// update displayed name for device button
        	$('#currentDeviceLabel').html(input.slice(0,nameMaxLength));
        	// $(deviceID).value=input;
        	// $('#deviceList').find(deviceID).value=input;
        	// $(deviceID).html(input);
        	document.getElementById(deviceID).value = input.slice(0,nameMaxLength);
        	// $(#inputName).attr("placeholder", "New device name.");
        	$('form').trigger("reset");
        });


        // $(document).on('click', '.save-name', function(event){
        // 	$("device-name").submit();
        // 	console.log("device name saved");
        // 	// update device name with api
        // 		$apiUtils.putRequest(apiUrl,deviceID,'name',this.value);
        // 	// update displayed name for device button
        // 	$('#currentDeviceLabel').html(this.value);
        // 	console.log("updated device name with: ", this.value);

        // });


    }



   

    function updateOnButton(device) {
        // console.log("light.ledState = " + lightProps.ledState);
        console.log("updateOnButton state received: ", device[1]['onState']);
        switch (device[1]['onState']) {
            case "true":
                console.log("light on");
                $('#ledON').closest('label').toggleClass('active', true);
                $('#ledOFF').closest('label').toggleClass('active', false);
                break;
            case "false":
                console.log("light off");
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

    function updateDeviceNames(){

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
            $("#parameter-UI").toggleClass('look-disabled',true);
            // $(".slider-brightness").prop('disabled',true);
        	// $('#brightness').toggleClass('look-disabled', true);
        	// $('#brightness').removeClass('look-enabled');   
            // console.log("hiding currentDeviceLabel");
        }
        else {
        	// console.log("getting/showing currentDeviceLabel and parameters");
        	
        	// if current device is in heartbeat list, get device info
			$apiUtils.getData(apiUrl, deviceID, updateMainContent, disableMainContent);

        	$("#currentDeviceLabel").show();
            $("#parameter-UI").toggleClass('look-disabled',false);
        	// $('#brightness').toggleClass('look-disabled', false);
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

    async function insertDevice(device, index) {
    	device = device.slice(3, device.length)
    	console.log("device to insert: ", device);
    	var deviceShort = device.slice(7, 15);
    	try {
    		console.log("getting device name to insert");
	    	var deviceName = await $apiUtils.getParam(apiUrl, device, "name");
	    } catch (error){
	    	console.error("Error caught!")
            console.error(error);
            var deviceName = deviceShort;
	    }
    	console.log("deviceName = ", deviceName);
        $("<input/>").attr({ type: "button", class: "btn-device", id: device, value: deviceName.slice(0,nameMaxLength) }).appendTo("#deviceList");

    }

    function removeDevice(device, index) {
    	// device = device.slice(3, 15);
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