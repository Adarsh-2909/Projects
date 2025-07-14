#include <WiFi.h>
#include <FirebaseESP32.h>
#include <Adafruit_Fingerprint.h>
#include <HardwareSerial.h>
#include <WebServer.h>

// Wi-Fi credentials
const char* ssid = "OPPO F23 5G";
const char* password = "AadiAppu";

// Firebase credentials
const char* FIREBASE_HOST = "authentication-6d57e-default-rtdb.asia-southeast1.firebasedatabase.app";
const char* FIREBASE_AUTH = "VPnUXkT9EnOma9YMVrtdyqhxiXF3";

// Firebase objects
FirebaseData firebaseData;
FirebaseAuth auth;
FirebaseConfig config;

// Fingerprint Sensor setup
#define RX_PIN 16  
#define TX_PIN 17  
HardwareSerial mySerial(2);
Adafruit_Fingerprint finger = Adafruit_Fingerprint(&mySerial);

// Web server
WebServer server(80);

void setup() {
  Serial.begin(115200);
  mySerial.begin(57600, SERIAL_8N1, RX_PIN, TX_PIN);

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) { delay(500); Serial.print("."); }
  Serial.println("\nWiFi connected! IP address: " + WiFi.localIP().toString());

  config.host = FIREBASE_HOST;
  config.signer.tokens.legacy_token = FIREBASE_AUTH;
  Firebase.begin(&config, &auth);
  Firebase.reconnectWiFi(true);
  Serial.println("Connected to Firebase!");

  finger.begin(57600);
  if (finger.verifyPassword()) {
    Serial.println("Fingerprint sensor ready!");
  } else {
    Serial.println("Failed to detect sensor. Check connections!");
    while (true);
  }

  // Web routes
  server.on("/", HTTP_GET, []() { server.send(200, "text/html", fingerprintPage()); });
  server.on("/authenticate", HTTP_GET, authenticateFingerprint);
  server.on("/enrollFingerprint", HTTP_GET, enrollFingerprint);
  server.on("/password", HTTP_GET, []() { server.send(200, "text/html", passwordPage()); });
  server.on("/validatePassword", HTTP_GET, validatePassword);
  server.on("/folders", HTTP_GET, []() { server.send(200, "text/html", folderPage()); });

  server.begin();
  Serial.println("Web server started!");
}

void loop() {
  server.handleClient();
}

// Enroll a fingerprint and store it in Firebase
void enrollFingerprint() {
  int id = 1; // Static ID for now (expand with user management)

  Serial.println("Place finger to enroll...");
  while (finger.getImage() != FINGERPRINT_OK);
  if (finger.image2Tz(1) != FINGERPRINT_OK) {
    server.send(400, "text/plain", "Error processing fingerprint.");
    return;
  }

  Serial.println("Remove finger...");
  delay(2000);
  Serial.println("Place same finger again...");
  
  while (finger.getImage() != FINGERPRINT_OK);
  if (finger.image2Tz(2) != FINGERPRINT_OK || finger.createModel() != FINGERPRINT_OK) {
    server.send(400, "text/plain", "Fingerprint enrollment failed.");
    return;
  }

  if (finger.storeModel(id) != FINGERPRINT_OK) {
    server.send(400, "text/plain", "Error storing fingerprint.");
    return;
  }

  // Store fingerprint ID in Firebase
  String path = "/fingerprints/" + String(id);
  if (Firebase.setInt(firebaseData, path, id)) {
    server.send(200, "text/plain", "Fingerprint enrolled successfully.");
  } else {
    server.send(500, "text/plain", "Failed to save fingerprint to Firebase.");
  }
}

// Authenticate using fingerprint
void authenticateFingerprint() {
  Serial.println("Place your finger for authentication...");
  while (finger.getImage() != FINGERPRINT_OK);
  
  if (finger.image2Tz() != FINGERPRINT_OK || finger.fingerFastSearch() != FINGERPRINT_OK) {
    server.send(200, "text/plain", "Fingerprint not recognized.");
    return;
  }

  int id = finger.fingerID;
  String path = "/fingerprints/" + String(id);

  if (Firebase.getInt(firebaseData, path) && firebaseData.dataType() == "int") {
    server.sendHeader("Location", "/password");
    server.send(302, "text/plain", "Redirecting to password page...");
  } else {
    server.send(200, "text/plain", "Fingerprint not found in database.");
  }
}

