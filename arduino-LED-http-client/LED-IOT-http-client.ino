/************************************************************************************************************************
   LED-IOT-APP v1.0
   Communicates with a rest api server to get LED control parameters in order to control attached LEDs.
   Also updates its state (e.g., "heartbeat") to rest API.
 ********************************************************************************************************************/

#include "Arduino_DebugUtils.h"
#include <FastLED.h>
#include "credentials.h" // wifi network credentials and authorization token stored in separate file
#include "sha1.h"

// if using ESP32
#include <WiFiMulti.h>
#include <WiFi.h>
#include <ArduinoJson.h>
#include <HTTPClient.h>
#include <ArduinoOTA.h>
WiFiMulti wifiMulti;
//#include <WiFiClientSecure.h>

// if using OLED display
#include "SSD1306Wire.h" // legacy include: `#include "SSD1306.h"` //OLED screen
SSD1306Wire  display(0x3c, 5, 4); //wifi bluetooth battery oled 18650 board dispplay

#include <SimpleHOTP.h>

// if using ESP8266....
//#include <ESP8266WiFi.h>
//#include <ESP8266WiFiMulti.h>
//#include <ESP8266HTTPClient.h>
//ESP8266WiFiMulti wifiMulti;
//#include <ArduinoHttpClient.h>



// This is GandiStandardSSLCA2.pem, the root Certificate Authority that signed
// the server certifcate for the demo server https://jigsaw.w3.org in this
// example. This certificate is valid until Sep 11 23:59:59 2024 GMT
const char* rootCACertificate = \
                                "-----BEGIN CERTIFICATE-----\n" \
                                "MIIF6TCCA9GgAwIBAgIQBeTcO5Q4qzuFl8umoZhQ4zANBgkqhkiG9w0BAQwFADCB\n" \
                                "iDELMAkGA1UEBhMCVVMxEzARBgNVBAgTCk5ldyBKZXJzZXkxFDASBgNVBAcTC0pl\n" \
                                "cnNleSBDaXR5MR4wHAYDVQQKExVUaGUgVVNFUlRSVVNUIE5ldHdvcmsxLjAsBgNV\n" \
                                "BAMTJVVTRVJUcnVzdCBSU0EgQ2VydGlmaWNhdGlvbiBBdXRob3JpdHkwHhcNMTQw\n" \
                                "OTEyMDAwMDAwWhcNMjQwOTExMjM1OTU5WjBfMQswCQYDVQQGEwJGUjEOMAwGA1UE\n" \
                                "CBMFUGFyaXMxDjAMBgNVBAcTBVBhcmlzMQ4wDAYDVQQKEwVHYW5kaTEgMB4GA1UE\n" \
                                "AxMXR2FuZGkgU3RhbmRhcmQgU1NMIENBIDIwggEiMA0GCSqGSIb3DQEBAQUAA4IB\n" \
                                "DwAwggEKAoIBAQCUBC2meZV0/9UAPPWu2JSxKXzAjwsLibmCg5duNyj1ohrP0pIL\n" \
                                "m6jTh5RzhBCf3DXLwi2SrCG5yzv8QMHBgyHwv/j2nPqcghDA0I5O5Q1MsJFckLSk\n" \
                                "QFEW2uSEEi0FXKEfFxkkUap66uEHG4aNAXLy59SDIzme4OFMH2sio7QQZrDtgpbX\n" \
                                "bmq08j+1QvzdirWrui0dOnWbMdw+naxb00ENbLAb9Tr1eeohovj0M1JLJC0epJmx\n" \
                                "bUi8uBL+cnB89/sCdfSN3tbawKAyGlLfOGsuRTg/PwSWAP2h9KK71RfWJ3wbWFmV\n" \
                                "XooS/ZyrgT5SKEhRhWvzkbKGPym1bgNi7tYFAgMBAAGjggF1MIIBcTAfBgNVHSME\n" \
                                "GDAWgBRTeb9aqitKz1SA4dibwJ3ysgNmyzAdBgNVHQ4EFgQUs5Cn2MmvTs1hPJ98\n" \
                                "rV1/Qf1pMOowDgYDVR0PAQH/BAQDAgGGMBIGA1UdEwEB/wQIMAYBAf8CAQAwHQYD\n" \
                                "VR0lBBYwFAYIKwYBBQUHAwEGCCsGAQUFBwMCMCIGA1UdIAQbMBkwDQYLKwYBBAGy\n" \
                                "MQECAhowCAYGZ4EMAQIBMFAGA1UdHwRJMEcwRaBDoEGGP2h0dHA6Ly9jcmwudXNl\n" \
                                "cnRydXN0LmNvbS9VU0VSVHJ1c3RSU0FDZXJ0aWZpY2F0aW9uQXV0aG9yaXR5LmNy\n" \
                                "bDB2BggrBgEFBQcBAQRqMGgwPwYIKwYBBQUHMAKGM2h0dHA6Ly9jcnQudXNlcnRy\n" \
                                "dXN0LmNvbS9VU0VSVHJ1c3RSU0FBZGRUcnVzdENBLmNydDAlBggrBgEFBQcwAYYZ\n" \
                                "aHR0cDovL29jc3AudXNlcnRydXN0LmNvbTANBgkqhkiG9w0BAQwFAAOCAgEAWGf9\n" \
                                "crJq13xhlhl+2UNG0SZ9yFP6ZrBrLafTqlb3OojQO3LJUP33WbKqaPWMcwO7lWUX\n" \
                                "zi8c3ZgTopHJ7qFAbjyY1lzzsiI8Le4bpOHeICQW8owRc5E69vrOJAKHypPstLbI\n" \
                                "FhfFcvwnQPYT/pOmnVHvPCvYd1ebjGU6NSU2t7WKY28HJ5OxYI2A25bUeo8tqxyI\n" \
                                "yW5+1mUfr13KFj8oRtygNeX56eXVlogMT8a3d2dIhCe2H7Bo26y/d7CQuKLJHDJd\n" \
                                "ArolQ4FCR7vY4Y8MDEZf7kYzawMUgtN+zY+vkNaOJH1AQrRqahfGlZfh8jjNp+20\n" \
                                "J0CT33KpuMZmYzc4ZCIwojvxuch7yPspOqsactIGEk72gtQjbz7Dk+XYtsDe3CMW\n" \
                                "1hMwt6CaDixVBgBwAc/qOR2A24j3pSC4W/0xJmmPLQphgzpHphNULB7j7UTKvGof\n" \
                                "KA5R2d4On3XNDgOVyvnFqSot/kGkoUeuDcL5OWYzSlvhhChZbH2UF3bkRYKtcCD9\n" \
                                "0m9jqNf6oDP6N8v3smWe2lBvP+Sn845dWDKXcCMu5/3EFZucJ48y7RetWIExKREa\n" \
                                "m9T8bJUox04FB6b9HbwZ4ui3uRGKLXASUoWNjDNKD/yZkuBjcNqllEdjB+dYxzFf\n" \
                                "BT02Vf6Dsuimrdfp5gJ0iHRc2jTbkNJtUQoj1iM=\n" \
                                "-----END CERTIFICATE-----\n";


