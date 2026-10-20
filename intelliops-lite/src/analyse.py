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
raise NotImplementedError

def classifier(evt: Evenement, nb_erreurs: int = 0) -> str:
raise NotImplementedError

def analyser(evt: Evenement, base: dict, nb_erreurs: int = 0) -> Analyse:
raise NotImplementedError