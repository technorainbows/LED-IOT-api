(function(global) {

    var apiUrl = 'https://api.ashleynewton.net/devices'
        // var apiUrl = 'http://localhost:5000/devices' // toggle for local development
    var deviceID = ''; // current device
    var devices = []; // devices online
    var lastDevice = '';
    var nameMaxLength = 15;

    /* Send a request to server to check if connected/in sync. 
     * If connected, updated/enable main content, otherwise disable main content.
     */
    function checkConnection() {

        // Get list of devices online/available
        $apiUtils.getData(apiUrl + "/hb", "", updateDeviceList,
            disableMainContent);

        setTimeout(checkConnection, 5000);
    }


    function updateMainContent(device) {
        updateOnButton(device);
        updateBrightSlider(device);
        $('#main-content').toggleClass('look-disabled', false);
        console.info("Page updated from server, ready for user input.");
    }

    /*
     * Call this function when the server is no longer connected. This will hide all content in "#main-content".
     */
    function disableMainContent() {

        console.info("disabling main content");
        $('#main-content').toggleClass('look-disabled', true);

    }


    /*
     * Initiates connection with API and also listens for events 	
     */
    function startLoadingPage() {

        /*  force main content to always be enabled for debugging purposes */
        // updateMainContent(device);

        console.info("Initializing client.");
        checkConnection();


        /* Update device status when onSwitch button is clicked. */
        $("#onSwitch").change(function() {

            var switchState = $("#onSwitch").prop('checked');

            switch (switchState) {
                case true:
                    console.debug("PUT request: onState - ON");
                    $apiUtils.putRequest(apiUrl, deviceID,
                        'onState', true);
                    break;
                case false:
                    console.debug("PUT request: onState - OFF");
                    $apiUtils.putRequest(apiUrl, deviceID,
                        'onState', false);
                    break;
            }

        });

        /* when brightness slider is moved, new value is sent to server  */
        $('input[name=slider-brightness]').change('mousestop', function() {
            var value = Number(this.value);
            console.debug("PUT request brightness value: ", value);
            $apiUtils.putRequest(apiUrl, deviceID, 'brightness',
                value);
        });

        /* display changed slider value to user */
        $(document).on('input change', '#slider-brightness', function() {
            var sValue = $(this).val();
            console.debug("slider-brightness value changed: " +
                sValue);
            $('#brightness-value').html(sValue);

        });



        /* when a device button is clicked, set current deviceID to button ID, 
                        and retrieve device settings from server. */
        $(document).on('click', '.btn-device', function selectDevice(event) {

            console.info("device selected: ", this.id);
            lastDevice = deviceID; // save current deviceID before updating it with new btn-device ID
            deviceID = this.id;

            /* update currentDeviceLabel shown to user */
            $('#currentDeviceLabel').html(this.value);
            document.getElementById('currentDeviceLabel').value =
                this.value;
            console.info("deviceID set to: ", deviceID);
            $('#currentDeviceLabel').show();


            /* If selected device is 'new', get device settings from server and update page */
            if (lastDevice != deviceID) {
                console.debug("lastDevice != deviceID ---> " +
                    lastDevice + " != " + deviceID);

                $apiUtils.getData(apiUrl, deviceID,
                    updateMainContent, disableMainContent);
                $('#brightness').toggleClass('look-disabled', false);

                if (lastDevice && document.getElementById(
                        lastDevice).classList.contains(
                        'btn-current')) {
                    document.getElementById(lastDevice).classList.remove(
                        'btn-current');
                }
            }

            console.debug("setting device button to current");
            document.getElementById(deviceID).classList.add(
                'btn-current');
        });


        /* Change name of device when form is submitted */
        $('form').on('submit', function changeDeviceName(event) {

            /* Prevent the page from reloading after form submit */
            event.preventDefault();

            /* Set the text-output span to the value of the first input */
            var $input = $(this).find('input');
            var input = $input.val();

            /* update device name on server */
            $apiUtils.putRequest(apiUrl, deviceID, 'name', input);

            /*  update displayed name for device button */
            $('#currentDeviceLabel').html(input.slice(0,
                nameMaxLength));
            document.getElementById(deviceID).value = input.slice(0,
                nameMaxLength);

        });

    }

    function updateOnButton(device) {
        console.debug("updateOnButton: state received: ", device[1][
            'onState'
        ]);
        switch (device[1]['onState']) {
            case "true":
                $("#onSwitch").prop("checked", true);
                break;
            case "false":
                $("#onSwitch").prop("checked", false);
                break;
        }
    }


    function updateBrightSlider(device) {
        var brightVal = device[1]['brightness']
        $('#brightness-value').html(brightVal);
        $('#slider-brightness').val(brightVal);
    }

    function updateDeviceList(newDevices) {
        var remove = [];
        var add = [];

        newDevices.sort();

        /* Identify old devices no longer online and remove */
        for (let device of devices) {
            if (newDevices.indexOf(device) === -1) remove.push(device);
        }
        remove.forEach(removeDevice);

        /* Hide parameter UI and current device label if not online (e.g., no heartbeat) */
        if (newDevices.includes(("hb_" + deviceID)) == false) {
            $("#currentDeviceLabel").hide();
            $("#parameter-UI").toggleClass('look-disabled', true);
            console.debug("hiding currentDeviceLabel");
        } else {
            console.debug(
                "getting/showing currentDeviceLabel and parameters");

            /* if current device is in heartbeat list, get device info */
            $apiUtils.getData(apiUrl, deviceID, updateMainContent,
                disableMainContent);

            $("#currentDeviceLabel").show();
            $("#parameter-UI").toggleClass('look-disabled', false);
        }

        /* Identify new devices received in order to add */
        const deviceSet = new Set(devices);
        for (let device of newDevices) {
            if (!deviceSet.has(device))
                add.push(device);
            // if (devices.indexOf(device) === -1) add.push(device);
        }
        add.forEach(insertDevice);

        /* update device list */
        devices = newDevices;

        $('#main-content').toggleClass('look-disabled', false);
    }

    async function insertDevice(device, index) {
        device = device.slice(3, device.length)
        console.debug("device to insert: ", device);

        /* Try to retrieve device name from server. 
         * If unable to, log error and set device name to shortened deviceID */
        let deviceName;
        try {
            console.debug("getting device name to insert");
            deviceName = await $apiUtils.getParam(apiUrl, device,
                "name");
        } catch (error) {
            console.error("Error caught: ", error);
            deviceName = device.slice(7, 15); // if device doesn't have a name already, create shortened name from ID
        }
        console.debug("deviceName = ", deviceName);
        $("<input/>").attr({
            type: "button",
            class: "btn-device",
            id: device,
            value: deviceName.slice(0, nameMaxLength)
        }).appendTo(
            "#deviceList");

    }

    function removeDevice(device, index) {
        device = device.slice(3, device.length);
        console.debug("Removing ", device);
        $("#" + device).remove();

    }


    // TODO: ADD ERROR RENDERING FUNCTIONALITY TO UI

    document.addEventListener('DOMContentLoaded', startLoadingPage);
    checkConnection();

})(window);