import re

from src.contrat import Evenement

_SECRET_RE = re.compile(
    r"(password|passwd|token|secret|api_key|apikey)(\s*[=:]\s*)([^\s&,;]+)",
    re.IGNORECASE,
)

_SEVERITES_LOG = {
    "CRITICAL": "CRITICAL",
    "FATAL": "CRITICAL",
    "ERROR": "HIGH",
    "WARN": "MEDIUM",
    "WARNING": "MEDIUM",
}


def _verifier_cles(rapport: dict, cles: tuple) -> None:
    manquantes = [c for c in cles if c not in rapport]
    if manquantes:
        raise ValueError(f"Cle(s) manquante(s) : {', '.join(manquantes)}")


def masquer_secrets(texte: str) -> str:
    """Remplace la valeur des secrets par [SECRET] (casse ignoree)."""
    return _SECRET_RE.sub(r"\1\2[SECRET]", texte)


def normaliser_log(ligne: str, numero: int, source: str = "DOCKER",
                   environment: str = "production") -> Evenement:
    # AAAA-MM-JJ HH:MM:SS NIVEAU composant message...
    champs = ligne.strip().split(None, 4)
    if len(champs) < 5:
        raise ValueError("Ligne de log invalide : moins de 5 champs")
    date, heure, niveau, composant, message = champs
    severity = _SEVERITES_LOG.get(niveau.upper(), "LOW")
    return Evenement(
        id=f"EVT-{numero:05d}",
        timestamp=f"{date}T{heure}Z",
        source=source,
        component=composant,
        environment=environment,
        event_type="LOG",
        severity=severity,
        message=masquer_secrets(message),
    )


def normaliser_scan(rapport: dict, numero: int,
                    environment: str = "production") -> Evenement:
    _verifier_cles(rapport, ("cve", "package", "severity", "date"))
    severity = str(rapport["severity"]).upper()
    if severity not in ("CRITICAL", "HIGH", "MEDIUM", "LOW"):
        severity = "LOW"
    return Evenement(
        id=f"EVT-{numero:05d}",
        timestamp=rapport["date"],
        source="TRIVY",
        component=rapport["package"],
        environment=environment,
        event_type="VULNERABILITY",
        severity=severity,
        message=f"Vulnerabilite {rapport['cve']} dans {rapport['package']}",
    )


def normaliser_pipeline(rapport: dict, numero: int,
                        environment: str = "production") -> Evenement:
    _verifier_cles(rapport, ("job", "status", "date"))
    echec = str(rapport["status"]).lower() == "failed"
    return Evenement(
        id=f"EVT-{numero:05d}",
        timestamp=rapport["date"],
        source="CI",
        component=rapport["job"],
        environment=environment,
        event_type="PIPELINE_FAILURE" if echec else "PIPELINE_OK",
        severity="HIGH" if echec else "LOW",
        message=f"Pipeline {rapport['job']} : {rapport['status']}",
    )