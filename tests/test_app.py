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

    def make_account(self, client, username="jogador1", password="senha-longa-de-teste"):
        return self.post("/conta/criar", {"username": username, "display_name": "Jogador Um",
                                          "password": password, "password_confirm": password}, client)

    def test_accounts_are_stored_separately_and_hashed(self):
        a, b = self.app.test_client(), self.app.test_client()
        self.assertEqual(self.make_account(a, "alice").status_code, 302)
        self.assertEqual(self.make_account(b, "bruno").status_code, 302)
        with storage.transaction(self.dbpath) as db:
            rows = db.execute("SELECT username, password_hash FROM user ORDER BY id").fetchall()
        self.assertEqual([r["username"] for r in rows], ["alice", "bruno"])
        self.assertTrue(all("senha-longa-de-teste" not in r["password_hash"] for r in rows))
        self.assertIn(b"@alice", a.get("/conta").data)
        self.assertIn(b"@bruno", b.get("/conta").data)

    def test_account_validation_and_duplicate_username(self):
        self.assertEqual(self.make_account(self.client).status_code, 302)
        other = self.app.test_client()
        self.assertEqual(self.make_account(other, "JOGADOR1").status_code, 400)
        self.assertEqual(self.make_account(other, "ab").status_code, 400)
        self.assertEqual(self.make_account(other, "novo", "curta").status_code, 400)
        mismatch = self.post("/conta/criar", {"username": "novo", "display_name": "Novo",
                                              "password": "senha-longa-de-teste",
                                              "password_confirm": "outra-senha-longa"}, other)
        self.assertEqual(mismatch.status_code, 400)
        with storage.transaction(self.dbpath) as db:
            self.assertEqual(db.execute("SELECT COUNT(*) FROM user").fetchone()[0], 1)

    def test_account_login_logout_and_rate_limit(self):
        self.make_account(self.client)
        self.post("/conta/sair", {})
        self.assertEqual(self.client.get("/conta").status_code, 302)
        self.assertEqual(self.post("/conta/entrar", {"username": "jogador1", "password": "errada"}).status_code, 401)
        self.assertEqual(self.post("/conta/entrar", {"username": "naoexiste", "password": "x"}).status_code, 401)
        ok = self.post("/conta/entrar", {"username": "JOGADOR1", "password": "senha-longa-de-teste"})
        self.assertEqual(ok.status_code, 302)
        self.assertEqual(self.client.get("/conta").status_code, 200)
        self.post("/conta/sair", {})
        for _ in range(5):
            self.post("/conta/entrar", {"username": "jogador1", "password": "errada"})
        self.assertEqual(self.post("/conta/entrar", {"username": "jogador1",
                                                     "password": "senha-longa-de-teste"}).status_code, 429)

    def test_registration_links_to_account_and_blocks_second_entry(self):
        self.create_tournament()
        player = self.app.test_client()
        self.make_account(player)
        data = {"name": "Jogador Um", "riot_id": "Jogador1#BR1", "rank": "Ouro"}
        self.assertEqual(self.post("/inscricao", data, player).status_code, 302)
        self.assertIsNotNone(self.read()["players"][0]["user_id"])
        again = self.post("/inscricao", {**data, "riot_id": "Jogador2#BR1"}, player)
        self.assertEqual(again.status_code, 400)
        self.assertEqual(len(self.read()["players"]), 1)
        page = player.get("/conta").data
        self.assertIn(b"Jogador1#BR1", page)
        self.assertNotIn(b"Jogador1#BR1", self.app.test_client().get("/inscricao").data)

    def test_anonymous_registration_still_works_and_account_is_private(self):
        self.create_tournament()
        anon = self.app.test_client()
        self.assertEqual(self.post("/inscricao", {"name": "Anon", "riot_id": "Anon#BR1", "rank": "Ferro"}, anon).status_code, 302)
        self.assertIsNone(self.read()["players"][0]["user_id"])
        self.assertEqual(anon.get("/conta").status_code, 302)
        self.assertEqual(self.post("/conta/sair", {}, anon).status_code, 403)

    def test_user_session_is_not_organizer(self):
        self.make_account(self.client)
        self.assertEqual(self.client.get("/organizador").status_code, 302)
        self.assertEqual(self.post("/organizador/acao", {"action": "create"}).status_code, 403)


if __name__ == "__main__":
    unittest.main()

