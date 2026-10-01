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
    "applications_services": {
        "name": "Aplicaciones y servicios",
        "description": "Servicios web institucionales, APIs, portales, ERP y microservicios.",
    },
    "databases": {
        "name": "Bases de datos",
        "description": "Motores relacionales, pools de conexión, transacciones, réplicas e integridad.",
    },
    "networks_connectivity": {
        "name": "Redes y conectividad",
        "description": "Enlaces WAN, switches, enrutamiento, VLANs, túneles VPN y DNS institucional.",
    },
    "infrastructure_storage": {
        "name": "Infraestructura y almacenamiento",
        "description": "Servidores físicos, virtualización, contenedores, cabinas SAN/NAS, arreglos RAID y copias de seguridad.",
    },
    "security_access": {
        "name": "Seguridad y accesos",
        "description": "Firewall perimetral, certificados SSL/TLS, autenticación LDAP/Keycloak y permisos de acceso.",
    },
}
LABELS = list(CATEGORIES)
VARIANTS_PER_FAMILY = {category: 18 for category in LABELS}

