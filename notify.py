"""Notify platform for Notifheure."""
from __future__ import annotations
import json
import logging
from typing import Any
from homeassistant.components.notify import (
   ATTR_TARGET,
   ATTR_DATA,
   ATTR_TITLE,
   ATTR_MESSAGE,
   BaseNotificationService,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
import homeassistant.components.mqtt as mqtt
from .const import DOMAIN
_LOGGER = logging.getLogger(__name__)
async def async_get_service(
   hass: HomeAssistant,
   config: ConfigType,
   discovery_info: DiscoveryInfoType | None = None,
) -> NotifheureNotifier | None:
   """Get the notification service."""
   entry_id = discovery_info["entry_id"]
   panels = hass.data[DOMAIN][entry_id]
   return NotifheureNotifier(hass, panels)
class NotifheureNotifier(BaseNotificationService):
   """Notifheure notification service."""
   def __init__(self, hass: HomeAssistant, panels: list[dict[str, str]]) -> None:
       """Initialize the notifier."""
       self.hass = hass
       self._panels = {p["name"]: p["topic"] for p in panels}
   async def async_send_message(self, message: str, **kwargs: Any) -> None:
       """Send a message to one or more Notifheure panels."""
       data = kwargs.get(ATTR_DATA) or {}
       targets = data.get(ATTR_TARGET, list(self._panels.keys()))
       if isinstance(targets, str):
           targets = [targets]
       payload_base = {"msg": message}
       options = data.get("options", "")
       if options:
           payload_base["opt"] = options
       for target in targets:
           topic = self._panels.get(target)
           if not topic:
               _LOGGER.warning("Unknown target: %s", target)
               continue
           payload = json.dumps(payload_base)
           await mqtt.async_publish(
               self.hass, topic, payload, qos=1, retain=False
           )
           _LOGGER.debug("Sent to %s: %s", topic, payload)