#define NETWORK_VANNEST

#ifdef NETWORK_CXE
// on CXE network
String IPaddress = "192.168.2.54";

#endif

#ifdef NETWORK_VANNEST
// on vannet
String IPaddress = "10.0.0.59";
//String apiURL = "http://10.0.0.59:5000/Devices/";
//String controllerURL = "10.0.0.59/site/index.html";
#endif

String apiURL = "http://" + IPaddress + ":5000/Devices/";
String controllerURL = IPaddress + "site/index.html";

String DEVICE_ID;

//RMT is an ESP hardware feature that offloads stuff like PWM and led strip protocol, it's rad
//#define FASTLED_RMT_CORE_DRIVER true
#define FASTLED_RMT_MAX_CHANNELS 1
FASTLED_USING_NAMESPACE

//#define LED_TYPE    WS2812B
#define LED_TYPE    WS2811


//#ifdef DEV_LIGHTCONTROL_TRIANGLE
#define DATA_PIN   33
String hostname = "Trianglez";
#define COLOR_ORDER GRB //pixels
#define COLOR_CORRECT TypicalLEDStrip
#define NUM_LEDS 200
#define MILLI_AMPS         1000
#define BRIGHTNESS          100
#define FRAMES_PER_SECOND  120
//#define DEVICE_ID "device1"

//#endif


CRGB leds[NUM_LEDS];

uint8_t speed = 10;

uint8_t gHue = 0; // rotating "base color" used by many of the patterns

boolean connectioWasAlive = true;
String lastState = "false";
String onState = "false";
int brightVal = BRIGHTNESS;

