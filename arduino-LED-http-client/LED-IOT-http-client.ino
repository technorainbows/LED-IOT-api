/*
  LED-IOT-APP v0.0.2
  Simple sketch that uses ESP board to connect to local wifi network then gets LED state from python API (ledAPI.py)

  Receives data as JSON formatted as {"ledState": true] or {"ledState": false} and toggles LEDs between off and rainbow.


*/

#include <FastLED.h>
#include "credentials.h" // wifi network credentials stored in separate file

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


// if using ESP8266....
//#include <ESP8266WiFi.h>
//#include <ESP8266WiFiMulti.h>
//#include <ESP8266HTTPClient.h>
//ESP8266WiFiMulti wifiMulti;
//#include <ArduinoHttpClient.h>




String apiURL = "http://10.0.0.59:5000/light";
String controllerURL = "10.0.0.59/site/index.html";


//RMT is an ESP hardware feature that offloads stuff like PWM and led strip protocol, it's rad
//#define FASTLED_RMT_CORE_DRIVER true
#define FASTLED_RMT_MAX_CHANNELS 1
FASTLED_USING_NAMESPACE

//#define LED_TYPE    WS2812B
#define LED_TYPE    WS2811


//#ifdef DEV_LIGHTCONTROL_TRIANGLE
#define DATA_PIN   25
char* hostname = "trianglez";
#define COLOR_ORDER GRB //pixels
#define COLOR_CORRECT TypicalLEDStrip
#define NUM_LEDS 200
#define MILLI_AMPS         800
#define BRIGHTNESS          100
#define FRAMES_PER_SECOND  120

//#endif


CRGB leds[NUM_LEDS];

uint8_t speed = 10;

uint8_t gHue = 0; // rotating "base color" used by many of the patterns

boolean connectioWasAlive = true;
bool lastState = false;


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


void setup() {
  Serial.begin(115200);

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
  //  wifiMulti.addAP("ssid_from_AP_2", "your_password_for_AP_2");
  //  wifiMulti.addAP("ssid_from_AP_3", "your_password_for_AP_3");

  Serial.println("Connecting Wifi...");
  if (wifiMulti.run() == WL_CONNECTED) {
    Serial.println("");
    Serial.println("WiFi connected");
    Serial.println("IP address: ");
    Serial.println(WiFi.localIP());

    // turn leds to green if connected
    fill_solid(leds, NUM_LEDS, CRGB::Green);
    FastLED.show();
    delay(100);
    fill_solid(leds, NUM_LEDS, CRGB::Black);
    FastLED.show();
  }

  setupAOTA(); // set up arduino over-the-air updating

  updateDisplay(); // update OLED screen on device


}




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

bool ledsState = false;

void loop() {

  //   check wifi status
  if (wifiMulti.run() != WL_CONNECTED) {
    Serial.println("WiFi not connected!");
    // turn first 5 leds to red if not connected
    fill_solid(leds, 20, CRGB::Red);
    FastLED.show();
    delay(500);
  }

  EVERY_N_MILLISECONDS(500) {
    //    monitorWiFi();
    ArduinoOTA.handle();
    // wait for WiFi connection
    if ((wifiMulti.run() == WL_CONNECTED)) {
        
//      Serial.println("wifi connected, connecting to api");
      
      HTTPClient http;

      // start connection and send HTTP header

      http.begin(apiURL);

      //    Serial.print("[HTTP] GET...\n");
      int httpCode = http.GET();

      // Check returning httpCode -- will be negative on error
      if (httpCode > 0) {
                    Serial.printf("[HTTP] GET... code: %d\n", httpCode);

        // file found at server
        if (httpCode == HTTP_CODE_OK) {
          Serial.print("Found file at server: ");
          String payload = http.getString();
                  Serial.println(payload);
  
          // parse payload

          const size_t capacity = JSON_OBJECT_SIZE(1) + 20;
          DynamicJsonBuffer jsonBuffer(capacity);

          //        const char* json = "{\"ledsState\":true}";

          JsonObject& root = jsonBuffer.parseObject(payload);

           ledsState = root["ledsState"]; // true

          if (ledsState != lastState) {
            lastState = ledsState;
            Serial.printf("ledState = %d\n", ledsState);
            
          }

        }
      } else {
        Serial.printf("[HTTP] GET... failed, error: %s\n", http.errorToString(httpCode).c_str());
      }

      http.end(); // close connection
//      Serial.println("Closing connection");
    }
  }

//  Serial.println("FastLED.show & FastLED.delay");
  //  delay(500);
  updateLEDS();
  FastLED.show();

  
  // insert a delay to keep the framerate modest
  FastLED.delay(1000 / FRAMES_PER_SECOND);

}


void updateLEDS() {

  if (!ledsState) fill_solid(leds, NUM_LEDS, CRGB::Black);
  
  else {
    fill_rainbow( leds, NUM_LEDS, gHue, speed);
    EVERY_N_MILLISECONDS( 10 ) { gHue++; } // slowly cycle the "base color" through the rainbow
  }
    



}




void updateDisplay() {//updates the little OLED status screen

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
/*


      Built upon the amazing FastLED work of Daniel Garcia and Mark Kriegsman:
   https://github.com/FastLED/FastLED

   ESP32 support provided by the hard work of Sam Guyer:
   https://github.com/samguyer/FastLED


   This program is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation, either version 3 of the License, or
   (at your option) any later version.

   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/
