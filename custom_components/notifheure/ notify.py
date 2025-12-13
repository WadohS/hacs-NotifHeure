"""Notify platform for Notifheure."""
from __future__ import annotations

import json
import logging
from typing import Any

from homeassistant.components.notify import (
    ATTR_TARGET,
    ATTR_DATA,
    BaseNotificationService,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.components import mqtt

from .const import DOMAIN, CONF_PANEL_NAME, CONF_PANEL_TOPIC

_LOGGER = logging.getLogger(__name__)


async def async_get_service(
    hass: HomeAssistant,
    config: ConfigType,
    discovery_info: DiscoveryInfoType | None = None,
) -> NotifheureNotifier | None:
    """Get the notification service."""
    if discovery_info is None:
        return None
    
    entry_id = discovery_info.get("entry_id")
    if entry_id is None:
        _LOGGER.error("No entry_id in discovery_info")
        return None
    
    panels = hass.data.get(DOMAIN, {}).get(entry_id, [])
    
    if not panels:
        _LOGGER.warning("Aucun panneau configur\Uffffffffour Notifheure")
    
    return NotifheureNotifier(hass, panels)


class NotifheureNotifier(BaseNotificationService):
    """Notifheure notification service."""

    def __init__(self, hass: HomeAssistant, panels: list[dict[str, str]]) -> None:
        """Initialize the notifier."""
        self.hass = hass
        self._panels = {p[CONF_PANEL_NAME]: p[CONF_PANEL_TOPIC] for p in panels}
        _LOGGER.info("NotifheureNotifier initialis\Uffffffffvec les panneaux: %s", list(self._panels.keys()))

    async def async_send_message(self, message: str = "", **kwargs: Any) -> None:
        """Send a message to one or more Notifheure panels."""
        # R\Uffffffffp\Uffffffffr les targets
        targets = kwargs.get(ATTR_TARGET)
        data = kwargs.get(ATTR_DATA, {})
        
        # Si target est dans data (comme dans votre exemple)
        if targets is None and ATTR_TARGET in data:
            targets = data.get(ATTR_TARGET)
        
        # Par d\Uffffffffut, envoyer \Uffffffffous les panneaux
        if targets is None:
            targets = list(self._panels.keys())
        
        # Convertir en liste si string
        if isinstance(targets, str):
            targets = [targets]
        
        # Construire le payload de base
        payload_base = {"msg": message}
        
        # Ajouter les options si pr\Uffffffffntes
        options = data.get("options", "")
        if options:
            payload_base["opt"] = options
        
        _LOGGER.debug("Envoi du message '%s' vers les cibles: %s", message, targets)
        
        # Envoyer \Uffffffffhaque panneau
        for target in targets:
            topic = self._panels.get(target)
            if not topic:
                _LOGGER.warning("Panneau inconnu: %s (panneaux disponibles: %s)", 
                              target, list(self._panels.keys()))
                continue
            
            payload = json.dumps(payload_base)
            
            try:
                await mqtt.async_publish(
                    self.hass, topic, payload, qos=1, retain=False
                )
                _LOGGER.info("Message envoy\Uffffffff %s (%s): %s", target, topic, payload)
            except Exception as err:
                _LOGGER.error("Erreur lors de l'envoi \Uffffffffs: %s", target, err)

    @property
    def targets(self) -> dict[str, str] | None:
        """Return a dictionary of registered targets."""
        return self._panels
