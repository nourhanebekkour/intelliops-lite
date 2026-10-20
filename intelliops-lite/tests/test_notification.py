import unittest

from src.contrat import Analyse, Evenement, Notification
from src.notification import (
    choisir_canal,
    notifier,
    rediger,
    tracer_decision,
    valider_action,
)


def exemple(sensible=True, niveau="CRITICAL"):
    e = Evenement("EVT-00125", "2026-10-05T10:02:11Z", "DOCKER", "backend",
                  "production", "LOG", "HIGH", "OOMKilled restarts=14")
    a = Analyse("EVT-00125", niveau, "Manque de memoire",
                "Redemarrer le service backend", sensible, ["DOCKER"])
    return e, a


class TestChoisirCanal(unittest.TestCase):
    def test_canaux(self):
        self.assertEqual(choisir_canal("CRITICAL"), "TEAMS")
        self.assertEqual(choisir_canal("HIGH"), "SLACK")
        self.assertEqual(choisir_canal("MEDIUM"), "EMAIL")
        self.assertEqual(choisir_canal("LOW"), "DASHBOARD")

    def test_niveau_inconnu(self):
        with self.assertRaises(ValueError):
            choisir_canal("URGENT")

    def test_casse_non_toleree(self):
        with self.assertRaises(ValueError):
            choisir_canal("critical")


class TestRediger(unittest.TestCase):
    def test_cinq_lignes(self):
        e, a = exemple()
        self.assertEqual(len(rediger(e, a).split("\n")), 5)

    def test_contenu_exact(self):
        e, a = exemple()
        attendu = (
            "[CRITICAL] Composant : backend\n"
            "Evenement : OOMKilled restarts=14\n"
            "Explication : Manque de memoire\n"
            "Action proposee : Redemarrer le service backend\n"
            "Sources : DOCKER"
        )
        self.assertEqual(rediger(e, a), attendu)

    def test_sources_multiples(self):
        e, a = exemple()
        a.sources = ["DOCKER", "TRIVY"]
        self.assertTrue(rediger(e, a).endswith("Sources : DOCKER, TRIVY"))


class TestNotifier(unittest.TestCase):
    def test_notification_creee(self):
        e, a = exemple()
        historique = []
        n = notifier(e, a, historique)
        self.assertIsInstance(n, Notification)
        self.assertEqual(n.event_id, "EVT-00125")
        self.assertEqual(n.channel, "TEAMS")
        self.assertEqual(n.recipient, "equipe-ops")
        self.assertEqual(n.text, rediger(e, a))

    def test_historique_mis_a_jour(self):
        e, a = exemple()
        historique = []
        n = notifier(e, a, historique)
        self.assertEqual(historique, [n])

    def test_statut_notified(self):
        e, a = exemple()
        self.assertEqual(e.status, "NEW")
        notifier(e, a, [])
        self.assertEqual(e.status, "NOTIFIED")

    def test_canal_suit_le_niveau(self):
        e, a = exemple(sensible=False, niveau="LOW")
        self.assertEqual(notifier(e, a, []).channel, "DASHBOARD")

    def test_niveau_invalide(self):
        e, a = exemple(niveau="???")
        historique = []
        with self.assertRaises(ValueError):
            notifier(e, a, historique)
        self.assertEqual(historique, [])


class TestValiderAction(unittest.TestCase):
    def test_reponses_positives(self):
        _, a = exemple()
        for rep in ["o", "oui", "ok", "yes", " OUI ", "Yes", "O", " ok\n"]:
            with self.subTest(reponse=rep):
                self.assertTrue(valider_action(a, rep))

    def test_reponses_negatives(self):
        _, a = exemple()
        for rep in ["n", "non", "no", "", "   ", "peut-etre", "ouiii"]:
            with self.subTest(reponse=rep):
                self.assertFalse(valider_action(a, rep))

    def test_action_non_sensible(self):
        _, a = exemple(sensible=False)
        self.assertTrue(valider_action(a, "n"))
        self.assertTrue(valider_action(a, ""))


class TestTracerDecision(unittest.TestCase):
    def test_entree_journal(self):
        _, a = exemple()
        journal = []
        entree = tracer_decision(a, True, "ops-oncall", journal,
                                 "2026-10-05T10:05:00Z")
        self.assertEqual(entree, {
            "event_id": "EVT-00125",
            "action": "Redemarrer le service backend",
            "approved": True,
            "actor": "ops-oncall",
            "timestamp": "2026-10-05T10:05:00Z",
        })
        self.assertEqual(journal, [entree])

    def test_decision_refusee(self):
        _, a = exemple()
        journal = []
        entree = tracer_decision(a, False, "alice", journal, "2026-10-05T10:06:00Z")
        self.assertFalse(entree["approved"])
        self.assertEqual(entree["actor"], "alice")

    def test_journal_cumulatif(self):
        _, a = exemple()
        journal = []
        tracer_decision(a, True, "x", journal, "t1")
        tracer_decision(a, False, "y", journal, "t2")
        self.assertEqual([j["timestamp"] for j in journal], ["t1", "t2"])


if __name__ == "__main__":
    unittest.main()