"""Constantes de la integración Olivar."""

DOMAIN = "olivar"

CONF_NOMBRE = "nombre"
CONF_VARIEDAD = "variedad"
CONF_SISTEMA = "sistema"
CONF_MARCO_FILAS = "marco_filas"
CONF_MARCO_ARBOLES = "marco_arboles"
CONF_OLIVOS = "olivos"
CONF_SUPERFICIE = "superficie_ha"
CONF_DIAS_RIEGO = "dias_riego"
CONF_CAUDAL_GOTERO = "caudal_gotero"
CONF_SEPARACION_GOTEROS = "separacion_goteros"
CONF_LINEAS = "lineas_por_fila"
CONF_COBERTURA = "cobertura"
CONF_ANO = "ano_plantacion"
CONF_NOTAS = "notas"

VARIEDADES = [
    "Picual",
    "Sikitita",
    "Sikitita 1",
    "Sikitita 2",
    "Arbequina",
    "Arbosana",
    "Koroneiki",
    "Hojiblanca",
    "Cornicabra",
    "Manzanilla",
    "Otra",
]

SISTEMAS = ["Tradicional", "Intensivo", "Superintensivo"]

# Cobertura de copa por defecto (% del suelo que sombrea la copa)
COBERTURA_POR_SISTEMA = {"Tradicional": 40, "Intensivo": 65, "Superintensivo": 100}

DEFAULTS = {
    CONF_VARIEDAD: "Picual",
    CONF_SISTEMA: "Intensivo",
    CONF_MARCO_FILAS: 5.0,
    CONF_MARCO_ARBOLES: 5.0,
    CONF_OLIVOS: 0,
    CONF_SUPERFICIE: 0.0,
    CONF_DIAS_RIEGO: 2,
    CONF_CAUDAL_GOTERO: 1.6,
    CONF_SEPARACION_GOTEROS: 1.0,
    CONF_LINEAS: 1,
    CONF_ANO: 0,
}
