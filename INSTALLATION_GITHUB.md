# 🚀 Guide d'installation et Configuration HACS

## 📦 Étape 1 : Préparer votre repository GitHub

### 1.1 Mettre à jour votre repository

Supprimez tout le contenu actuel de votre repository `hacs-NotifHeure` et remplacez-le par les fichiers de l'archive.

**Structure finale attendue :**

```
hacs-NotifHeure/
├── custom_components/
│   └── notifheure/
│       ├── __init__.py
│       ├── manifest.json
│       ├── const.py
│       ├── config_flow.py
│       ├── notify.py
│       ├── strings.json
│       ├── services.yaml
│       └── translations/
│           └── fr.json
├── .gitignore
├── hacs.json
├── README.md
├── info.md
└── LICENSE
```

### 1.2 Commandes Git pour mettre à jour

```bash
# Cloner votre repo (si pas déjà fait)
git clone https://github.com/WadohS/hacs-NotifHeure.git
cd hacs-NotifHeure

# Supprimer l'ancien contenu (sauf .git)
rm -rf custom_components *.py *.json *.md *.txt 2>/dev/null

# Extraire l'archive téléchargée
unzip notifheure_v1.0.0.zip
mv notifheure_integration/* .
rmdir notifheure_integration

# Vérifier la structure
tree -L 3  # ou ls -R

# Commit et push
git add .
git commit -m "✨ Version 1.0.0 - Intégration complète fonctionnelle"
git push origin main
```

### 1.3 Créer une release (Recommandé pour HACS)

1. Sur GitHub, allez dans **Releases** → **Create a new release**
2. Tag version : `v1.0.0`
3. Release title : `Version 1.0.0 - Release initiale`
4. Description :
   ```markdown
   ## 🎉 Première version stable
   
   ### ✨ Fonctionnalités
   - Configuration via l'interface utilisateur
   - Support de multiples panneaux LED
   - Communication MQTT
   - Compatible NeoPixel/WS2812B
   
   ### 📦 Installation
   Voir le [README](https://github.com/WadohS/hacs-NotifHeure/blob/main/README.md)
   ```
5. Cliquez sur **Publish release**

---

## 🔧 Étape 2 : Configuration HACS

### 2.1 Ajouter votre repository dans HACS

#### Sur Home Assistant :

1. Ouvrez **HACS** dans le menu latéral
2. Cliquez sur **Intégrations**
3. Cliquez sur les **3 points** en haut à droite
4. Sélectionnez **Dépôts personnalisés**
5. Ajoutez :
   - **URL** : `https://github.com/WadohS/hacs-NotifHeure`
   - **Catégorie** : `Integration`
6. Cliquez sur **Ajouter**

### 2.2 Installer l'intégration via HACS

1. Dans **HACS** → **Intégrations**
2. Recherchez `Notifheure`
3. Cliquez sur l'intégration
4. Cliquez sur **Télécharger**
5. Sélectionnez la version (normalement `v1.0.0`)
6. Attendez la fin du téléchargement
7. **Redémarrez Home Assistant**

---

## ✅ Étape 3 : Vérification et test

### 3.1 Vérifier l'installation

Après redémarrage, allez dans **Paramètres** → **Système** → **Journaux** et cherchez :

```
[custom_components.notifheure] Notifheure chargé avec 0 panneau(x): []
```

✅ Si vous voyez ce message = Installation réussie !

### 3.2 Ajouter l'intégration

1. **Paramètres** → **Appareils et services**
2. **+ Ajouter une intégration**
3. Recherchez `Notifheure`
4. Cliquez sur **Configurer**
5. L'intégration est ajoutée !

### 3.3 Configurer vos panneaux

1. Dans **Appareils et services**, trouvez **Notifheure**
2. Cliquez sur **Configurer** (icône engrenage)
3. **Ajouter un panneau** :
   - **Nom** : `test` (ou autre)
   - **Topic MQTT** : `notifheure/test`
4. Cliquez sur **Soumettre**

### 3.4 Test du service

Dans **Outils de développement** → **Services** :

```yaml
service: notify.notifheure
data:
  target: ["test"]
  message: "Hello World!"
  data:
    options: "nzo=0;pause=1"
```

Cliquez sur **Appeler le service**

Vérifiez les logs :
```
[custom_components.notifheure.notify] Message envoyé à test (notifheure/test): {"msg":"Hello World!","opt":"nzo=0;pause=1"}
```

---

## 🐛 Dépannage

### L'intégration n'apparaît pas dans HACS

**Causes possibles :**
- Le fichier `hacs.json` est mal placé (doit être à la racine)
- La structure du repo est incorrecte
- HACS n'a pas été rechargé

**Solutions :**
```bash
# Vérifier la structure sur GitHub
https://github.com/WadohS/hacs-NotifHeure

# Dans HACS, recharger les dépôts :
# HACS → 3 points → Recharger les dépôts
```

### Erreur lors du téléchargement

**Solution :**
1. Supprimez le dépôt personnalisé
2. Ajoutez-le à nouveau
3. Si ça persiste, installez manuellement :

```bash
# Sur Home Assistant (SSH/Terminal)
cd /config/custom_components
rm -rf notifheure
git clone https://github.com/WadohS/hacs-NotifHeure.git temp
mv temp/custom_components/notifheure ./
rm -rf temp
```

### L'intégration ne charge pas

Vérifiez les logs :
```yaml
# Dans configuration.yaml
logger:
  default: info
  logs:
    custom_components.notifheure: debug
```

Redémarrez et consultez les logs.

---

## 📝 Checklist finale

- [ ] Repository GitHub mis à jour avec la nouvelle structure
- [ ] Release v1.0.0 créée sur GitHub
- [ ] Repository ajouté dans HACS comme dépôt personnalisé
- [ ] Intégration téléchargée via HACS
- [ ] Home Assistant redémarré
- [ ] Intégration ajoutée dans Appareils et services
- [ ] Au moins un panneau configuré
- [ ] Service `notify.notifheure` testé avec succès
- [ ] Logs vérifiés (pas d'erreur)

---

## 🎯 Prochaines étapes

Une fois l'intégration fonctionnelle :

1. **Configurer votre ESP32** avec le code fourni dans le README
2. **Tester la communication MQTT** entre HA et ESP32
3. **Créer des automatisations** pour utiliser vos panneaux LED
4. **Partager votre expérience** en créant une discussion GitHub

---

## 🆘 Besoin d'aide ?

- 📖 [README complet](https://github.com/WadohS/hacs-NotifHeure/blob/main/README.md)
- 🐛 [Ouvrir une issue](https://github.com/WadohS/hacs-NotifHeure/issues)
- 💬 [Discussions GitHub](https://github.com/WadohS/hacs-NotifHeure/discussions)

---

**Bon test ! 🚀**
