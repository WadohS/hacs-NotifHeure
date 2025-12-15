"""Notifheure integration."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import CONF_PANELS, DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.NOTIFY]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Notifheure from a config entry."""
    _LOGGER.warning("🟢 Notifheure: Démarrage de l'intégration")
    
    try:
        # Récupérer les panneaux depuis options ou data
        panels = entry.options.get(CONF_PANELS, entry.data.get(CONF_PANELS, []))
        
        # Stocker les panneaux dans hass.data
        hass.data.setdefault(DOMAIN, {})
        hass.data[DOMAIN][entry.entry_id] = panels
        
        _LOGGER.warning(
            "🟢 Notifheure chargé avec %d panneau(x): %s",
            len(panels),
            [p.get("name", "unknown") for p in panels]
        )
        
        # Forward vers plateforme notify
        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
        
        # Écouter les mises à jour d'options
        entry.async_on_unload(entry.add_update_listener(async_reload_entry))
        
        return True
        
    except Exception as err:
        _LOGGER.error("🔴 Erreur lors du setup: %s", err, exc_info=True)
        return False


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.warning("🔴 Notifheure: Déchargement de l'intégration")
    
    try:
        unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
        
        if unload_ok:
            hass.data[DOMAIN].pop(entry.entry_id, None)
        
        return unload_ok
        
    except Exception as err:
        _LOGGER.error("🔴 Erreur lors du unload: %s", err, exc_info=True)
        return False


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry when options change."""
    _LOGGER.warning("🔄 Notifheure: Rechargement de la configuration")
    await hass.config_entries.async_reload(entry.entry_id)
