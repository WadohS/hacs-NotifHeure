"""Notifheure integration."""
from __future__ import annotations
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import Platform

from .const import DOMAIN, CONF_PANELS

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.NOTIFY]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Notifheure from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    
    # R\Uffffffffp\Uffffffffr les panneaux depuis les options (ou data en fallback)
    panels = entry.options.get(CONF_PANELS, entry.data.get(CONF_PANELS, []))
    
    # Stocker les panneaux
    hass.data[DOMAIN][entry.entry_id] = panels
    
    _LOGGER.info("Configuration Notifheure avec %d panneau(x)", len(panels))
    
    # Configurer les plateformes
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    # \Uffffffffouter les mises \Uffffffffour des options
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id, None)
        _LOGGER.info("Notifheure d\Uffffffffarg\Uffffffffvec succ\Uffffffff)
    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry when options are updated."""
    await hass.config_entries.async_reload(entry.entry_id)
