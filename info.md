# Notifheure

Intégration Home Assistant pour contrôler des panneaux LED Notifheure via MQTT.

## Configuration

1. Installez l'intégration via HACS
2. Ajoutez l'intégration dans Paramètres → Appareils et services
3. Configurez vos panneaux LED dans les options
4. Utilisez le service `notify.notifheure` pour envoyer des messages

## Utilisation rapide

```yaml
service: notify.notifheure
data:
  target: ["salon"]
  message: "Bonjour !"
  data:
    options: "nzo=0;pause=1"
```

Pour plus d'informations, consultez le [README complet](https://github.com/WadohS/hacs-NotifHeure).
