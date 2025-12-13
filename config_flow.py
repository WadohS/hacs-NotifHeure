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
       return self.async_create_entry(title="Notifheure", data={})
class OptionsFlowHandler(config_entries.OptionsFlow):
   """Handle options."""
   def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
       """Initialize options flow."""
       self.config_entry = config_entry
       self.panels = self.config_entry.options.get(CONF_PANELS, [])
   async def async_step_init(
       self, user_input: dict[str, Any] | None = None
   ) -> FlowResult:
       """Manage panels."""
       return self.async_show_menu(
           step_id="init",
           menu_options=[
               "add_panel",
               "remove_panel",
           ],
       )
   async def async_step_add_panel(
       self, user_input: dict[str, Any] | None = None
   ) -> FlowResult:
       """Add a panel."""
       if user_input is not None:
           new_panel = {
               CONF_PANEL_NAME: user_input[CONF_PANEL_NAME],
               CONF_PANEL_TOPIC: user_input[CONF_PANEL_TOPIC],
           }
           panels = self.panels + [new_panel]
           return self.async_create_entry(title="", data={CONF_PANELS: panels})
       return self.async_show_form(
           step_id="add_panel",
           data_schema=vol.Schema(
               {
                   vol.Required(CONF_PANEL_NAME): selector.TextSelector(),
                   vol.Required(CONF_PANEL_TOPIC): selector.TextSelector(
                       text={"multiline": False}
                   ),
               }
           ),
       )
   async def async_step_remove_panel(
       self, user_input: dict[str, Any] | None = None
   ) -> FlowResult:
       """Remove a panel."""
       if user_input is not None:
           index = int(user_input["panel_index"])
           panels = self.panels[:index] + self.panels[index + 1 :]
           return self.async_create_entry(title="", data={CONF_PANELS: panels})
       selectors = []
       for i, panel in enumerate(self.panels):
           selectors.append(
               selector.SelectOptionDict(
                   value=str(i), label=f"{panel[CONF_PANEL_NAME]} ({panel[CONF_PANEL_TOPIC]})"
               )
           )
       return self.async_show_form(
           step_id="remove_panel",
           data_schema=vol.Schema(
               {
                   vol.Required("panel_index"): selector.SelectSelector(
                       selector={"options": selectors}
                   ),
               }
           ),
       )