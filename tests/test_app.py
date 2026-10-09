"""Testes HTTP: permissões, formulários, persistência e fluxo completo."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import tempfile
import unittest

from werkzeug.security import generate_password_hash
from app import create_app
import storage
import tournament as rules


class AppTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.password_hash = generate_password_hash("senha-de-teste-segura")

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.dbpath = str(Path(self.temp.name) / "test.sqlite3")
        self.app = create_app({"TESTING": True, "SECRET_KEY": "test-only",
                               "DATABASE": self.dbpath})
        self.client = self.app.test_client()
        with storage.transaction(self.dbpath) as db:
            db.execute("INSERT INTO organizer VALUES (1, ?, ?, ?)",
                       ("organizador", self.password_hash, "test-version"))

    def tearDown(self):
        self.temp.cleanup()

    def token(self, client=None):
        client = client or self.client
        client.get("/")
        with client.session_transaction() as session:
            session["csrf"] = "test-csrf-token"
        return "test-csrf-token"

    def post(self, path, data, client=None, **kwargs):
        client = client or self.client
        return client.post(path, data={**data, "csrf_token": self.token(client)}, **kwargs)

    def login(self):
        response = self.post("/organizador/entrar",
                             {"username": "organizador", "password": "senha-de-teste-segura"})
        self.assertEqual(response.status_code, 302)

    def create_tournament(self, capacity=8):
        self.login()
        return self.post("/organizador/acao",
                         {"action": "create", "name": "Copa de teste", "capacity": capacity})

    def read(self):
        db = storage.connect(self.dbpath)
        try:
            return storage.read(db)
        finally:
            db.close()

    def test_all_empty_pages_render(self):
        for path in ("/", "/inscricao", "/duplas", "/grupos", "/mata-mata", "/organizador/entrar"):
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)
                self.assertIn(b'lang="pt-BR"', response.data)
        self.assertEqual(self.client.get("/inexistente").status_code, 404)

    def test_csrf_and_organizer_permission(self):
        self.assertEqual(self.client.post("/inscricao").status_code, 400)
        self.assertEqual(self.client.get("/organizador").status_code, 302)
        self.assertEqual(self.post("/organizador/acao", {"action": "create"}).status_code, 403)
        response = self.client.post("/inscricao", data={"csrf_token": "ação"})
        self.assertEqual(response.status_code, 400)
        self.assertIsNone(self.read())

    def test_login_rate_limit_and_logout(self):
        for _ in range(5):
            response = self.post("/organizador/entrar", {"username": "organizador", "password": "errada"})
            self.assertEqual(response.status_code, 401)
        self.assertEqual(self.post("/organizador/entrar", {}).status_code, 429)
        with storage.transaction(self.dbpath) as db:
            db.execute("DELETE FROM login_attempt")
        self.login()
        self.assertEqual(self.client.get("/organizador").status_code, 200)
        self.post("/organizador/sair", {})
        self.assertEqual(self.client.get("/organizador").status_code, 302)

    def test_password_change_invalidates_session(self):
        self.login()
        with storage.transaction(self.dbpath) as db:
            db.execute("UPDATE organizer SET version = 'changed'")
        self.assertEqual(self.client.get("/organizador").status_code, 302)

    def test_registration_and_privacy(self):
        self.create_tournament()
        visitor = self.app.test_client()
        self.assertEqual(self.post("/inscricao", {"name": "Rafa", "riot_id": "Rafa#BR1", "rank": "Ouro"}, visitor).status_code, 302)
        response = visitor.get("/inscricao")
        self.assertIn(b"Rafa", response.data)
        self.assertNotIn(b"Rafa#BR1", response.data)
        self.assertIn(b"Rafa#BR1", self.client.get("/organizador").data)
        duplicate = self.post("/inscricao", {"name": "Rafa", "riot_id": "rafa#br1", "rank": "Ouro"}, visitor)
        self.assertEqual(duplicate.status_code, 400)
        self.assertIn(b'value="rafa#br1"', duplicate.data)
        self.assertEqual(len(self.read()["players"]), 1)

    def test_html_escaping(self):
        self.create_tournament()
        self.post("/inscricao", {"name": "<script>alert(1)</script>", "riot_id": "Player#BR1", "rank": "Ferro"})
        response = self.client.get("/inscricao")
        self.assertNotIn(b"<script>alert(1)</script>", response.data)
        self.assertIn(b"&lt;script&gt;", response.data)
        self.assertIn("script-src 'self'", response.headers["Content-Security-Policy"])

    def test_persistence_and_atomic_last_slot(self):
        self.create_tournament()
        with storage.transaction(self.dbpath) as db:
            s = storage.read(db)
            for i in range(15):
                rules.register(s, f"Jogador {i}", f"Jogador{i}#BR1", "Prata")
            storage.save(db, s)
        def signup(i):
            client = self.app.test_client()
            return self.post("/inscricao", {"name": f"Novo {i}", "riot_id": f"Novo{i}#BR1", "rank": "Prata"}, client).status_code
        with ThreadPoolExecutor(max_workers=2) as pool:
            codes = list(pool.map(signup, [1, 2]))
        self.assertEqual(sorted(codes), [302, 400])
        reopened = create_app({"TESTING": True, "SECRET_KEY": "test-only", "DATABASE": self.dbpath})
        self.assertIn(b"16 jogadores", reopened.test_client().get("/inscricao").data)
        self.assertEqual(len(self.read()["players"]), 16)

    def test_complete_http_journey(self):
        for capacity in (8, 16):
            with self.subTest(capacity=capacity):
                with storage.transaction(self.dbpath) as db:
                    db.execute("DELETE FROM tournament")
                self.create_tournament(capacity)
                visitor = self.app.test_client()
                for i in range(capacity * 2):
                    response = self.post("/inscricao", {"name": f"Jogador {i}", "riot_id": f"Player{i}#BR1",
                                                        "rank": rules.RANKS[i % 9]}, visitor)
                    self.assertEqual(response.status_code, 302)
                self.post("/organizador/acao", {"action": "draw"})
                self.assertEqual(self.read()["phase"], "groups")
                for path in ("/", "/inscricao", "/duplas", "/grupos", "/mata-mata", "/organizador"):
                    self.assertEqual(self.client.get(path).status_code, 200)
                while self.read()["phase"] != "finished":
                    s = self.read()
                    for m in s["matches"]:
                        if m["score_a"] is None:
                            self.post("/organizador/acao", {"action": "score", "match_id": m["id"],
                                                           "score_a": 13, "score_b": 5})
                    self.post("/organizador/acao", {"action": "advance"})
                    for path in ("/", "/grupos", "/mata-mata", "/organizador"):
                        self.assertEqual(self.client.get(path).status_code, 200)
                self.assertIsNotNone(self.read()["champion"])

    def test_wrong_action_preserves_data(self):
        self.create_tournament()
        before = self.read()
        for action in ("draw", "advance", "unknown"):
            self.post("/organizador/acao", {"action": action})
            self.assertEqual(self.read(), before)
        self.post("/organizador/acao", {"action": "create", "name": "Substituição", "capacity": 16})
        self.assertEqual(self.read(), before)

    def test_admin_command(self):
        result = self.app.test_cli_runner().invoke(
            args=["init-admin", "--username", "rafa", "--password", "nova-senha-segura"])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(self.post("/organizador/entrar", {"username": "rafa", "password": "nova-senha-segura"}).status_code, 302)


if __name__ == "__main__":
    unittest.main()