#define NUM_SECONDS_TO_WAIT 5

/****************************************************************************************
   setupAOTA: Set up wireless updating if using ESP32
 ***************************************************************************************/

void setupAOTA() {

  ArduinoOTA.setHostname(hostname.c_str());

  ArduinoOTA
  .onStart([]() {
    String type;
    if (ArduinoOTA.getCommand() == U_FLASH)
      type = "sketch";
    else // U_SPIFFS
      type = "filesystem";

    // NOTE: if updating SPIFFS this would be the place to unmount SPIFFS using SPIFFS.end()
    Serial.println("Start updating " + type);
  })
  .onEnd([]() {
    Serial.println("\nEnd");
  })
  .onProgress([](unsigned int progress, unsigned int total) {
    Serial.printf("Progress: %u%%\r", (progress / (total / 100)));
  })
  .onError([](ota_error_t error) {
    Serial.printf("Error[%u]: ", error);
    if (error == OTA_AUTH_ERROR) Serial.println("Auth Failed");
    else if (error == OTA_BEGIN_ERROR) Serial.println("Begin Failed");
    else if (error == OTA_CONNECT_ERROR) Serial.println("Connect Failed");
    else if (error == OTA_RECEIVE_ERROR) Serial.println("Receive Failed");
    else if (error == OTA_END_ERROR) Serial.println("End Failed");
  });

  ArduinoOTA.begin();
}


/* ****************************************************************************************
    setDeviceID: Generates a unique device ID based on performing SHA1 hashing of device's
                 MAC address.Returns this ID as a string variable.
 *****************************************************************************************/
String setDeviceID() {
  byte mac[6] = {};

  //      String test = "test";
  //      int ml = test.length();
  WiFi.macAddress(mac);
  Serial.print("MAC ADDRESS: ");
  for (int i = 0; i < 5; i++) {
    Serial.print(mac[i], HEX);
    Serial.print(":");
  }
  Serial.println();
  int ml = sizeof(mac);
  char macArray[ml + 1];
  //  test.getBytes(macArray, ml + 1);
  //  mac.toCharArray(macArray, 6);


  uint32_t hash[5] = {}; // This will contain the 160-bit Hash
  SimpleSHA1::generateSHA(mac, (ml * 8), hash);
  //    Serial.println(hash);
  char hashChar[sizeof(hash) * 8 + 1];
  String device_hash = "device_";

  for (int i = 0; i < 5; i++) {
    //        Serial.print(hash[i], HEX);

    sprintf(hashChar, "%X", hash[i]);
    device_hash += String(hashChar);
  }

  Serial.print("device_hash = ");
  Serial.println(device_hash);


  //      utoa((unsigned int)hash, hashChar, HEX);
  //      Serial.println();
  //      Serial.println(hashChar2);
  //      Serial.print("hashChar = ");
  //      Serial.println(hashChar);
  //      String testDev = String(hashChar);
  //      Serial.print("testDev = ");
  //      Serial.println(testDev);
  //      DEVICE_ID = "device_" + hashString;
  //      Serial.print("DEVICE_ID = ");
  //      Serial.println(DEVICE_ID);
  return device_hash;
}

/***************************************************************************************
  setup
***************************************************************************************/

void setup() {
  Serial.begin(115200);
  Debug.timestampOn();
  Debug.setDebugLevel(DBG_DEBUG);

#ifdef __AVR_ATmega32U4__ // Arduino AVR Leonardo

  while (!Serial) {
    ; // wait for serial port to connect. Needed for Leonardo only
  }

#else

  delay(500); // Wait a time

#endif


  //all this is for OLED status screen
  display.init();
  display.clear();
  display.drawString(0, 0, "probably booting");
  //display.flipScreenVertically();
  display.display();

  // set up LEDS
  FastLED.setDither(BINARY_DITHER);
  FastLED.setMaxPowerInVoltsAndMilliamps(5, MILLI_AMPS);
  FastLED.setBrightness(BRIGHTNESS);
  FastLED.addLeds<LED_TYPE, DATA_PIN, COLOR_ORDER>(leds, NUM_LEDS).setCorrection(COLOR_CORRECT);


  // setup WIFI
  WiFi.mode(WIFI_STA);
  wifiMulti.addAP(ssid1, password1);
  wifiMulti.addAP(ssid2, password2);
  //  wifiMulti.addAP("ssid_from_AP_2", "your_password_for_AP_2");
  //  wifiMulti.addAP("ssid_from_AP_3", "your_password_for_AP_3");

  Serial.println("Connecting Wifi...")  ;
  if (wifiMulti.run() == WL_CONNECTED) {
    Serial.println("");
    //    Serial.println("WiFi connected");
    Serial.printf("WiFi connected to %s\n", WiFi.SSID().c_str());
    //    Serial.println(WiFi.localIP());
    Serial.print("IP address: ");
    Serial.println(WiFi.localIP());

    // turn leds to green if connected
    fill_solid(leds, NUM_LEDS, CRGB::Green);
    FastLED.show();
    delay(100);
    fill_solid(leds, NUM_LEDS, CRGB::Black);
    FastLED.show();



    // inititalize deviceID
    DEVICE_ID = setDeviceID();

  }

  setupAOTA(); // set up arduino over-the-air updating

  updateDisplay(); // update OLED screen on device

  //    printlnA(F("*** Setup end"));

}


