"""Testes da camada de banco (storage.py), sem passar pelo Flask."""
from pathlib import Path
import sqlite3
import tempfile
import unittest

import storage
import tournament as rules


class StorageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = str(Path(self.temp.name) / "storage.sqlite3")
        storage.initialize(self.path)

    def tearDown(self):
        self.temp.cleanup()

    def tables(self):
        db = storage.connect(self.path)
        try:
            rows = db.execute("SELECT name FROM sqlite_master WHERE type = 'table'").fetchall()
        finally:
            db.close()
        return {row["name"] for row in rows}

    def add_user(self, db, username):
        return db.execute(
            "INSERT INTO user (username, display_name, password_hash, created) VALUES (?, 'Nome', 'hash', 0)",
            (username,))

    def test_initialize_creates_tables_and_is_repeatable(self):
        expected = {"tournament", "organizer", "user", "login_attempt"}
        self.assertTrue(expected <= self.tables())
        with storage.transaction(self.path) as db:
            self.add_user(db, "alice")
        storage.initialize(self.path)  # reabrir o app não pode apagar dados
        with storage.transaction(self.path) as db:
            self.assertEqual(db.execute("SELECT COUNT(*) FROM user").fetchone()[0], 1)

    def test_read_is_none_before_save_and_roundtrips_after(self):
        db = storage.connect(self.path)
        try:
            self.assertIsNone(storage.read(db))
        finally:
            db.close()
        state = rules.create("Copa Ação", 8)
        rules.register(state, "João", "Joao#BR1", "Ouro", user_id=7)
        with storage.transaction(self.path) as db:
            storage.save(db, state)
        db = storage.connect(self.path)
        try:
            self.assertEqual(storage.read(db), state)  # acentos e user_id preservados
        finally:
            db.close()

    def test_save_replaces_instead_of_duplicating(self):
        with storage.transaction(self.path) as db:
            storage.save(db, rules.create("Primeira", 8))
            storage.save(db, rules.create("Segunda", 16))
        db = storage.connect(self.path)
        try:
            self.assertEqual(db.execute("SELECT COUNT(*) FROM tournament").fetchone()[0], 1)
            self.assertEqual(storage.read(db)["name"], "Segunda")
        finally:
            db.close()

    def test_transaction_rolls_back_on_error(self):
        with self.assertRaises(RuntimeError):
            with storage.transaction(self.path) as db:
                storage.save(db, rules.create("Não pode ficar", 8))
                self.add_user(db, "fantasma")
                raise RuntimeError("falha no meio da operação")
        db = storage.connect(self.path)
        try:
            self.assertIsNone(storage.read(db))
            self.assertEqual(db.execute("SELECT COUNT(*) FROM user").fetchone()[0], 0)
        finally:
            db.close()

    def test_database_rejects_duplicate_username_ignoring_case(self):
        with storage.transaction(self.path) as db:
            self.add_user(db, "Alice")
        with self.assertRaises(sqlite3.IntegrityError):
            with storage.transaction(self.path) as db:
                self.add_user(db, "ALICE")
        db = storage.connect(self.path)
        try:
            self.assertEqual(db.execute("SELECT COUNT(*) FROM user").fetchone()[0], 1)
        finally:
            db.close()

    def test_user_ids_are_distinct_and_never_reused(self):
        with storage.transaction(self.path) as db:
            first = self.add_user(db, "alice").lastrowid
            second = self.add_user(db, "bruno").lastrowid
        with storage.transaction(self.path) as db:
            db.execute("DELETE FROM user WHERE id = ?", (second,))
            third = self.add_user(db, "carla").lastrowid
        self.assertEqual(len({first, second, third}), 3)

    def test_organizer_table_accepts_only_one_row(self):
        with storage.transaction(self.path) as db:
            db.execute("INSERT INTO organizer VALUES (1, 'org', 'hash', 'v1')")
        with self.assertRaises(sqlite3.IntegrityError):
            with storage.transaction(self.path) as db:
                db.execute("INSERT INTO organizer VALUES (2, 'outro', 'hash', 'v2')")


if __name__ == "__main__":
    unittest.main()
