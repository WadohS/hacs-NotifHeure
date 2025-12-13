"""Notify platform for Notifheure."""
from __future__ import annotations

import json
import logging
from typing import Any, cast

import voluptuous as vol
from homeassistant.components import mqtt
from homeassistant.components.notify import (
    ATTR_DATA,
    ATTR_MESSAGE,
    ATTR_TARGET,
    ATTR_TITLE,
    BaseNotificationService,
    PLATFORM_SCHEMA,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv, discovery
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .const import CONF_PANELS, CONF_PANEL_NAME, CONF_PANEL_TOPIC, DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({})

async def async_get_service(
    hass: HomeAssistant,
    config: ConfigType,
    discovery_info: DiscoveryInfoType | None = None,
) -> NotifheureNotifier | None:
    """Get the notification service."""
    if discovery_info is None:
        return None
    
    entry_id = discovery_info["entry_id"]
    panels = hass.data[DOMAIN].get(entry_id, [])
    return NotifheureNotifier(hass, panels)

class NotifheureNotifier(BaseNotificationService):
    """Notifheure notification service."""

    def __init__(self, hass: HomeAssistant, panels: list[dict[str, str]]) -> None:
        """Initialize the notifier."""
        self.hass = hass
        self._panels = {p[CONF_PANEL_NAME]: p[CONF_PANEL_TOPIC] for p in panels}

    async def async_send_message(self, message: str = "", **kwargs: Any) -> None:
        """Send a message to one or more Notifheure panels."""
        data = kwargs.get(ATTR_DATA) or {}
        targets = data.get(ATTR_TARGET, list(self._panels.keys()))
        
        if isinstance(targets, str):
            targets = [targets]

        payload_base = {"msg": message}
        options = data.get("options", "")
        if options:
            payload_base["opt"] = options

        payload = json.dumps(payload_base)
        
        for target in targets:
            topic = self._panels.get(target)
            if not topic:
                _LOGGER.warning("Unknown Notifheure target: %s", target)
                continue

            await mqtt.async_publish(
                self.hass, 
                topic, 
                payload, 
                qos=1, 
                retain=False
            )
            _LOGGER.debug("Sent to %s (%s): %s", target, topic, payload)