/****************************************************************************************
    monitorWiFi
****************************************************************************************/
void monitorWiFi()
{
  Debug.print(DBG_INFO, "Monitoring wifi...");

  if (wifiMulti.run() != WL_CONNECTED)
  {
    if (connectioWasAlive == true)
    {
      connectioWasAlive = false;
      Serial.print("Looking for WiFi ");
      // turn first 20 leds to red if not connected
      fill_solid(leds, 20, CRGB::Red);
      FastLED.show();
    }
    Serial.print(".");
    delay(100);
  }
  else if (connectioWasAlive == false)
  {
    connectioWasAlive = true;
    //    delay(500);
    Serial.printf(" connected to %s\n", WiFi.SSID().c_str());
    Serial.println(WiFi.localIP());
    updateDisplay();

  }
}


/***************************************************************************
   heartbeat: sends a POST request with device's unique ID to API
***************************************************************************/

void heartbeat() {
  //  monitorWiFi();
  //  EVERY_N_MILLISECONDS(500) {
  if (wifiMulti.run() == WL_CONNECTED) { //Check WiFi connection status

    Debug.print(DBG_INFO, "setting heartbeat");
    HTTPClient http;
    String HB_URL = apiURL + "HB/" + DEVICE_ID;
    //    String HB_URL = "https://jsonplaceholder.typicode.com/posts?userId=1";

    http.begin(HB_URL);
    //  http.begin(apiURL + "HB/" + DEVICE_ID); //Specify destination for HTTP request
    http.addHeader("Content-Type", "application/json");             //Specify content-type header
    http.addHeader("Authorization", "Bearer " + auth_token);
    //    delay(200);
    Debug.print(DBG_INFO, "about to POST");
    //    char* httpResponse = http.POST(DEVICE_ID);
    int httpResponseCode = http.POST("{}");   //Send the actual POST request
    Debug.print(DBG_INFO, "POSTing complete");

    if (httpResponseCode > 0) {

      String response = http.getString();                       //Get the response to the request
      //      Serial.println("POST RESPONSE CODE:");
      Debug.print(DBG_INFO, "%i", httpResponseCode);   //Print return code
      //      Serial.print("POST RESPONSE: ");
      Debug.print(DBG_INFO, "%s", response);           //Print request answer

    } else {

      Debug.print(DBG_ERROR, "Error on sending POST: ");
      Serial.println(httpResponseCode);

    }

    http.end();  //Free resources

  } else {

    Debug.print(DBG_ERROR, "Error in WiFi connection");
    for (int i = 0; i < NUM_SECONDS_TO_WAIT && WiFi.status() != WL_CONNECTED; i++) {
      Serial.print(".");
      delay(100);
    }
  }


}

/*******************************************************
  Main Loop
*******************************************************/

