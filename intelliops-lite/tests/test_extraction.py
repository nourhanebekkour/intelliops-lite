def test_masquer_secrets_variantes(self):
        self.assertEqual(masquer_secrets("TOKEN: abc&x=1"), "TOKEN: [SECRET]&x=1")
        self.assertEqual(masquer_secrets("api_key=k1;user=bob"), "api_key=[SECRET];user=bob")

def test_severites(self):
        base = "2026-10-05 10:00:00 {} backend msg"
        self.assertEqual(normaliser_log(base.format("FATAL"), 1).severity, "CRITICAL")
        self.assertEqual(normaliser_log(base.format("warn"), 1).severity, "MEDIUM")
        self.assertEqual(normaliser_log(base.format("INFO"), 1).severity, "LOW")

def test_log_invalide(self):
        with self.assertRaises(ValueError):
            normaliser_log("trop court", 1)

def test_scan(self):
        r = {"cve": "CVE-2026-1234", "package": "lib-xyz",
             "severity": "critical", "date": "2026-10-05T10:07:00Z"}
        e = normaliser_scan(r, 7)
        self.assertEqual(e.source, "TRIVY")
        self.assertEqual(e.severity, "CRITICAL")
        self.assertEqual(e.message, "Vulnerabilite CVE-2026-1234 dans lib-xyz")
        with self.assertRaises(ValueError):
            normaliser_scan({"cve": "x"}, 7)

def test_pipeline(self):
        r = {"job": "build", "status": "FAILED", "date": "2026-10-05T10:06:00Z"}
        e = normaliser_pipeline(r, 8)
        self.assertEqual(e.event_type, "PIPELINE_FAILURE")
        self.assertEqual(e.severity, "HIGH")
        ok = normaliser_pipeline({**r, "status": "success"}, 9)
        self.assertEqual(ok.event_type, "PIPELINE_OK")
        self.assertEqual(ok.severity, "LOW")