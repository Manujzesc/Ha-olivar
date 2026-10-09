"""Sensores de cada parcela del olivar."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .calc import calcular
from .const import (
    CONF_MARCO_ARBOLES,
    CONF_MARCO_FILAS,
    CONF_NOMBRE,
    CONF_NOTAS,
    CONF_SISTEMA,
    CONF_VARIEDAD,
    DEFAULTS,
    DOMAIN,
)


def _fmt(n: Any) -> str:
    """5.0 -> '5', 1.5 -> '1,5'."""
    try:
        f = float(n)
    except (TypeError, ValueError):
        return "?"
    s = f"{f:g}"
    return s.replace(".", ",")


@dataclass(frozen=True, kw_only=True)
class OlivarSensorDescription(SensorEntityDescription):
    """Descripción de un sensor de parcela."""

    value_fn: Callable[[dict[str, Any], dict[str, Any]], Any]


SENSORES: tuple[OlivarSensorDescription, ...] = (
    OlivarSensorDescription(
        key="ficha",
        translation_key="ficha",
        icon="mdi:tree",
        value_fn=lambda cfg, c: cfg.get(CONF_VARIEDAD),
    ),
    OlivarSensorDescription(
        key="marco",
        translation_key="marco",
        icon="mdi:grid",
        value_fn=lambda cfg, c: f"{_fmt(cfg.get(CONF_MARCO_FILAS))}x{_fmt(cfg.get(CONF_MARCO_ARBOLES))}",
    ),
    OlivarSensorDescription(
        key="olivos",
        translation_key="olivos",
        icon="mdi:pine-tree",
        native_unit_of_measurement="olivos",
        value_fn=lambda cfg, c: c["olivos_total"],
    ),
    OlivarSensorDescription(
        key="superficie",
        translation_key="superficie",
        icon="mdi:texture-box",
        native_unit_of_measurement="ha",
        value_fn=lambda cfg, c: c["superficie_total"],
    ),
    OlivarSensorDescription(
        key="arboles_ha",
        translation_key="arboles_ha",
        icon="mdi:forest",
        native_unit_of_measurement="árboles/ha",
        value_fn=lambda cfg, c: c["arboles_ha"],
    ),
    OlivarSensorDescription(
        key="dias_riego",
        translation_key="dias_riego",
        icon="mdi:calendar-week",
        native_unit_of_measurement="días/semana",
        value_fn=lambda cfg, c: c["dias_riego"],
    ),
    OlivarSensorDescription(
        key="goteros_arbol",
        translation_key="goteros_arbol",
        icon="mdi:water-outline",
        native_unit_of_measurement="goteros",
        value_fn=lambda cfg, c: c["goteros_arbol"],
    ),
    OlivarSensorDescription(
        key="caudal_arbol",
        translation_key="caudal_arbol",
        icon="mdi:water-pump",
        native_unit_of_measurement="L/h",
        value_fn=lambda cfg, c: c["caudal_arbol"],
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Crear los sensores de la parcela."""
    cfg = {**DEFAULTS, **entry.data, **entry.options}
    datos = calcular(cfg)
    device = DeviceInfo(
        identifiers={(DOMAIN, entry.entry_id)},
        name=entry.title,
        manufacturer="Olivar",
        model=f"{cfg.get(CONF_SISTEMA)} · {cfg.get(CONF_VARIEDAD)}",
    )
    async_add_entities(
        OlivarSensor(entry, desc, cfg, datos, device) for desc in SENSORES
    )


class OlivarSensor(SensorEntity):
    """Un dato de la ficha de la parcela."""

    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(
        self,
        entry: ConfigEntry,
        description: OlivarSensorDescription,
        cfg: dict[str, Any],
        datos: dict[str, Any],
        device: DeviceInfo,
    ) -> None:
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = device
        self._attr_native_value = description.value_fn(cfg, datos)
        if description.key == "ficha":
            atributos = {k: v for k, v in cfg.items() if k != CONF_NOMBRE}
            atributos.update(datos)
            atributos["parcela"] = entry.title
            if not cfg.get(CONF_NOTAS):
                atributos.pop(CONF_NOTAS, None)
            self._attr_extra_state_attributes = atributos