void loop() {

  monitorWiFi();
  EVERY_N_MILLISECONDS(500) {

    heartbeat();
  }

  EVERY_N_MILLISECONDS(200) {

    ArduinoOTA.handle();


    // wait for WiFi connection
    if ((wifiMulti.run() == WL_CONNECTED)) {


      HTTPClient http;

      // start connection and send HTTP header
      http.begin(apiURL + DEVICE_ID);
      http.addHeader("Authorization", "Bearer " + auth_token);

      int httpCode = http.GET();

      // Check returning httpCode -- will be negative on error
      if (httpCode > 0) {
        Debug.print(DBG_INFO, "[HTTP] GET... code: %d\n", httpCode);

        // file found at server
        if (httpCode == HTTP_CODE_OK) {
          Debug.print(DBG_INFO, "Found file at server: ");
          String payload = http.getString();
          Debug.print(DBG_INFO, payload.c_str());

          // parse payload

          const size_t capacity = JSON_ARRAY_SIZE(2) + JSON_OBJECT_SIZE(3) + 100;
          DynamicJsonDocument doc(capacity);

          //                    const char* json = "[\"device_266A08DBF47456428F703EEDF1E208B7117785DF\",{\"brightness\":\"123\",\"name\":\"triangle\",\"onState\":\"true\"}]";

          deserializeJson(doc, payload);

          const char* root_0 = doc[0]; // "device_266A08DBF47456428F703EEDF1E208B7117785DF"

          JsonObject root_1 = doc[1];
          const char* root_1_brightness = root_1["brightness"]; // "123"
          const char* root_1_name = root_1["name"]; // "triangle"
          const char* root_1_onState = root_1["onState"]; // "true"
          Debug.print(DBG_DEBUG, "root_0 = ");
          Debug.print(DBG_DEBUG, root_0);
          Debug.print(DBG_DEBUG, "brightness = ");
          Debug.print(DBG_DEBUG, root_1_brightness);
          Debug.print(DBG_DEBUG, "name = ");
          Debug.print(DBG_DEBUG, root_1_name);
          onState = root_1_onState;
          Debug.print(DBG_DEBUG, "onState = ");
          Debug.print(DBG_DEBUG, root_1_onState);

          //          strcpy(hostname, root_1_name);


          int root_2 = doc[2]; // 200

          int newBright = atoi(root_1_brightness);

          if (onState != lastState) {
            lastState = onState;
            Debug.print(DBG_INFO, "onState changed!");
            Debug.print(DBG_INFO, onState.c_str());

          }

          if (brightVal != newBright) {
            brightVal = newBright;
            //            Serial.printf("brightVal = %d\n", brightVal);

            FastLED.setBrightness(brightVal);
            FastLED.show();
          }
          if (hostname != root_1_name) {
            hostname = root_1_name;
            updateDisplay();
          }

        }
      } else {
        Debug.print(DBG_ERROR, "[HTTP] GET... failed, error: %s\n", http.errorToString(httpCode).c_str());
      }

      http.end(); // close connection
      //      Serial.println("Closing connection");
    }
  }

  //  Serial.println("Setting brightness");
  //  delay(500);
  FastLED.setBrightness(brightVal);
  FastLED.show();
  updateLEDS();



  // insert a delay to keep the framerate modest
  FastLED.delay(800 / FRAMES_PER_SECOND);

}

/*****************************************************************************************************
  updateLEDS: toggles LEDs on/off depending on onState; if LEDs are on then fills with rainbow fade
*****************************************************************************************************/

void updateLEDS() {

  if (onState == "false") {
    fill_solid(leds, NUM_LEDS, CRGB::Black);
    Debug.print(DBG_VERBOSE, "onstate is false");
    FastLED.show();
  }

  else {
    Debug.print(DBG_VERBOSE, "onState is true");
    fill_rainbow( leds, NUM_LEDS, gHue, speed);
    EVERY_N_MILLISECONDS( 10 ) {
      gHue++;  // slowly cycle the "base color" through the rainbow
      FastLED.show();
    }
  }
  //  Serial.println("FastLED.show");

}

/**************************************************************************************************
  updateDisplay: updates the little OLED status screen of device
**************************************************************************************************/

void updateDisplay() {
  Debug.print(DBG_INFO, "updating display with hostname %s", hostname.c_str());

  display.clear();
  display.setFont(ArialMT_Plain_24); //11,16,24
  display.setTextAlignment(TEXT_ALIGN_LEFT);
  display.drawString(0, 0, hostname.c_str());
  //display.display(); //draw the screen

  display.setFont(ArialMT_Plain_16);
  display.drawString(0, 22, WiFi.localIP().toString());
  //  display.display(); //draw the screen

  display.setFont(ArialMT_Plain_10);
  display.drawString(0, 36, WiFi.SSID().c_str());
  display.drawString(0, 46, String(FastLED.getFPS()) + "FPS");

  display.display(); //draw the screen


}
