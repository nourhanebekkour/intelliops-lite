import unittest
from src.analyse import analyser, classifier, compter_erreurs, est_doublon, chercher_procedures
from src.contrat import PROCEDURES, Evenement, Analyse

def evt(type_="LOG", severity="HIGH", message="OOMKilled restarts=14", composant="backend"):
    return Evenement("EVT-00001", "2026-10-05T10:00:00Z", "DOCKER", composant,
                     "production", type_, severity, message)

class TestAnalyse(unittest.TestCase):

    def test_doublon(self):
        vus = set()
        self.assertFalse(est_doublon(evt(), vus))
        self.assertTrue(est_doublon(evt(), vus))

    def test_compter_erreurs(self):
        compteur = {}
        e = evt()
        n = compter_erreurs(e, compteur)
        self.assertEqual(n, 1)
        # deuxième appel incrémente
        n = compter_erreurs(e, compteur)
        self.assertEqual(n, 2)

    def test_classifier_boucle(self):
        e = evt()
        self.assertEqual(classifier(e, 3), "CRITICAL")  # règle essentielle
        self.assertEqual(classifier(e, 2), "HIGH")
        self.assertEqual(classifier(e, 0), "HIGH")  # par défaut

    def test_chercher_procedures(self):
        e = evt()
        procs = chercher_procedures(e, PROCEDURES)
        self.assertIsInstance(procs, list)

    def test_analyser(self):
        e = evt()
        base = PROCEDURES
        analyse = analyser(e, base, nb_erreurs=3)
        self.assertIsInstance(analyse, Analyse)
        self.assertEqual(analyse.diagnostic, "CRITICAL")
