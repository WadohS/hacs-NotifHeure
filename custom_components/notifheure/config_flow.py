"""Config flow for Notifheure integration."""
import logging
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from .const import DOMAIN, CONF_PANELS, CONF_PANEL_NAME, CONF_PANEL_TOPIC

_LOGGER = logging.getLogger(__name__)

class NotifheureConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Gère le flux de configuration Notifheure."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Étape de configuration initiale."""
        _LOGGER.warning("🟢 Config flow: Étape user appelée")

        # Une seule instance autorisée
        if self._async_current_entries():
            _LOGGER.warning("🟡 Config flow: Instance déjà existante, abandon")
            return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            _LOGGER.warning("🟢 Config flow: Création de l'entrée")
            return self.async_create_entry(
                title="Notifheure",
                data={},
                options={CONF_PANELS: []}
            )

        _LOGGER.warning("🟢 Config flow: Affichage du formulaire initial")
        return self.async_show_form(
            step_id="user",
            description_placeholders={
                "name": "Notifheure Configuration"
            }
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Retourne le gestionnaire d'options."""
        _LOGGER.warning("🟢 Options flow: Création du gestionnaire")
        return NotifheureOptionsFlowHandler(config_entry)


class NotifheureOptionsFlowHandler(config_entries.OptionsFlow):
    """Gère les options de Notifheure - VERSION CORRIGÉE."""

    def __init__(self, config_entry):
        """Initialise le gestionnaire d'options."""
        _LOGGER.warning("🟢 Options: Initialisation")
        # ✅ CORRECTION: Ne PAS définir self.config_entry (propriété read-only)
        # On utilise un attribut privé au lieu de modifier la propriété read-only
        self._config_entry = config_entry
        _LOGGER.warning(f"🟢 Options: Entry ID = {config_entry.entry_id}")

    async def async_step_init(self, user_input=None):
        """Gère l'étape initiale des options."""
        _LOGGER.warning("🟢 Options flow: Étape init appelée")
        return await self.async_step_manage_panels()

    async def async_step_manage_panels(self, user_input=None):
        """Gère l'ajout et la suppression de panneaux."""
        _LOGGER.warning("🟢 Options flow: Étape manage_panels appelée")
        
        panels = self._config_entry.options.get(CONF_PANELS, [])
        _LOGGER.warning(f"🟢 Options flow: {len(panels)} panneau(x) existant(s)")

        if user_input is not None:
            _LOGGER.warning("🟢 Options flow: Traitement du choix utilisateur")
            
            if user_input.get("action") == "add":
                _LOGGER.warning("🟢 Options flow: Redirection vers add_panel")
                return await self.async_step_add_panel()
            
            elif user_input.get("action") == "remove":
                _LOGGER.warning("🟢 Options flow: Redirection vers remove_panel")
                return await self.async_step_remove_panel()
            
            elif user_input.get("action") == "done":
                _LOGGER.warning("🟢 Options flow: Configuration terminée")
                return self.async_create_entry(title="", data=self._config_entry.options)

        # Menu de gestion des panneaux
        _LOGGER.warning("🟢 Options flow: Affichage du menu de gestion")
        return self.async_show_form(
            step_id="manage_panels",
            data_schema=vol.Schema({
                vol.Required("action", default="add"): vol.In({
                    "add": "➕ Ajouter un panneau",
                    "remove": "🗑️ Supprimer un panneau",
                    "done": "✅ Terminer"
                })
            }),
            description_placeholders={
                "panels_count": str(len(panels)),
                "panels_list": ", ".join([p[CONF_PANEL_NAME] for p in panels]) or "Aucun panneau"
            }
        )

    async def async_step_add_panel(self, user_input=None):
        """Ajoute un nouveau panneau."""
        _LOGGER.warning("🟢 Options flow: Étape add_panel appelée")
        
        if user_input is not None:
            _LOGGER.warning(f"🟢 Options flow: Ajout du panneau '{user_input[CONF_PANEL_NAME]}'")
            
            panels = list(self._config_entry.options.get(CONF_PANELS, []))
            
            # Vérifie si le panneau existe déjà
            if any(p[CONF_PANEL_NAME] == user_input[CONF_PANEL_NAME] for p in panels):
                _LOGGER.warning(f"🟡 Options flow: Panneau '{user_input[CONF_PANEL_NAME]}' existe déjà")
                return self.async_show_form(
                    step_id="add_panel",
                    data_schema=vol.Schema({
                        vol.Required(CONF_PANEL_NAME, default=""): str,
                        vol.Required(CONF_PANEL_TOPIC, default="notifheure/"): str,
                    }),
                    errors={"base": "panel_exists"}
                )
            
            # Ajoute le nouveau panneau
            panels.append({
                CONF_PANEL_NAME: user_input[CONF_PANEL_NAME],
                CONF_PANEL_TOPIC: user_input[CONF_PANEL_TOPIC]
            })
            
            _LOGGER.warning(f"🟢 Options flow: Panneau ajouté, total = {len(panels)}")
            
            # Sauvegarde les options
            new_options = {**self._config_entry.options, CONF_PANELS: panels}
            self.hass.config_entries.async_update_entry(
                self._config_entry, options=new_options
            )
            
            _LOGGER.warning("🟢 Options flow: Retour au menu de gestion")
            return await self.async_step_manage_panels()

        # Affiche le formulaire d'ajout
        _LOGGER.warning("🟢 Options flow: Affichage du formulaire d'ajout")
        return self.async_show_form(
            step_id="add_panel",
            data_schema=vol.Schema({
                vol.Required(CONF_PANEL_NAME, default=""): str,
                vol.Required(CONF_PANEL_TOPIC, default="notifheure/"): str,
            }),
            description_placeholders={
                "example_name": "salon",
                "example_topic": "notifheure/salon"
            }
        )

    async def async_step_remove_panel(self, user_input=None):
        """Supprime un panneau existant."""
        _LOGGER.warning("🟢 Options flow: Étape remove_panel appelée")
        
        panels = list(self._config_entry.options.get(CONF_PANELS, []))
        
        if not panels:
            _LOGGER.warning("🟡 Options flow: Aucun panneau à supprimer")
            return await self.async_step_manage_panels()
        
        if user_input is not None:
            _LOGGER.warning(f"🟢 Options flow: Suppression du panneau '{user_input['panel_to_remove']}'")
            
            # Supprime le panneau
            panels = [p for p in panels if p[CONF_PANEL_NAME] != user_input["panel_to_remove"]]
            
            _LOGGER.warning(f"🟢 Options flow: Panneau supprimé, reste = {len(panels)}")
            
            # Sauvegarde les options
            new_options = {**self._config_entry.options, CONF_PANELS: panels}
            self.hass.config_entries.async_update_entry(
                self._config_entry, options=new_options
            )
            
            return await self.async_step_manage_panels()

        # Affiche le formulaire de suppression
        _LOGGER.warning("🟢 Options flow: Affichage du formulaire de suppression")
        panel_choices = {p[CONF_PANEL_NAME]: p[CONF_PANEL_NAME] for p in panels}
        
        return self.async_show_form(
            step_id="remove_panel",
            data_schema=vol.Schema({
                vol.Required("panel_to_remove"): vol.In(panel_choices)
            })
        )
