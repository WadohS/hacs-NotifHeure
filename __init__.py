"""Notifheure integration."""
from __future__ import annotations
import logging
from typing import Any
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import Platform
from homeassistant.helpers import device_registry as dr
from .const import DOMAIN
from .notify import NotifheureNotifier
PLATFORMS: list[Platform] = [Platform.NOTIFY]
async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
   """Set up Notifheure from a config entry."""
   hass.data.setdefault(DOMAIN, {})
   # Stocker les panneaux de config
   panels = entry.data.get("panels", [])
   hass.data[DOMAIN][entry.entry_id] = panels
   # Créer un notifier par panneau
   await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
   return True
async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
   """Unload a config entry."""
   if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
       hass.data[DOMAIN].pop(entry.entry_id, None)
   return unload_ok