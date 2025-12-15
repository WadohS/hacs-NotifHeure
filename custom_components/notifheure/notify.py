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
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .const import CONF_PANEL_NAME, CONF_PANEL_TOPIC, DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_get_service(
    hass: HomeAssistant,
    config: ConfigType,
    discovery_info: DiscoveryInfoType | None = None,
) -> NotifheureNotificationService | None:
    """Get the Notifheure notification service."""
    if discovery_info is None:
        return None

    entry_id = discovery_info.get("entry_id")
    if entry_id is None:
        _LOGGER.error("No entry_id in discovery_info")
        return None

    panels = hass.data.get(DOMAIN, {}).get(entry_id, [])

    if not panels:
        _LOGGER.warning("Aucun panneau configuré pour Notifheure")

    return NotifheureNotificationService(hass, panels)


class NotifheureNotificationService(BaseNotificationService):
    """Implement the notification service for Notifheure."""

    def __init__(self, hass: HomeAssistant, panels: list[dict[str, str]]) -> None:
        """Initialize the service."""
        self.hass = hass
        self._panels = {p[CONF_PANEL_NAME]: p[CONF_PANEL_TOPIC] for p in panels}
        _LOGGER.info(
            "NotifheureNotificationService initialisé avec: %s",
            list(self._panels.keys()),
        )

    async def async_send_message(self, message: str = "", **kwargs: Any) -> None:
        """Send a message to one or more Notifheure panels."""
        # Récupérer les targets
        targets = kwargs.get(ATTR_TARGET)
        data = kwargs.get(ATTR_DATA, {})

        # Si target est dans data
        if targets is None and ATTR_TARGET in data:
            targets = data.get(ATTR_TARGET)

        # Par défaut: tous les panneaux
        if targets is None:
            targets = list(self._panels.keys())

        # Convertir en liste si string
        if isinstance(targets, str):
            targets = [targets]

        # Construire le payload
        payload_dict = {"msg": message}

        # Ajouter les options si présentes
        options = data.get("options", "")
        if options:
            payload_dict["opt"] = options

        _LOGGER.debug("Envoi du message '%s' vers: %s", message, targets)

        # Envoyer à chaque panneau
        for target in targets:
            topic = self._panels.get(target)
            if not topic:
                _LOGGER.warning(
                    "Panneau inconnu: %s (disponibles: %s)",
                    target,
                    list(self._panels.keys()),
                )
                continue

            payload = json.dumps(payload_dict)

            try:
                await mqtt.async_publish(self.hass, topic, payload, qos=1, retain=False)
                _LOGGER.info("Message envoyé à %s (%s): %s", target, topic, payload)
            except Exception as err:  # pylint: disable=broad-except
                _LOGGER.error("Erreur lors de l'envoi à %s: %s", target, err)

    @property
    def targets(self) -> dict[str, str] | None:
        """Return a dictionary of registered targets."""
        return self._panels if self._panels else None
