"""Cálculos de la parcela (sin dependencias de Home Assistant)."""

from __future__ import annotations

from datetime import date
from typing import Any

from .const import (
    CONF_ANO,
    CONF_SISTEMA,
    COBERTURA_POR_SISTEMA,
    CONF_CAUDAL_GOTERO,
    CONF_DIAS_RIEGO,
    CONF_LINEAS,
    CONF_MARCO_ARBOLES,
    CONF_MARCO_FILAS,
    CONF_OLIVOS,
    CONF_SEPARACION_GOTEROS,
    CONF_SUPERFICIE,
)


def _num(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def calcular(cfg: dict[str, Any]) -> dict[str, Any]:
    """Devuelve los datos derivados de la ficha de una parcela."""
    filas = _num(cfg.get(CONF_MARCO_FILAS))
    arboles = _num(cfg.get(CONF_MARCO_ARBOLES))
    sep = _num(cfg.get(CONF_SEPARACION_GOTEROS))
    caudal = _num(cfg.get(CONF_CAUDAL_GOTERO))
    lineas = _num(cfg.get(CONF_LINEAS), 1)
    olivos = int(_num(cfg.get(CONF_OLIVOS)))
    superficie = _num(cfg.get(CONF_SUPERFICIE))
    dias = int(_num(cfg.get(CONF_DIAS_RIEGO)))
    cobertura = COBERTURA_POR_SISTEMA.get(cfg.get(CONF_SISTEMA), 100)
    ano = int(_num(cfg.get(CONF_ANO)))
    edad = date.today().year - ano if 1900 < ano <= date.today().year else None

    m2_arbol = filas * arboles if filas > 0 and arboles > 0 else None
    arboles_ha = round(10000 / m2_arbol) if m2_arbol else None
    goteros_arbol = round(arboles / sep * lineas, 2) if sep > 0 and arboles > 0 else None
    caudal_arbol = round(goteros_arbol * caudal, 2) if goteros_arbol is not None else None
    # Lámina de riego: mm (= L/m²) que se aplican por hora
    mm_hora = (
        round(caudal * lineas / (sep * filas), 3) if sep > 0 and filas > 0 else None
    )

    if olivos > 0:
        olivos_total = olivos
        estimado = False
    elif superficie > 0 and arboles_ha:
        olivos_total = round(superficie * arboles_ha)
        estimado = True
    else:
        olivos_total = None
        estimado = False

    if superficie > 0:
        superficie_total = round(superficie, 2)
    elif olivos > 0 and m2_arbol:
        superficie_total = round(olivos * m2_arbol / 10000, 2)
    else:
        superficie_total = None

    return {
        "m2_arbol": round(m2_arbol, 2) if m2_arbol else None,
        "arboles_ha": arboles_ha,
        "goteros_arbol": goteros_arbol,
        "caudal_arbol": caudal_arbol,
        "mm_hora": mm_hora,
        "olivos_total": olivos_total,
        "olivos_estimado": estimado,
        "superficie_total": superficie_total,
        "dias_riego": dias,
        "cobertura": cobertura,
        "ano_plantacion": ano if ano > 0 else None,
        "edad": edad,
        "litros_semana_por_hora": round(caudal_arbol * dias, 2)
        if caudal_arbol is not None
        else None,
    }
