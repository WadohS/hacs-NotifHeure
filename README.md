# Notifheure pour Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![GitHub release](https://img.shields.io/github/release/WadohS/hacs-NotifHeure.svg)](https://github.com/WadohS/hacs-NotifHeure/releases)
[![License](https://img.shields.io/github/license/WadohS/hacs-NotifHeure.svg)](LICENSE)

Intégration Home Assistant pour contrôler des panneaux LED Notifheure (compatible NeoPixel/WS2812B) via MQTT.

Basé sur le projet [Notifheure de Byfeel](https://www.youtube.com/watch?v=xxx), cette intégration permet d'afficher des notifications sur des bandes LED contrôlées par ESP32.

## 🎯 Fonctionnalités

- ✅ Configuration via l'interface utilisateur (Config Flow)
- ✅ Support de multiples panneaux LED
- ✅ Communication via MQTT
- ✅ Options de formatage personnalisables
- ✅ Compatible NeoPixel (WS2812B, WS2811, etc.)
- ✅ Compatible avec le tutoriel Byfeel

## 📦 Installation

### Méthode 1 : Via HACS (recommandé)

1. Ouvrez HACS dans Home Assistant
2. Cliquez sur les 3 points en haut à droite → **Dépôts personnalisés**
3. Ajoutez l'URL : `https://github.com/WadohS/hacs-NotifHeure`
4. Sélectionnez la catégorie : **Integration**
5. Cliquez sur **Ajouter**
6. Recherchez "Notifheure" dans HACS
7. Cliquez sur **Télécharger**
8. Redémarrez Home Assistant

### Méthode 2 : Installation manuelle

1. Téléchargez la dernière version depuis [Releases](https://github.com/WadohS/hacs-NotifHeure/releases)
2. Extrayez le contenu dans le dossier `custom_components/notifheure` de votre Home Assistant
3. Redémarrez Home Assistant

## ⚙️ Configuration

### Prérequis

- ✅ Home Assistant 2023.1.0 ou supérieur
- ✅ Intégration MQTT configurée et fonctionnelle
- ✅ ESP32 avec firmware compatible (voir section Hardware)

### Configuration de l'intégration

1. Allez dans **Paramètres** → **Appareils et services**
2. Cliquez sur **+ Ajouter une intégration**
3. Recherchez **Notifheure**
4. Cliquez sur **Configurer**
5. L'intégration est maintenant installée !

### Ajouter des panneaux LED

1. Dans **Appareils et services**, trouvez **Notifheure**
2. Cliquez sur **Configurer** (icône engrenage)
3. Sélectionnez **Ajouter un panneau**
4. Renseignez :
   - **Nom du panneau** : ex. `salon`, `cuisine`, `bureau`
   - **Topic MQTT** : ex. `notifheure/salon`
5. Répétez pour chaque panneau

### Configuration MQTT

Assurez-vous que votre broker MQTT est configuré dans Home Assistant :

```yaml
# configuration.yaml (si pas déjà fait)
mqtt:
  broker: 192.168.1.100  # IP de votre broker
  port: 1883
  username: !secret mqtt_user
  password: !secret mqtt_password
```

## 🚀 Utilisation

### Service de notification

Une fois configuré, un service `notify.notifheure` est créé automatiquement.

#### Exemple basique

```yaml
service: notify.notifheure
data:
  target: ["salon"]
  message: "Bonjour !"
```

#### Exemple avec options

```yaml
service: notify.notifheure
data:
  target: ["salon", "cuisine"]
  message: "Température: {{ states('sensor.temperature_salon') }}°C"
  data:
    options: "nzo=0;pause=1"
```

#### Exemple avec templating

```yaml
service: notify.notifheure
data:
  target: ["salon"]
  message: >
    {% if is_state('binary_sensor.porte_entree', 'on') %}
      Porte ouverte !
    {% else %}
      Porte fermée
    {% endif %}
  data:
    options: "nzo=0;pause=0"
```

### Paramètres disponibles

| Paramètre | Type | Requis | Description |
|-----------|------|--------|-------------|
| `target` | liste | Non | Liste des panneaux cibles. Si omis, envoie à tous les panneaux |
| `message` | string | Oui | Message à afficher sur le panneau LED |
| `data.options` | string | Non | Options de formatage (voir ci-dessous) |

### Options de formatage

Les options sont envoyées sous forme de string séparées par des points-virgules :

```
"option1=valeur1;option2=valeur2"
```

Options standard (selon votre firmware) :
- `nzo=0` : Pas de zone (affichage complet)
- `pause=1` : Pause entre les messages
- `speed=50` : Vitesse de défilement
- `color=FF0000` : Couleur en hexadécimal
- Autres selon votre code ESP32

## 🔧 Configuration Hardware (ESP32 + NeoPixel)

### Matériel nécessaire

- ESP32 (NodeMCU, DevKit, etc.)
- Bande LED NeoPixel (WS2812B, WS2811)
- Alimentation 5V adaptée (selon le nombre de LEDs)
- Câbles et condensateur 1000µF (recommandé)

### Schéma de câblage

```
ESP32          NeoPixel
-----          --------
GPIO 5   --->  DIN
GND      --->  GND
5V       --->  5V (via alimentation externe)
```

⚠️ **Important** : Alimentez la bande LED avec une source externe si vous avez plus de 10 LEDs !

### Firmware ESP32

Voici un code de base compatible avec cette intégration :

```cpp
#include <WiFi.h>
#include <PubSubClient.h>
#include <Adafruit_NeoPixel.h>
#include <ArduinoJson.h>

// Configuration WiFi
const char* ssid = "VOTRE_SSID";
const char* password = "VOTRE_PASSWORD";

// Configuration MQTT
const char* mqtt_server = "192.168.1.100";
const int mqtt_port = 1883;
const char* mqtt_user = "votre_user";
const char* mqtt_password = "votre_password";
const char* mqtt_topic = "notifheure/salon";  // À adapter selon votre config

// Configuration NeoPixel
#define LED_PIN 5
#define NUM_LEDS 60
Adafruit_NeoPixel strip = Adafruit_NeoPixel(NUM_LEDS, LED_PIN, NEO_GRB + NEO_KHZ800);

WiFiClient espClient;
PubSubClient client(espClient);

void setup() {
  Serial.begin(115200);
  
  // Initialiser NeoPixel
  strip.begin();
  strip.show();
  strip.setBrightness(50);
  
  // Connexion WiFi
  setup_wifi();
  
  // Connexion MQTT
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);
}

void setup_wifi() {
  delay(10);
  Serial.println("Connexion WiFi...");
  WiFi.begin(ssid, password);
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  
  Serial.println("\nWiFi connecté !");
  Serial.print("IP: ");
  Serial.println(WiFi.localIP());
}

void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Message reçu sur ");
  Serial.println(topic);
  
  // Parser le JSON
  StaticJsonDocument<256> doc;
  DeserializationError error = deserializeJson(doc, payload, length);
  
  if (error) {
    Serial.println("Erreur parsing JSON");
    return;
  }
  
  const char* message = doc["msg"];
  const char* options = doc["opt"];
  
  Serial.print("Message: ");
  Serial.println(message);
  Serial.print("Options: ");
  Serial.println(options);
  
  // Afficher le message sur les LEDs
  displayMessage(message);
}

void displayMessage(const char* message) {
  // Animation simple : clignotement bleu
  for (int i = 0; i < 3; i++) {
    // Allumer en bleu
    for (int j = 0; j < NUM_LEDS; j++) {
      strip.setPixelColor(j, strip.Color(0, 0, 255));
    }
    strip.show();
    delay(300);
    
    // Éteindre
    strip.clear();
    strip.show();
    delay(300);
  }
  
  // TODO: Implémenter l'affichage du texte selon vos besoins
  // Vous pouvez utiliser une matrice LED ou un défilement
}

void reconnect() {
  while (!client.connected()) {
    Serial.println("Connexion MQTT...");
    
    if (client.connect("ESP32_Notifheure", mqtt_user, mqtt_password)) {
      Serial.println("MQTT connecté !");
      client.subscribe(mqtt_topic);
    } else {
      Serial.print("Échec, rc=");
      Serial.print(client.state());
      Serial.println(" Nouvelle tentative dans 5s");
      delay(5000);
    }
  }
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();
}
```

### Bibliothèques Arduino nécessaires

Installez ces bibliothèques dans Arduino IDE :
- `PubSubClient` by Nick O'Leary
- `Adafruit NeoPixel` by Adafruit
- `ArduinoJson` by Benoit Blanchon

## 📝 Exemples d'automatisations

### Notification de porte ouverte

```yaml
automation:
  - alias: "Notif porte ouverte"
    trigger:
      - platform: state
        entity_id: binary_sensor.porte_entree
        to: "on"
    action:
      - service: notify.notifheure
        data:
          target: ["entree"]
          message: "PORTE OUVERTE"
          data:
            options: "nzo=0;pause=1"
```

### Notification météo du matin

```yaml
automation:
  - alias: "Météo du matin"
    trigger:
      - platform: time
        at: "07:00:00"
    action:
      - service: notify.notifheure
        data:
          target: ["salon"]
          message: >
            Météo: {{ states('sensor.temperature_exterieure') }}°C
            {{ state_attr('weather.home', 'forecast')[0].condition }}
```

### Rappel de rendez-vous

```yaml
automation:
  - alias: "Rappel RDV"
    trigger:
      - platform: calendar
        entity_id: calendar.personnel
        event: start
        offset: "-00:15:00"
    action:
      - service: notify.notifheure
        data:
          target: ["bureau"]
          message: "RDV dans 15 minutes!"
```

## 🐛 Dépannage

### L'intégration n'apparaît pas

1. Vérifiez les logs : **Paramètres** → **Système** → **Journaux**
2. Recherchez "notifheure" ou "custom_components"
3. Assurez-vous que le dossier est bien `custom_components/notifheure/`
4. Vérifiez que tous les fichiers sont présents
5. Redémarrez Home Assistant

### MQTT ne fonctionne pas

1. Vérifiez que l'intégration MQTT est configurée
2. Testez avec MQTT Explorer ou `mosquitto_pub`
3. Vérifiez les logs de votre broker MQTT
4. Assurez-vous que l'ESP32 est connecté au broker

### Les messages ne s'affichent pas

1. Vérifiez le topic MQTT dans la configuration
2. Consultez les logs de l'ESP32 (Serial Monitor)
3. Testez l'envoi MQTT manuel :
   ```bash
   mosquitto_pub -h BROKER_IP -t "notifheure/salon" -m '{"msg":"Test","opt":""}'
   ```

### Logs détaillés

Pour activer les logs détaillés, ajoutez dans `configuration.yaml` :

```yaml
logger:
  default: info
  logs:
    custom_components.notifheure: debug
```

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :

- Ouvrir une [Issue](https://github.com/WadohS/hacs-NotifHeure/issues) pour un bug
- Proposer une [Pull Request](https://github.com/WadohS/hacs-NotifHeure/pulls) pour une amélioration
- Partager vos exemples d'utilisation

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## 🙏 Remerciements

- [Byfeel](https://www.youtube.com/@byfeel) pour le projet original Notifheure
- La communauté Home Assistant
- Les contributeurs de ce projet

## 📞 Support

- 🐛 [Issues GitHub](https://github.com/WadohS/hacs-NotifHeure/issues)
- 💬 [Discussions GitHub](https://github.com/WadohS/hacs-NotifHeure/discussions)
- 📺 [Tutoriel Byfeel](https://www.youtube.com/watch?v=xxx)

## 🔗 Liens utiles

- [Documentation Home Assistant](https://www.home-assistant.io/)
- [HACS](https://hacs.xyz/)
- [MQTT](https://mqtt.org/)
- [Adafruit NeoPixel Guide](https://learn.adafruit.com/adafruit-neopixel-uberguide)

---

⭐ **Si ce projet vous est utile, n'hésitez pas à lui donner une étoile sur GitHub !**
