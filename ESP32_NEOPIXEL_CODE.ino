/*
 * Notifheure - Code ESP32 pour bandes LED NeoPixel
 * Compatible avec l'intégration Home Assistant Notifheure
 * 
 * Hardware requis:
 * - ESP32 (NodeMCU, DevKit, etc.)
 * - Bande LED NeoPixel WS2812B
 * - Alimentation 5V adaptée
 * 
 * Bibliothèques requises:
 * - PubSubClient (by Nick O'Leary)
 * - Adafruit NeoPixel
 * - ArduinoJson (v6+)
 */

#include <WiFi.h>
#include <PubSubClient.h>
#include <Adafruit_NeoPixel.h>
#include <ArduinoJson.h>

// ==========================================
// CONFIGURATION - À MODIFIER SELON VOS BESOINS
// ==========================================

// Configuration WiFi
const char* WIFI_SSID = "VOTRE_SSID";
const char* WIFI_PASSWORD = "VOTRE_PASSWORD";

// Configuration MQTT
const char* MQTT_SERVER = "192.168.1.100";  // IP de votre broker MQTT
const int MQTT_PORT = 1883;
const char* MQTT_USER = "votre_user";       // Laisser vide si pas d'authentification
const char* MQTT_PASSWORD = "votre_password"; // Laisser vide si pas d'authentification
const char* MQTT_TOPIC = "notifheure/salon"; // Topic MQTT (doit correspondre à la config HA)
const char* MQTT_CLIENT_ID = "ESP32_Notifheure_Salon"; // ID unique pour ce client

// Configuration NeoPixel
#define LED_PIN 5           // GPIO utilisé (GPIO5 = D5)
#define NUM_LEDS 60         // Nombre de LEDs sur la bande
#define LED_BRIGHTNESS 50   // Luminosité (0-255)

// ==========================================
// INITIALISATION
// ==========================================

Adafruit_NeoPixel strip = Adafruit_NeoPixel(NUM_LEDS, LED_PIN, NEO_GRB + NEO_KHZ800);
WiFiClient espClient;
PubSubClient mqttClient(espClient);

// Variables globales
String currentMessage = "";
unsigned long lastUpdate = 0;
int scrollPosition = 0;

// ==========================================
// SETUP
// ==========================================

void setup() {
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("\n\n=================================");
  Serial.println("   NOTIFHEURE - ESP32 + NeoPixel");
  Serial.println("=================================\n");
  
  // Initialiser NeoPixel
  strip.begin();
  strip.setBrightness(LED_BRIGHTNESS);
  strip.show(); // Éteindre toutes les LEDs
  
  Serial.println("✓ NeoPixel initialisé");
  Serial.print("  - LEDs: ");
  Serial.println(NUM_LEDS);
  Serial.print("  - Pin: GPIO");
  Serial.println(LED_PIN);
  Serial.print("  - Luminosité: ");
  Serial.println(LED_BRIGHTNESS);
  
  // Animation de démarrage
  bootAnimation();
  
  // Connexion WiFi
  setupWiFi();
  
  // Configuration MQTT
  mqttClient.setServer(MQTT_SERVER, MQTT_PORT);
  mqttClient.setCallback(mqttCallback);
  mqttClient.setBufferSize(512); // Augmenter si messages longs
  
  // Connexion MQTT
  connectMQTT();
  
  Serial.println("\n✅ Système prêt !");
  Serial.println("En attente de messages MQTT...\n");
}

// ==========================================
// LOOP PRINCIPAL
// ==========================================

void loop() {
  // Maintenir la connexion MQTT
  if (!mqttClient.connected()) {
    connectMQTT();
  }
  mqttClient.loop();
  
  // Gérer l'affichage du message (scroll, animations, etc.)
  // À implémenter selon vos besoins
  
  delay(10);
}

// ==========================================
// CONNEXION WIFI
// ==========================================

void setupWiFi() {
  Serial.print("Connexion WiFi à ");
  Serial.println(WIFI_SSID);
  
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 30) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n✓ WiFi connecté !");
    Serial.print("  - IP: ");
    Serial.println(WiFi.localIP());
    Serial.print("  - Signal: ");
    Serial.print(WiFi.RSSI());
    Serial.println(" dBm");
  } else {
    Serial.println("\n✗ Échec connexion WiFi !");
    Serial.println("Redémarrage dans 5 secondes...");
    delay(5000);
    ESP.restart();
  }
}

// ==========================================
// CONNEXION MQTT
// ==========================================

void connectMQTT() {
  while (!mqttClient.connected()) {
    Serial.print("Connexion MQTT à ");
    Serial.print(MQTT_SERVER);
    Serial.print(":");
    Serial.println(MQTT_PORT);
    
    // Tentative de connexion
    bool connected;
    if (strlen(MQTT_USER) > 0) {
      connected = mqttClient.connect(MQTT_CLIENT_ID, MQTT_USER, MQTT_PASSWORD);
    } else {
      connected = mqttClient.connect(MQTT_CLIENT_ID);
    }
    
    if (connected) {
      Serial.println("✓ MQTT connecté !");
      Serial.print("  - Topic: ");
      Serial.println(MQTT_TOPIC);
      
      // S'abonner au topic
      mqttClient.subscribe(MQTT_TOPIC);
      
      // Animation de connexion réussie
      flashColor(0, 255, 0, 3); // Vert 3 fois
      
    } else {
      Serial.print("✗ Échec MQTT, code: ");
      Serial.println(mqttClient.state());
      Serial.println("Nouvelle tentative dans 5 secondes...");
      
      // Animation d'erreur
      flashColor(255, 0, 0, 2); // Rouge 2 fois
      
      delay(5000);
    }
  }
}

