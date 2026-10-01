"""Fixed keyword rules, written before evaluating the model."""

from app.settings import LABELS
from app.text import normalize_text

KEYWORDS = {
    "access": ["contrasena", "clave", "usuario", "credenciales", "permiso", "permisos", "sesion", "cuenta"],
    "network": ["wifi", "internet", "vpn", "ethernet", "router", "dns", "conexion", "red"],
    "hardware": ["teclado", "monitor", "raton", "mouse", "bateria", "impresora", "ventilador", "cargador"],
    "software": ["programa", "aplicacion", "instalador", "software", "licencia", "formula", "planilla", "actualizacion"],
    "email": ["correo", "buzon", "destinatario", "spam", "adjuntos", "firma", "mensajes", "bandeja"],
}


def rule_prediction(message, fallback):
    normalized = f" {normalize_text(message)} "
    matches = {category: [word for word in KEYWORDS[category] if f" {word} " in normalized] for category in LABELS}
    winner = max(LABELS, key=lambda category: len(matches[category]))
    return {"category": winner if matches[winner] else fallback, "matches": matches, "used_fallback": not bool(matches[winner])}

