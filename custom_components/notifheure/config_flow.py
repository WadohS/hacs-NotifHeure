"""Config flow for Notifheure integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from .const import CONF_PANEL_NAME, CONF_PANEL_TOPIC, CONF_PANELS, DOMAIN

_LOGGER = logging.getLogger(__name__)


class NotifheureConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Notifheure."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            return self.async_create_entry(
                title="Notifheure",
                data={},
                options={CONF_PANELS: []},
            )

        return self.async_show_form(step_id="user")

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

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        return self.async_show_menu(
            step_id="init",
            menu_options=["add_panel", "list_panels", "remove_panel"],
        )

    async def async_step_add_panel(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Add a new panel."""
        errors = {}

        if user_input is not None:
            name = user_input[CONF_PANEL_NAME].strip()
            topic = user_input[CONF_PANEL_TOPIC].strip()

            panels = list(self.config_entry.options.get(CONF_PANELS, []))

            # Vérifier si le nom existe déjà
            if any(p[CONF_PANEL_NAME] == name for p in panels):
                errors[CONF_PANEL_NAME] = "name_exists"
            else:
                new_panel = {
                    CONF_PANEL_NAME: name,
                    CONF_PANEL_TOPIC: topic,
                }
                panels.append(new_panel)

                _LOGGER.info("Ajout du panneau: %s -> %s", name, topic)

                return self.async_create_entry(title="", data={CONF_PANELS: panels})

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
                        )
                    ),
                }
            ),
            errors=errors,
        )

    async def async_step_list_panels(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """List all configured panels."""
        panels = list(self.config_entry.options.get(CONF_PANELS, []))

        if not panels:
            return self.async_abort(reason="no_panels")

        panel_list = "\n".join(
            f"• {p[CONF_PANEL_NAME]}: {p[CONF_PANEL_TOPIC]}" for p in panels
        )

        return self.async_show_form(
            step_id="list_panels",
            description_placeholders={"panels": panel_list},
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
            panels = panels[:index] + panels[index + 1 :]

            _LOGGER.info("Suppression du panneau: %s", removed_panel[CONF_PANEL_NAME])

            return self.async_create_entry(title="", data={CONF_PANELS: panels})

        options = [
            selector.SelectOptionDict(
                value=str(i),
                label=f"{panel[CONF_PANEL_NAME]} ({panel[CONF_PANEL_TOPIC]})",
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
                            mode=selector.SelectSelectorMode.DROPDOWN,
                        )
                    ),
                }
            ),
        )