// ==========================================
// CALLBACK MQTT - RÉCEPTION DE MESSAGES
// ==========================================

void mqttCallback(char* topic, byte* payload, unsigned int length) {
  Serial.println("\n📨 Message MQTT reçu !");
  Serial.print("  - Topic: ");
  Serial.println(topic);
  Serial.print("  - Taille: ");
  Serial.print(length);
  Serial.println(" octets");
  
  // Convertir payload en String
  String payloadStr = "";
  for (unsigned int i = 0; i < length; i++) {
    payloadStr += (char)payload[i];
  }
  
  Serial.print("  - Payload brut: ");
  Serial.println(payloadStr);
  
  // Parser le JSON
  StaticJsonDocument<512> doc;
  DeserializationError error = deserializeJson(doc, payloadStr);
  
  if (error) {
    Serial.print("✗ Erreur parsing JSON: ");
    Serial.println(error.c_str());
    flashColor(255, 165, 0, 2); // Orange pour erreur JSON
    return;
  }
  
  // Extraire les données
  const char* message = doc["msg"];
  const char* options = doc["opt"] | ""; // Valeur par défaut vide
  
  Serial.println("\n📝 Données extraites:");
  Serial.print("  - Message: ");
  Serial.println(message);
  Serial.print("  - Options: ");
  Serial.println(options);
  
  // Afficher le message sur les LEDs
  currentMessage = String(message);
  displayMessage(message, options);
}

// ==========================================
// AFFICHAGE DU MESSAGE SUR LES LEDS
// ==========================================

void displayMessage(const char* message, const char* options) {
  Serial.println("\n🎨 Affichage du message...");
  
  // Parser les options
  // Format: "nzo=0;pause=1;color=FF0000"
  bool nzo = false;
  int pause = 0;
  uint32_t color = strip.Color(0, 0, 255); // Bleu par défaut
  
  // TODO: Parser les options selon vos besoins
  // Exemple simple ci-dessous
  
  // Animation simple: clignotement bleu
  for (int i = 0; i < 3; i++) {
    // Allumer
    for (int j = 0; j < NUM_LEDS; j++) {
      strip.setPixelColor(j, color);
    }
    strip.show();
    delay(300);
    
    // Éteindre
    strip.clear();
    strip.show();
    delay(300);
  }
  
  // TODO: Implémenter l'affichage du texte
  // Vous pouvez utiliser une matrice LED ou un défilement
  // selon votre matériel et vos besoins
  
  Serial.println("✓ Message affiché !");
}

// ==========================================
// ANIMATIONS UTILITAIRES
// ==========================================

// Animation de démarrage
void bootAnimation() {
  Serial.println("Animation de démarrage...");
  
  // Arc-en-ciel rapide
  for (int j = 0; j < 255; j += 5) {
    for (int i = 0; i < NUM_LEDS; i++) {
      strip.setPixelColor(i, Wheel((i + j) & 255));
    }
    strip.show();
    delay(10);
  }
  
  strip.clear();
  strip.show();
}

// Flash de couleur
void flashColor(uint8_t r, uint8_t g, uint8_t b, int times) {
  for (int i = 0; i < times; i++) {
    for (int j = 0; j < NUM_LEDS; j++) {
      strip.setPixelColor(j, strip.Color(r, g, b));
    }
    strip.show();
    delay(200);
    
    strip.clear();
    strip.show();
    delay(200);
  }
}

// Fonction roue de couleurs (pour arc-en-ciel)
uint32_t Wheel(byte WheelPos) {
  WheelPos = 255 - WheelPos;
  if (WheelPos < 85) {
    return strip.Color(255 - WheelPos * 3, 0, WheelPos * 3);
  }
  if (WheelPos < 170) {
    WheelPos -= 85;
    return strip.Color(0, WheelPos * 3, 255 - WheelPos * 3);
  }
  WheelPos -= 170;
  return strip.Color(WheelPos * 3, 255 - WheelPos * 3, 0);
}

// ==========================================
// FONCTIONS AVANCÉES (À IMPLÉMENTER)
// ==========================================

/*
 * TODO: Implémenter selon vos besoins:
 * 
 * 1. Défilement de texte
 *    - Utiliser une matrice LED 8x8 ou 16x8
 *    - Bibliothèque MD_Parola pour matrices MAX7219
 * 
 * 2. Affichage sur segment
 *    - Bibliothèque TM1637 pour afficheurs 7 segments
 * 
 * 3. Effets avancés
 *    - Changement de couleur selon le message
 *    - Animations personnalisées
 *    - Gestion de la luminosité automatique
 * 
 * 4. Parser les options
 *    - nzo: zones d'affichage
 *    - pause: délai entre messages
 *    - speed: vitesse de défilement
 *    - color: couleur personnalisée
 */
