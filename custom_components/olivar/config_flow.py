"""Formularios para añadir y editar parcelas del olivar."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import (
    CONF_CAUDAL_GOTERO,
    CONF_ANO,
    CONF_DIAS_RIEGO,
    CONF_LINEAS,
    CONF_MARCO_ARBOLES,
    CONF_MARCO_FILAS,
    CONF_NOMBRE,
    CONF_OLIVOS,
    CONF_SEPARACION_GOTEROS,
    CONF_SISTEMA,
    CONF_SUPERFICIE,
    CONF_VARIEDAD,
    DEFAULTS,
    DOMAIN,
    SISTEMAS,
    VARIEDADES,
)


def _number(min_v: float, max_v: float, step: float, unit: str | None = None):
    cfg: dict[str, Any] = {
        "min": min_v,
        "max": max_v,
        "step": step,
        "mode": selector.NumberSelectorMode.BOX,
    }
    if unit:
        cfg["unit_of_measurement"] = unit
    return selector.NumberSelector(selector.NumberSelectorConfig(**cfg))


def _schema(d: dict[str, Any], con_nombre: bool = True) -> vol.Schema:
    campos: dict[Any, Any] = {}
    if con_nombre:
        campos[vol.Required(CONF_NOMBRE, default=d.get(CONF_NOMBRE, ""))] = (
            selector.TextSelector()
        )
    campos.update(
        {
            vol.Required(CONF_VARIEDAD, default=d[CONF_VARIEDAD]): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=VARIEDADES,
                    custom_value=True,
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            ),
            vol.Required(CONF_SISTEMA, default=d[CONF_SISTEMA]): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=SISTEMAS, mode=selector.SelectSelectorMode.DROPDOWN
                )
            ),
            vol.Required(CONF_MARCO_FILAS, default=d[CONF_MARCO_FILAS]): _number(
                0.5, 30, 0.1, "m"
            ),
            vol.Required(CONF_MARCO_ARBOLES, default=d[CONF_MARCO_ARBOLES]): _number(
                0.5, 30, 0.1, "m"
            ),
            vol.Optional(CONF_OLIVOS, default=d[CONF_OLIVOS]): _number(
                0, 100000, 1, "olivos"
            ),
            vol.Optional(CONF_SUPERFICIE, default=d[CONF_SUPERFICIE]): _number(
                0, 1000, 0.01, "ha"
            ),
            vol.Required(CONF_DIAS_RIEGO, default=d[CONF_DIAS_RIEGO]): _number(
                0, 7, 1, "días/semana"
            ),
            vol.Required(CONF_CAUDAL_GOTERO, default=d[CONF_CAUDAL_GOTERO]): _number(
                0, 50, 0.1, "L/h"
            ),
            vol.Required(
                CONF_SEPARACION_GOTEROS, default=d[CONF_SEPARACION_GOTEROS]
            ): _number(0.1, 10, 0.05, "m"),
            vol.Required(CONF_LINEAS, default=d[CONF_LINEAS]): _number(
                1, 4, 1, "líneas"
            ),
            vol.Optional(CONF_ANO, default=d[CONF_ANO]): _number(
                0, 2100, 1, None
            ),
        }
    )
    return vol.Schema(campos)


def _limpiar(datos: dict[str, Any]) -> dict[str, Any]:
    """Convierte los números enteros que el formulario devuelve como float."""
    out = dict(datos)
    for k in (CONF_OLIVOS, CONF_DIAS_RIEGO, CONF_LINEAS, CONF_ANO):
        if k in out and out[k] is not None:
            out[k] = int(out[k])
    if CONF_NOMBRE in out:
        out[CONF_NOMBRE] = str(out[CONF_NOMBRE]).strip()
    return out


class OlivarConfigFlow(ConfigFlow, domain=DOMAIN):
    """Añadir una parcela."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            datos = _limpiar(user_input)
            if not datos[CONF_NOMBRE]:
                errors[CONF_NOMBRE] = "nombre_vacio"
            else:
                await self.async_set_unique_id(datos[CONF_NOMBRE].lower())
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title=datos[CONF_NOMBRE], data=datos)
        valores = {**DEFAULTS, **(user_input or {})}
        return self.async_show_form(
            step_id="user", data_schema=_schema(valores), errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        return OlivarOptionsFlow()


class OlivarOptionsFlow(OptionsFlow):
    """Editar la ficha de una parcela."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if user_input is not None:
            return self.async_create_entry(data=_limpiar(user_input))
        actual = {**DEFAULTS, **self.config_entry.data, **self.config_entry.options}
        return self.async_show_form(
            step_id="init", data_schema=_schema(actual, con_nombre=False)
        )
