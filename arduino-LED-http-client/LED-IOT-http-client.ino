/*
  LED-IOT-APP v0.3
  Simple sketch that uses ESP board to connect to local wifi network then gets LED state from python API (ledAPI.py)

*/
#include "Arduino_DebugUtils.h"
//#include "SerialDebug.h" //https://github.com/JoaoLopesF/SerialDebug
#include <FastLED.h>
#include "credentials.h" // wifi network credentials stored in separate file
#include "sha1.h"
// if using ESP32
#include <WiFiMulti.h>
#include <WiFi.h>
#include <ArduinoJson.h>
#include <HTTPClient.h>
#include <ArduinoOTA.h>
WiFiMulti wifiMulti;


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


//*********** SerialDebug Library Stuff *********************//

// Disable all debug ? Good to release builds (production)
// as nothing of SerialDebug is compiled, zero overhead :-)
// For it just uncomment the DEBUG_DISABLED
//#define DEBUG_DISABLED true

// Define the initial debug level here (uncomment to do it)
// #define DEBUG_INITIAL_LEVEL DEBUG_LEVEL_INFO

// Disable SerialDebug debugger ? No more commands and features as functions and globals
// Uncomment this to disable it
//#define DEBUG_DISABLE_DEBUGGER true

// Disable auto function name (good if your debug yet contains it)
//#define DEBUG_AUTO_FUNC_DISABLED true

// Force debug messages to can use flash ) ?
// Disable native Serial.printf (if have)
// Good for low memory, due use flash, but more slow and not use macros
//#define DEBUG_USE_FLASH_F true

//uint32_t mTimeSeconds = 0;
//boolean mLedON = false; // Buildin Led ON ?

// Debug levels

//    printlnV(F("This is a message of debug level VERBOSE"));
//    printlnD(F("This is a message of debug level DEBUG"));
//    printlnI(F("This is a message of debug level INFO"));
//    printlnW(F("This is a message of debug level WARNING"));
//    printlnE(F("This is a message of debug level ERROR"));

//***********************************************************//


// on CXE network
String IPaddress = "192.168.2.54";
String apiURL = "http://" + IPaddress + ":5000/Devices/";
String controllerURL = IPaddress + "site/index.html";

// on vannet
//String apiURL = "http://10.0.0.59:5000/Devices/";
//String controllerURL = "10.0.0.59/site/index.html";
String DEVICE_ID;

//RMT is an ESP hardware feature that offloads stuff like PWM and led strip protocol, it's rad
//#define FASTLED_RMT_CORE_DRIVER true
#define FASTLED_RMT_MAX_CHANNELS 1
FASTLED_USING_NAMESPACE

//#define LED_TYPE    WS2812B
#define LED_TYPE    WS2811


//#ifdef DEV_LIGHTCONTROL_TRIANGLE
#define DATA_PIN   33
char* hostname = "Trianglez";
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

