
"""Notifheure integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv

from .const import CONF_PANELS, DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.NOTIFY]

CONFIG_SCHEMA = cv.DEP_CONFIG

async def async_setup(hass: HomeAssistant, config: dict[str, Any]) -> bool:
    """Set up the Notifheure component from configuration.yaml (legacy)."""
    # Support YAML config pour compatibilité
    _LOGGER.warning(
        "YAML configuration for Notifheure is deprecated. "
        "Please use the UI instead."
    )
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Notifheure from a config entry."""
    _LOGGER.debug("Setting up Notifheure entry: %s", entry.entry_id)
    
    # Migration options -> data si besoin (pour updates futurs)
    if entry.options:
        hass.config_entries.async_update_entry(entry, data=entry.options)
    
    # Stocker les panneaux dans hass.data
    hass.data.setdefault(DOMAIN, {})
    panels = entry.data.get(CONF_PANELS, [])
    hass.data[DOMAIN][entry.entry_id] = panels
    
    _LOGGER.info(
        "Notifheure loaded with %d panels: %s",
        len(panels),
        [p["name"] for p in panels]
    )
    
    # Forward vers plateforme notify
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.debug("Unloading Notifheure entry: %s", entry.entry_id)
    
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id, None)
    
    return unload_ok

async def async_migrate_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Migrate old entry."""
    _LOGGER.debug("Migrating Notifheure entry: %s", config_entry.version)
    
    # Migration future si besoin
    if config_entry.version == 1:
        new_data = dict(config_entry.data)
        config_entry.version = 2
        hass.config_entries.async_update_entry(config_entry, data=new_data)
    
    return True