String fingerprintPage() {
  return R"rawliteral(
  <!DOCTYPE html>
  <html>
  <head>
    <title>Fingerprint Authentication</title>
    <style>
      body { font-family: Arial, sans-serif; text-align: center; background-color: #f4f4f4; }
      .container { margin-top: 50px; }
      h1 { color: #333; }
      .button { padding: 15px 25px; font-size: 18px; border: none; color: white; background-color: #007BFF; cursor: pointer; border-radius: 5px; }
      .button:hover { background-color: #0056b3; }
      img { margin: 20px; width: 120px; }
    </style>
  </head>
  <body>
    <div class="container">
      <h1>Fingerprint Authentication</h1>
      <img src="fingerprint.png" alt="Fingerprint">
      <br>
      <button class="button" onclick="location.href='/authenticate'">Scan Fingerprint</button>
      <button class="button" onclick="location.href='/enrollFingerprint'">Enroll Fingerprint</button>
    </div>
  </body>
  </html>
  )rawliteral";
}

void validatePassword() {
  if (!server.hasArg("password")) {
    server.send(400, "text/plain", "Password not provided.");
    return;
  }
  String password = server.arg("password");
  if (password == "Aadi@123") {
    server.sendHeader("Location", "/folders");
    server.send(302, "text/plain", "Redirecting to folders...");
  } else {
    server.send(200, "text/plain", "Incorrect Password.");
  }
}

String passwordPage() {
  return R"rawliteral(
  <!DOCTYPE html>
  <html>
  <head>
    <title>Password Authentication</title>
    <style>
      body { font-family: Arial, sans-serif; text-align: center; background-color: #f4f4f4; }
      .container { margin-top: 50px; }
      h1 { color: #333; }
      input { padding: 10px; font-size: 16px; border: 1px solid #ccc; border-radius: 5px; }
      .button { padding: 10px 20px; font-size: 16px; color: white; background-color: #28a745; border: none; border-radius: 5px; cursor: pointer; }
      .button:hover { background-color: #218838; }
    </style>
  </head>
  <body>
    <div class="container">
      <h1>Enter Password</h1>
      <form action="/validatePassword" method="GET">
        <input type="password" name="password" required>
        <button class="button" type="submit">Submit</button>
      </form>
    </div>
  </body>
  </html>
  )rawliteral";
}

String folderPage() {
  return R"rawliteral(
  <!DOCTYPE html>
  <html>
  <head>
    <title>Folders</title>
    <style>
      body { font-family: Arial, sans-serif; text-align: center; background-color: #f4f4f4; }
      .container { margin-top: 50px; }
      h1 { color: #333; }
      .button-container { display: flex; justify-content: center; gap: 15px; margin-top: 20px; }
      .button { padding: 15px 25px; font-size: 18px; border: none; color: white; background-color: #007BFF; cursor: pointer; border-radius: 5px; }
      .button:hover { background-color: #0056b3; }
    </style>
  </head>
  <body>
    <div class="container">
      <h1>Select a Folder</h1>
      <div class="button-container">
        <!-- Google Drive folder links -->
        <button class="button" onclick="window.location.href='https://drive.google.com/drive/folders/1f0FvUoDmnbfxHylgCzV4OOCn4iIIcRCL?usp=sharing'">Certificates</button>
        <button class="button" onclick="window.location.href='https://drive.google.com/drive/folders/1rZTnVyFrc_P_zpLmFOFLdZsTlJuSOMtt?usp=drive_link'">Important Data</button>
        <button class="button" onclick="window.location.href='https://drive.google.com/drive/folders/1QzHX0iu8pN4UdP2oZ_nO1uCCesAB5-gG?usp=drive_link'">Money</button>
      </div>
    </div>
  </body>
  </html>
  )rawliteral";
}
