"""Notify platform for Notifheure."""
from __future__ import annotations

import json
import logging
from typing import Any

from homeassistant.components import mqtt
from homeassistant.components.notify import (
    ATTR_DATA,
    ATTR_TARGET,
    BaseNotificationService,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_PANEL_NAME, CONF_PANEL_TOPIC, DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Notifheure notify platform."""
    _LOGGER.warning("🟢 Notify: async_setup_entry appelé")
    
    # Récupérer les panneaux depuis hass.data
    panels = hass.data.get(DOMAIN, {}).get(config_entry.entry_id, [])
    
    _LOGGER.warning("🟢 Notify: %d panneau(x) chargé(s): %s", 
                   len(panels), 
                   [p.get(CONF_PANEL_NAME) for p in panels])
    
    # Créer le service de notification
    notify_service = NotifheureNotificationService(hass, panels, config_entry.entry_id)
    
    # Enregistrer le service notify.notifheure
    hass.services.async_register(
        "notify",
        "notifheure",
        notify_service.async_send_message,
    )
    
    _LOGGER.warning("🟢 Notify: Service notify.notifheure enregistré avec succès")


class NotifheureNotificationService(BaseNotificationService):
    """Implement the notification service for Notifheure."""

    def __init__(
        self, 
        hass: HomeAssistant, 
        panels: list[dict[str, str]],
        entry_id: str
    ) -> None:
        """Initialize the service."""
        self.hass = hass
        self.entry_id = entry_id
        self._panels = {
            p.get(CONF_PANEL_NAME, ""): p.get(CONF_PANEL_TOPIC, "") 
            for p in panels
        }
        _LOGGER.warning(
            "🟢 NotifheureService: Initialisé avec panneaux: %s",
            list(self._panels.keys()),
        )

    async def async_send_message(self, message: str = "", **kwargs: Any) -> None:
        """Send a message to one or more Notifheure panels."""
        _LOGGER.warning("🟢 Service: Message reçu='%s'", message)
        
        # Récupérer les targets
        targets = kwargs.get(ATTR_TARGET)
        data = kwargs.get(ATTR_DATA, {})

        # Si target est dans data
        if targets is None and ATTR_TARGET in data:
            targets = data.get(ATTR_TARGET)

        # Par défaut: tous les panneaux
        if targets is None:
            targets = list(self._panels.keys())
            _LOGGER.warning("🟡 Aucun target, envoi à tous: %s", targets)

        # Convertir en liste si string
        if isinstance(targets, str):
            targets = [targets]

        _LOGGER.warning("🟢 Targets: %s", targets)

        # Construire le payload
        payload_dict = {"msg": message}

        # Ajouter les options si présentes
        options = data.get("options", "")
        if options:
            payload_dict["opt"] = options
            _LOGGER.warning("🟢 Options: %s", options)

        # Envoyer à chaque panneau
        for target in targets:
            topic = self._panels.get(target)
            if not topic:
                _LOGGER.error(
                    "🔴 Panneau inconnu: %s (disponibles: %s)",
                    target,
                    list(self._panels.keys()),
                )
                continue

            payload = json.dumps(payload_dict)

            try:
                await mqtt.async_publish(self.hass, topic, payload, qos=1, retain=False)
                _LOGGER.warning("🟢 MQTT publié: %s -> %s: %s", target, topic, payload)
            except Exception as err:
                _LOGGER.error("🔴 Erreur MQTT pour %s: %s", target, err, exc_info=True)

    @property
    def targets(self) -> dict[str, str] | None:
        """Return a dictionary of registered targets."""
        return self._panels if self._panels else None