// Set up wireless updating if using ESP32
void setupAOTA() {

  ArduinoOTA.setHostname(hostname);

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


/* setDeviceID: Generates a unique device ID based on performing SHA1 hashing of device's MAC address.
                Returns this ID as a string variable.
*/
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

  // Debug

  // Attention:
  // SerialDebug starts disabled and it only is enabled if have data avaliable in Serial
  // Good to reduce overheads.
  // if You want debug, just press any key and enter in monitor serial

  // Note: all debug in setup must be debugA (always), due it is disabled now.

  //    printlnA(F("**** Setup: initializing ..."));

  // Buildin led
  //
  //    pinMode(LED_BUILTIN, OUTPUT);
  //    digitalWrite(LED_BUILTIN, LOW);



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


/*
   monitorWiFi
*/
void monitorWiFi()
{
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


/*
    heartbeat: sends a POST request with device's unique ID to API
*/

void heartbeat() {
  monitorWiFi();
  //  EVERY_N_MILLISECONDS(500) {
  if (wifiMulti.run() == WL_CONNECTED) { //Check WiFi connection status

    for (int i = 0; i < NUM_SECONDS_TO_WAIT && WiFi.status() != WL_CONNECTED; i++) {
      Serial.print(".");
      delay(1000);
    }

    Debug.print(DBG_VERBOSE, "setting heartbeat");
    HTTPClient http;
    String HB_URL = apiURL + "HB/" + DEVICE_ID;
    http.begin(HB_URL);
    //  http.begin(apiURL + "HB/" + DEVICE_ID); //Specify destination for HTTP request
    http.addHeader("Content-Type", "application/json");             //Specify content-type header
    //    delay(200);
    Debug.print(DBG_VERBOSE, "about to POST");
    //    char* httpResponse = http.POST(DEVICE_ID);
    int httpResponseCode = http.POST("{}");   //Send the actual POST request
    Debug.print(DBG_VERBOSE, "POSTing complete");

    if (httpResponseCode > 0) {

      String response = http.getString();                       //Get the response to the request
      //      Serial.println("POST RESPONSE CODE:");
      Debug.print(DBG_VERBOSE, "%i", httpResponseCode);   //Print return code
      //      Serial.print("POST RESPONSE: ");
       Debug.print(DBG_VERBOSE, "%s", response);           //Print request answer

    } else {

      Debug.print(DBG_ERROR, "Error on sending POST: ");
      Serial.println(httpResponseCode);

    }

    http.end();  //Free resources

  } else {

    Debug.print(DBG_ERROR, "Error in WiFi connection");

  }


}


void loop() {
  //  debugHandle();

  //   check wifi status
  for (int i = 0; i < 5 && WiFi.status() != WL_CONNECTED; i++) {
    Serial.print(".");
    delay(1000);
  }

  EVERY_N_MILLISECONDS(200) {
    if (wifiMulti.run() != WL_CONNECTED) {
      Debug.print(DBG_ERROR, "WiFi not connected!");
      // turn first 5 leds to red if not connected
      fill_solid(leds, 20, CRGB::Red);
      FastLED.show();
      //    delay(200);
    }
  }



  EVERY_N_MILLISECONDS(500) {


    monitorWiFi();
    ArduinoOTA.handle();
    //    if (wifiMulti.run() == WL_CONNECTED) { //Check WiFi connection status
    //
    //      //      }
    //      //    for(int i = 0; i < NUM_SECONDS_TO_WAIT && WiFi.status() != WL_CONNECTED; i++) {
    //      //      Serial.print(".");
    //      //      delay(1000);
    //      //  }
    //
    ////      Serial.println("setting heartbeat");
    //      HTTPClient http;
    //      String HB_URL = IPaddress + ":5000/Devices/HB/" + DEVICE_ID;
    //      Serial.println(HB_URL);
    //      http.begin(HB_URL);
    //      //  http.begin(apiURL + "HB/" + DEVICE_ID); //Specify destination for HTTP request
    //      http.addHeader("Content-Type", "application/json");             //Specify content-type header
    //      //    delay(200);
    //      Serial.println("about to POST");
    //      //    char* httpResponse = http.POST(DEVICE_ID);
    //      int httpResponseCode = http.POST("{}");   //Send the actual POST request
    //      Serial.println("POSTing complete");
    //
    //      if (httpResponseCode > 0) {
    //
    //        String response = http.getString();                       //Get the response to the request
    //        Serial.print("POST RESPONSE CODE:");
    //        Serial.println(httpResponseCode);   //Print return code
    //        //        Serial.print("POST RESPONSE: ");
    //        //        Serial.println(response);           //Print request answer
    //
    //      } else {
    //
    //        Serial.print("Error on sending POST: ");
    //        Serial.println(httpResponseCode);
    //
    //      }
    //
    //      http.end();  //Free resources
    //
    //    } else {
    //
    //      Serial.println("Error in WiFi connection");
    //
    //    }

    // wait for WiFi connection
    if ((wifiMulti.run() == WL_CONNECTED)) {
      heartbeat();
      //      Serial.println("wifi connected, connecting to api");

      HTTPClient http;

      // start connection and send HTTP header
      //      Serial.print("beginning HTTP connection to: ");
      //      Serial.println(apiURL + DEVICE_ID);
      http.begin(apiURL + DEVICE_ID);





      //      Serial.print("[HTTP] GET...\n");
      int httpCode = http.GET();

      // Check returning httpCode -- will be negative on error
      if (httpCode > 0) {
        //          Serial.printf("[HTTP] GET... code: %d\n", httpCode);

        // file found at server
        if (httpCode == HTTP_CODE_OK) {
          //          Serial.print("Found file at server: ");
          String payload = http.getString();
          //          Serial.println(payload);

          // parse payload

          const size_t capacity = JSON_ARRAY_SIZE(3) + JSON_OBJECT_SIZE(3) + 60;
          DynamicJsonDocument doc(capacity);
          //          const char* json = "[\"deviceID\",{\"brightness\":\"255\",\"name\":\"Default\",\"onState\":\"true\"},200]";

          //        const char* json = "[{\"brightness\":17,\"name\":\"Ashley-Triangle\",\"onState\":true},200]";

          deserializeJson(doc, payload);
          const char* root_0 = doc[0]; // "deviceID"

          JsonObject root_1 = doc[1];
          const char* root_1_brightness = root_1["brightness"]; // "255"
          const char* root_1_name = root_1["name"]; // "Default"
          const char* root_1_onState = root_1["onState"]; // "true"
          int root_2 = doc[2]; // 200

          int newBright = atoi(root_1_brightness);

          onState = root_1_onState;
          //          Serial.printf("brightVal = %d\n", brightVal);
          if (onState != lastState) {
            lastState = onState;
            //            Serial.println("onState = " + onState);

          }

          if (brightVal != newBright) {
            brightVal = newBright;
            //            Serial.printf("brightVal = %d\n", brightVal);

            FastLED.setBrightness(brightVal);
            FastLED.show();
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

/*
   updateLEDS: toggles LEDs on/off depending on onState; if LEDs are on then fills with rainbow fade
*/

void updateLEDS() {

  if (onState == "false") fill_solid(leds, NUM_LEDS, CRGB::Black);

  else {
    fill_rainbow( leds, NUM_LEDS, gHue, speed);
    EVERY_N_MILLISECONDS( 10 ) {
      gHue++;  // slowly cycle the "base color" through the rainbow
    }
  }
  //  Serial.println("FastLED.show");
  FastLED.show();


}

/*
    updateDisplay: updates the little OLED status screen of device
*/

void updateDisplay() {

  display.clear();
  display.setFont(ArialMT_Plain_24); //11,16,24
  display.setTextAlignment(TEXT_ALIGN_LEFT);
  display.drawString(0, 0, hostname);
  //display.display(); //draw the screen

  display.setFont(ArialMT_Plain_16);
  display.drawString(0, 22, WiFi.localIP().toString());
  //  display.display(); //draw the screen

  display.setFont(ArialMT_Plain_10);
  display.drawString(0, 36, WiFi.SSID().c_str());
  display.drawString(0, 46, String(FastLED.getFPS()) + "FPS");

  display.display(); //draw the screen


}
