"""Fixed keyword rules for UOIT incident categories as heuristic reference."""

from app.settings import LABELS
from app.text import normalize_text

KEYWORDS = {
    "applications_services": [
        "portal", "web", "api", "microservicio", "microservicios", "endpoint",
        "erp", "tomcat", "cola", "rabbitmq", "mensajeria", "batch", "despliegue",
    ],
    "databases": [
        "postgresql", "mysql", "oracle", "database", "datos", "pool", "deadlock",
        "transaccion", "transacciones", "replica", "tablespace", "wal", "pgbouncer",
    ],
    "networks_connectivity": [
        "enlace", "wan", "fibra", "bgp", "ospf", "switch", "switches", "broadcast",
        "dns", "vpn", "ipsec", "wifi", "vlan", "gateway", "enrutador", "enrutamiento",
    ],
    "infrastructure_storage": [
        "hipervisor", "virtualizacion", "esxi", "proxmox", "vmware", "raid", "disco",
        "discos", "backup", "respaldo", "san", "nas", "lun", "datastore", "snapshot",
    ],
    "security_access": [
        "certificado", "ssl", "tls", "https", "ldap", "directorio", "activo",
        "firewall", "keycloak", "sso", "ssh", "ids", "edr", "rbac", "permisos", "autenticacion",
    ],
}


def rule_prediction(text, fallback):
    normalized = f" {normalize_text(text)} "
    matches = {
        category: [word for word in KEYWORDS[category] if f" {word} " in normalized]
        for category in LABELS
    }
    winner = max(LABELS, key=lambda category: len(matches[category]))
    return {
        "category": winner if matches[winner] else fallback,
        "matches": matches,
        "used_fallback": not bool(matches[winner]),
    }
