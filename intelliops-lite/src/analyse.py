from src.contrat import Analyse, Evenement

def est_doublon(evt: Evenement, vus: set) -> bool:
    """
    Vérifie si un événement est déjà vu.
    """
    if evt.id in vus:
        return True
    vus.add(evt.id)
    return False
def compter_erreurs(evt: Evenement, compteur: dict) -> int:
    """
    Compte le nombre d'erreurs par composant.
    """
    key = evt.component
    compteur[key] = compteur.get(key, 0) + 1
    return compteur[key]
def chercher_procedures(evt: Evenement, base: dict) -> list:
    """
    Retourne la liste des procédures associées à un événement
    en fonction de son type ou message.
    """
    procedures = []
    for rule, actions in base.items():
        if rule in evt.message or rule in evt.event_type:
            procedures.extend(actions)
    return procedures
def classifier(evt: Evenement, nb_erreurs: int = 0) -> str:
    """
    Classe la criticité de l'événement selon sa sévérité et le nombre d'erreurs.
    """
    # Exemple de règles simples
    if nb_erreurs > 101:
        return "CRITICAL"
    if evt.severity.upper() == "HIGH":
        return "HIGH"
    if evt.severity.upper() == "LOW":
        return "LOW"
    return "INFO"
def analyser(evt: Evenement, base: dict, nb_erreurs: int = 0) -> Analyse:
    """
    Produit une analyse complète de l'événement.
    """
    level = classifier(evt, nb_erreurs)
    procedures = chercher_procedures(evt, base)
    explanation = f"Event {evt.id} classified as {level}"
    action = procedures[0] if procedures else "No action defined"
    sensitive = "password" in evt.message.lower() or "token" in evt.message.lower()

    return Analyse(
        event_id=evt.id,
        level=level,
        explanation=explanation,
        action=action,
        sensitive=sensitive,
        sources=[evt.source]
    )