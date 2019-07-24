/*
  LED-IOT-APP v0.0.1
  Simple sketch that uses ESP board to connect to local wifi network then gets LED state from python API (ledAPI.py)

  Receives data as JSON formatted as {"ledState": true] or {"ledState": false} and toggles LEDs between off and rainbow.


*/

#include <FastLED.h>
#include <ESP8266WiFi.h>
#include <ESP8266WiFiMulti.h>
#include <ESP8266HTTPClient.h>
#include <ArduinoJson.h>
//#include <ArduinoHttpClient.h>

//#include <HTTPClient.h>

ESP8266WiFiMulti wifiMulti;

String apiURL = "http://10.0.0.59:5000/light";
String controllerURL = "10.0.0.59/site/index.html";

const char * ssid1 = "_VanNest";
const char * password1 = "alleged cat";

//RMT is an ESP hardware feature that offloads stuff like PWM and led strip protocol, it's rad
//#define FASTLED_RMT_CORE_DRIVER true
#define FASTLED_RMT_MAX_CHANNELS 1
FASTLED_USING_NAMESPACE

#define LED_TYPE    WS2812B



//#ifdef DEV_LIGHTCONTROL_TRIANGLE
#define DATA_PIN   6
//char* hostname = "ashliana";
#define COLOR_ORDER GRB //pixels
#define COLOR_CORRECT TypicalLEDStrip
#define NUM_LEDS 200
#define MILLI_AMPS         800
#define BRIGHTNESS          100
#define FRAMES_PER_SECOND  120

//#endif

CRGB leds[NUM_LEDS];

uint8_t gHue = 0; // rotating "base color" used by many of the patterns


void setup() {
  Serial.begin(115200);

  WiFi.mode(WIFI_STA);
  wifiMulti.addAP(ssid1, password1);
  //  wifiMulti.addAP("ssid_from_AP_2", "your_password_for_AP_2");
  //  wifiMulti.addAP("ssid_from_AP_3", "your_password_for_AP_3");

  Serial.println("Connecting Wifi...");
  if (wifiMulti.run() == WL_CONNECTED) {
    Serial.println("");
    Serial.println("WiFi connected");
    Serial.println("IP address: ");
    Serial.println(WiFi.localIP());
  }

  FastLED.setDither(BINARY_DITHER);

  FastLED.setMaxPowerInVoltsAndMilliamps(5, MILLI_AMPS);
  FastLED.setBrightness(BRIGHTNESS);

  FastLED.addLeds<LED_TYPE, DATA_PIN, COLOR_ORDER>(leds, NUM_LEDS).setCorrection(COLOR_CORRECT);


}

bool lastState = false;

void loop() {

  // check wifi status
  if (wifiMulti.run() != WL_CONNECTED) {
    Serial.println("WiFi not connected!");
    delay(1000);
  }

  // wait for WiFi connection
  if ((wifiMulti.run() == WL_CONNECTED)) {

    HTTPClient http;

    // start connection and send HTTP header

    http.begin(apiURL);

    //    Serial.print("[HTTP] GET...\n");
    int httpCode = http.GET();

    // Check returning httpCode -- will be negative on error
    if (httpCode > 0) {
      //            Serial.printf("[HTTP] GET... code: %d\n", httpCode);

      // file found at server
      if (httpCode == HTTP_CODE_OK) {
        String payload = http.getString();
        //        Serial.println(payload);

        // parse payload

        const size_t capacity = JSON_OBJECT_SIZE(1) + 20;
        DynamicJsonBuffer jsonBuffer(capacity);

        //        const char* json = "{\"ledsState\":true}";

        JsonObject& root = jsonBuffer.parseObject(payload);

        bool ledsState = root["ledsState"]; // true

        if (ledsState != lastState) {
          lastState = ledsState;
          updateLEDS(ledsState);
          Serial.printf("ledState = %d\n", ledsState);

        }

      }
    } else {
      Serial.printf("[HTTP] GET... failed, error: %s\n", http.errorToString(httpCode).c_str());
    }

    http.end(); // close connection
  }

  delay(500);
}


void updateLEDS(bool state) {

  if (state) fill_rainbow( leds, NUM_LEDS, gHue);

  else fill_solid(leds, NUM_LEDS, CRGB::Black);

  FastLED.show();

  // insert a delay to keep the framerate modest
  FastLED.delay(1000 / FRAMES_PER_SECOND);


  // do some periodic updates
  //        EVERY_N_MILLISECONDS( 20 ) {
  //        gHue++;  // slowly cycle the "base color" through the rainbow
  //        }
  //  EVERY_N_SECONDS( 10 ) { nextPattern(); } // change patterns periodically

}

//
//bool readReponseContent(struct UserData* userData) {
//  // Compute optimal size of the JSON buffer according to what we need to parse.
//  // See https://bblanchon.github.io/ArduinoJson/assistant/
//  const size_t BUFFER_SIZE =
//    JSON_OBJECT_SIZE(8)    // the root object has 8 elements
//    + JSON_OBJECT_SIZE(5)  // the "address" object has 5 elements
//    + JSON_OBJECT_SIZE(2)  // the "geo" object has 2 elements
//    + JSON_OBJECT_SIZE(3)  // the "company" object has 3 elements
//    + MAX_CONTENT_SIZE;    // additional space for strings
//
//  // Allocate a temporary memory pool
//  DynamicJsonBuffer jsonBuffer(BUFFER_SIZE);
//
//  JsonObject& root = jsonBuffer.parseObject(client);
//
//  if (!root.success()) {
//    Serial.println("JSON parsing failed!");
//    return false;
//  }
//
//  // Here were copy the strings we're interested in
//  strcpy(userData->name, root["name"]);
//  strcpy(userData->company, root["company"]["name"]);
//  // It's not mandatory to make a copy, you could just use the pointers
//  // Since, they are pointing inside the "content" buffer, so you need to make
//  // sure it's still in memory when you read the string
//
//  return true;
//}
