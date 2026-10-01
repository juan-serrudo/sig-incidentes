"""Paths, category definitions and choices made before evaluation."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
ARTIFACT_DIR = ROOT / "artifacts"
FRONTEND_DIR = ROOT / "frontend"
SEED = 42
MIN_ACCEPTED_ACCURACY = 0.90
MIN_ACCEPTED_CASES = 20
CATEGORIES = {
    "access": {"name": "Accesos y permisos", "description": "Credenciales, cuentas bloqueadas y autorización de acceso."},
    "network": {"name": "Red y conectividad", "description": "Conexión a internet, red local, wifi y VPN."},
    "hardware": {"name": "Equipos y periféricos", "description": "Componentes físicos, pantallas, impresoras y accesorios."},
    "software": {"name": "Aplicaciones", "description": "Errores de ejecución, instalación o funcionamiento de programas."},
    "email": {"name": "Correo electrónico", "description": "Envío, recepción, buzón y configuración de mensajes."},
}
LABELS = list(CATEGORIES)
VARIANTS_PER_FAMILY = {"access": 24, "network": 20, "hardware": 16, "software": 18, "email": 14}

