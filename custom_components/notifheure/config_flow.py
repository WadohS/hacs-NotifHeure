"""Config flow for Notifheure integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .const import CONF_PANEL_NAME, CONF_PANEL_TOPIC, CONF_PANELS, DOMAIN

_LOGGER = logging.getLogger(__name__)


class NotifheureConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Notifheure."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        _LOGGER.warning("🟢 Config flow: Étape user appelée")
        
        try:
            if self._async_current_entries():
                _LOGGER.warning("🟡 Config flow: Instance déjà existante")
                return self.async_abort(reason="single_instance_allowed")

            if user_input is not None:
                _LOGGER.warning("🟢 Config flow: Création de l'entrée")
                return self.async_create_entry(
                    title="Notifheure",
                    data={},
                    options={CONF_PANELS: []},
                )

            _LOGGER.warning("🟢 Config flow: Affichage du formulaire initial")
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema({}),
            )
            
        except Exception as err:
            _LOGGER.error("🔴 Config flow erreur user: %s", err, exc_info=True)
            raise

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> NotifheureOptionsFlowHandler:
        """Get the options flow for this handler."""
        return NotifheureOptionsFlowHandler(config_entry)


class NotifheureOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle Notifheure options."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry
        _LOGGER.warning("🟢 Options flow: Initialisation")

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        _LOGGER.warning("🟢 Options flow: Étape init")
        
        try:
            return self.async_show_menu(
                step_id="init",
                menu_options=["add_panel", "list_panels", "remove_panel"],
            )
        except Exception as err:
            _LOGGER.error("🔴 Options flow erreur init: %s", err, exc_info=True)
            raise

    async def async_step_add_panel(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Add a new panel."""
        _LOGGER.warning("🟢 Options flow: Étape add_panel")
        
        errors = {}

        try:
            if user_input is not None:
                _LOGGER.warning("🟢 Options flow: Traitement input: %s", user_input)
                
                name = str(user_input.get(CONF_PANEL_NAME, "")).strip()
                topic = str(user_input.get(CONF_PANEL_TOPIC, "")).strip()
                
                if not name or not topic:
                    _LOGGER.error("🔴 Options flow: Champs vides")
                    errors["base"] = "invalid_input"
                else:
                    panels = list(self.config_entry.options.get(CONF_PANELS, []))
                    
                    # Vérifier si le nom existe déjà
                    if any(p.get(CONF_PANEL_NAME) == name for p in panels):
                        _LOGGER.warning("🟡 Options flow: Nom déjà existant")
                        errors[CONF_PANEL_NAME] = "name_exists"
                    else:
                        new_panel = {
                            CONF_PANEL_NAME: name,
                            CONF_PANEL_TOPIC: topic,
                        }
                        panels.append(new_panel)
                        
                        _LOGGER.warning("🟢 Ajout du panneau: %s -> %s", name, topic)
                        
                        return self.async_create_entry(title="", data={CONF_PANELS: panels})

            # Afficher le formulaire
            _LOGGER.warning("🟢 Options flow: Affichage formulaire add_panel")
            return self.async_show_form(
                step_id="add_panel",
                data_schema=vol.Schema(
                    {
                        vol.Required(CONF_PANEL_NAME, default=""): str,
                        vol.Required(CONF_PANEL_TOPIC, default=""): str,
                    }
                ),
                errors=errors,
            )
            
        except Exception as err:
            _LOGGER.error("🔴 Options flow erreur add_panel: %s", err, exc_info=True)
            raise

    async def async_step_list_panels(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """List all configured panels."""
        _LOGGER.warning("🟢 Options flow: Étape list_panels")
        
        try:
            panels = list(self.config_entry.options.get(CONF_PANELS, []))

            if not panels:
                _LOGGER.warning("🟡 Options flow: Aucun panneau")
                return self.async_abort(reason="no_panels")

            panel_list = "\n".join(
                f"• {p.get(CONF_PANEL_NAME, 'unknown')}: {p.get(CONF_PANEL_TOPIC, 'unknown')}" 
                for p in panels
            )
            
            _LOGGER.warning("🟢 Options flow: Liste des panneaux:\n%s", panel_list)

            return self.async_show_form(
                step_id="list_panels",
                data_schema=vol.Schema({}),
                description_placeholders={"panels": panel_list},
            )
            
        except Exception as err:
            _LOGGER.error("🔴 Options flow erreur list_panels: %s", err, exc_info=True)
            raise

    async def async_step_remove_panel(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Remove a panel."""
        _LOGGER.warning("🟢 Options flow: Étape remove_panel")
        
        try:
            panels = list(self.config_entry.options.get(CONF_PANELS, []))

            if not panels:
                _LOGGER.warning("🟡 Options flow: Aucun panneau à supprimer")
                return self.async_abort(reason="no_panels")

            if user_input is not None:
                _LOGGER.warning("🟢 Options flow: Suppression input: %s", user_input)
                
                index = int(user_input.get("panel_index", -1))
                
                if 0 <= index < len(panels):
                    removed_panel = panels[index]
                    panels = panels[:index] + panels[index + 1:]
                    
                    _LOGGER.warning("🟢 Suppression du panneau: %s", removed_panel.get(CONF_PANEL_NAME))
                    
                    return self.async_create_entry(title="", data={CONF_PANELS: panels})
                else:
                    _LOGGER.error("🔴 Options flow: Index invalide")
                    return self.async_abort(reason="invalid_index")

            # Créer les options
            panel_options = {}
            for i, p in enumerate(panels):
                panel_options[str(i)] = f"{p.get(CONF_PANEL_NAME, 'unknown')} ({p.get(CONF_PANEL_TOPIC, 'unknown')})"
            
            _LOGGER.warning("🟢 Options flow: Affichage formulaire remove avec %d options", len(panel_options))

            return self.async_show_form(
                step_id="remove_panel",
                data_schema=vol.Schema(
                    {
                        vol.Required("panel_index"): vol.In(panel_options),
                    }
                ),
            )
            
        except Exception as err:
            _LOGGER.error("🔴 Options flow erreur remove_panel: %s", err, exc_info=True)
            raise
