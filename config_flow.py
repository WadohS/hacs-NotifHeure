"""Config flow for Notifheure."""
import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from .const import DOMAIN, CONF_PANELS, CONF_PANEL_NAME, CONF_PANEL_TOPIC

_LOGGER = logging.getLogger(__name__)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Notifheure config flow."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Get the options flow for this handler."""
        return OptionsFlowHandler(config_entry)

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle a flow initialized by the user."""
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            return self.async_create_entry(
                title="Notifheure",
                data={},
                options={CONF_PANELS: []}
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({}),
            description_placeholders={
                "info": "Configurez vos panneaux Notifheure dans les options apr\Uffffffffl'installation."
            }
        )


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage panels."""
        return self.async_show_menu(
            step_id="init",
            menu_options=["add_panel", "edit_panels", "remove_panel"],
        )

    async def async_step_add_panel(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Add a panel."""
        errors = {}
        
        if user_input is not None:
            # Valider le nom du panneau
            name = user_input[CONF_PANEL_NAME].strip()
            topic = user_input[CONF_PANEL_TOPIC].strip()
            
            panels = list(self.config_entry.options.get(CONF_PANELS, []))
            
            # V\Ufffffffffier si le nom existe d\Uffffffff
            if any(p[CONF_PANEL_NAME] == name for p in panels):
                errors[CONF_PANEL_NAME] = "name_exists"
            else:
                new_panel = {
                    CONF_PANEL_NAME: name,
                    CONF_PANEL_TOPIC: topic,
                }
                panels.append(new_panel)
                
                _LOGGER.info("Ajout du panneau: %s -> %s", name, topic)
                
                return self.async_create_entry(
                    title="",
                    data={CONF_PANELS: panels}
                )

        return self.async_show_form(
            step_id="add_panel",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_PANEL_NAME): selector.TextSelector(
                        selector.TextSelectorConfig(type=selector.TextSelectorType.TEXT)
                    ),
                    vol.Required(CONF_PANEL_TOPIC): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT,
                            multiline=False
                        )
                    ),
                }
            ),
            errors=errors,
            description_placeholders={
                "example": "Exemple: Nom='Salon', Topic='notifheure/salon'"
            }
        )

    async def async_step_edit_panels(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Edit existing panels list."""
        panels = list(self.config_entry.options.get(CONF_PANELS, []))
        
        if not panels:
            return self.async_abort(reason="no_panels")
        
        panel_list = "\n".join(
            f"- {p[CONF_PANEL_NAME]}: {p[CONF_PANEL_TOPIC]}" for p in panels
        )
        
        return self.async_show_form(
            step_id="edit_panels",
            data_schema=vol.Schema({}),
            description_placeholders={"panels": panel_list}
        )

    async def async_step_remove_panel(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Remove a panel."""
        panels = list(self.config_entry.options.get(CONF_PANELS, []))
        
        if not panels:
            return self.async_abort(reason="no_panels")
        
        if user_input is not None:
            index = int(user_input["panel_index"])
            removed_panel = panels[index]
            panels = panels[:index] + panels[index + 1:]
            
            _LOGGER.info("Suppression du panneau: %s", removed_panel[CONF_PANEL_NAME])
            
            return self.async_create_entry(
                title="",
                data={CONF_PANELS: panels}
            )

        options = [
            selector.SelectOptionDict(
                value=str(i),
                label=f"{panel[CONF_PANEL_NAME]} ({panel[CONF_PANEL_TOPIC]})"
            )
            for i, panel in enumerate(panels)
        ]

        return self.async_show_form(
            step_id="remove_panel",
            data_schema=vol.Schema(
                {
                    vol.Required("panel_index"): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=options,
                            mode=selector.SelectSelectorMode.DROPDOWN
                        )
                    ),
                }
            ),
        )
