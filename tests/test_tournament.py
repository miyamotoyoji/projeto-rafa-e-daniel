import copy
import random
import unittest
import tournament as rules


def full_tournament(capacity=8):
    state = rules.create("Copa da comunidade", capacity)
    for i in range(capacity * 2):
        rules.register(state, f"Jogador {i}", f"Jogador{i}#BR1", rules.RANKS[i % 9])
    return state


class TournamentTests(unittest.TestCase):
    def test_only_supported_sizes(self):
        for capacity in (0, 4, 9, 32):
            with self.assertRaises(rules.RuleError):
                rules.create("Copa", capacity)

    def test_registration_validation(self):
        s = rules.create("Copa", 8)
        rules.register(s, "Rafa", "Rafael#BR1", "Ouro")
        for name, riot, rank in [("Rafa", "rafael#br1", "Ouro"), ("R", "Novo#BR1", "Ouro"),
                                 ("Rafa", "sem-tag", "Ouro"), ("Rafa", "Novo#BR1", "Inválido")]:
            with self.assertRaises(rules.RuleError):
                rules.register(s, name, riot, rank)
        self.assertEqual(len(s["players"]), 1)

    def test_capacity_and_incomplete_draw(self):
        with self.assertRaises(rules.RuleError):
            rules.draw(rules.create("Copa", 8))
        s = full_tournament()
        with self.assertRaises(rules.RuleError):
            rules.register(s, "Outro", "Outro#BR1", "Ferro")

    def test_balanced_pairs_and_groups(self):
        for capacity in (8, 16):
            for seed in range(20):
                s = full_tournament(capacity)
                rules.draw(s, random.Random(seed))
                ids = [p["id"] for team in s["teams"] for p in team["players"]]
                self.assertEqual(len(set(ids)), capacity * 2)
                self.assertEqual(len(s["teams"]), capacity)
                self.assertEqual(len(s["matches"]), capacity // 4 * 6)
                strengths = [t["strength"] for t in s["teams"]]
                self.assertLessEqual(max(strengths) - min(strengths), 1)
                for g in s["groups"]:
                    matches = [m for m in s["matches"] if m["group"] == g["name"]]
                    self.assertEqual(len(matches), 6)
                    for team in g["teams"]:
                        self.assertEqual(sum(team in (m["a"], m["b"]) for m in matches), 3)

    def test_draw_is_locked_and_signup_closes(self):
        s = full_tournament()
        rules.draw(s)
        with self.assertRaises(rules.RuleError):
            rules.draw(s)
        with self.assertRaises(rules.RuleError):
            rules.register(s, "Outro", "Outro#BR1", "Ferro")
        with self.assertRaises(rules.RuleError):
            rules.remove_player(s, 1)

    def test_invalid_score_does_not_change_match(self):
        s = full_tournament()
        rules.draw(s)
        before = copy.deepcopy(s)
        for a, b in [(13, 13), (-1, 13), (13, 100), ("13", 0), (True, 0)]:
            with self.assertRaises(rules.RuleError):
                rules.set_score(s, 1, a, b)
        self.assertEqual(s, before)

    def test_points_and_tie_order(self):
        s = full_tournament()
        rules.draw(s, random.Random(1))
        g = s["groups"][0]
        self.assertEqual([r["team"] for r in rules.standings(s, g)], g["teams"])
        first = s["matches"][0]
        rules.set_score(s, first["id"], 13, 5)
        top = rules.standings(s, g)[0]
        self.assertEqual((top["team"], top["points"], top["diff"]), (first["a"], 3, 8))

    def test_corrections_recalculate_standings(self):
        s = full_tournament()
        rules.draw(s)
        m = s["matches"][0]
        rules.set_score(s, m["id"], 13, 0)
        rules.set_score(s, m["id"], 0, 13)
        rows = rules.standings(s, s["groups"][0])
        self.assertEqual(rows[0]["team"], m["b"])
        self.assertEqual(sum(row["points"] for row in rows), 3)

    def test_full_championship_both_sizes(self):
        for capacity in (8, 16):
            s = full_tournament(capacity)
            rules.draw(s, random.Random(7))
            with self.assertRaises(rules.RuleError):
                rules.advance(s)
            for m in list(s["matches"]):
                rules.set_score(s, m["id"], 13, 7)
            qualifiers = {r["team"] for g in s["groups"] for r in rules.standings(s, g)[:2]}
            rules.advance(s)
            round_one = [m for m in s["matches"] if m["round"] == 1]
            self.assertEqual({m[k] for m in round_one for k in ("a", "b")}, qualifiers)
            with self.assertRaises(rules.RuleError):
                rules.set_score(s, 1, 0, 13)
            if capacity == 16:
                halves = [{m[k] for m in part for k in ("a", "b")}
                          for part in (round_one[:2], round_one[2:])]
                for g in s["groups"]:
                    self.assertEqual(len(halves[0] & set(g["teams"])), 1)
                    self.assertEqual(len(halves[1] & set(g["teams"])), 1)
            while s["phase"] != "finished":
                for m in s["matches"]:
                    if m["round"] == s["round"]:
                        rules.set_score(s, m["id"], 13, 4)
                rules.advance(s)
            self.assertIn(s["champion"], qualifiers)
            with self.assertRaises(rules.RuleError):
                rules.set_score(s, s["matches"][-1]["id"], 0, 13)

    def test_player_removal_preserves_unique_ids(self):
        s = full_tournament()
        rules.remove_player(s, 3)
        rules.register(s, "Novo", "Novo#BR1", "Ferro")
        self.assertEqual(len(set(p["id"] for p in s["players"])), 16)


if __name__ == "__main__":
    unittest.main()

