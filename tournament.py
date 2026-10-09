"""Regras do campeonato, independentes das páginas e do banco de dados."""
from itertools import combinations
import random
import re

RANKS = ["Ferro", "Bronze", "Prata", "Ouro", "Platina",
         "Diamante", "Ascendente", "Imortal", "Radiante"]
PHASES = {"registration": "Inscrições abertas", "groups": "Fase de grupos",
          "knockout": "Mata-mata", "finished": "Campeonato encerrado"}


class RuleError(ValueError):
    """Mensagem que pode ser exibida ao jogador ou organizador."""


def create(name, capacity):
    name = name.strip()
    if not 3 <= len(name) <= 70:
        raise RuleError("O nome do campeonato precisa ter entre 3 e 70 caracteres.")
    if capacity not in (8, 16):
        raise RuleError("Escolha 8 ou 16 duplas.")
    return {"name": name, "capacity": capacity, "phase": "registration",
            "players": [], "teams": [], "groups": [], "matches": [],
            "round": 0, "champion": None}


def register(state, name, riot_id, rank):
    if state["phase"] != "registration":
        raise RuleError("As inscrições estão encerradas.")
    if len(state["players"]) >= state["capacity"] * 2:
        raise RuleError("Todas as vagas foram preenchidas.")
    name, riot_id = name.strip(), riot_id.strip()
    if not 2 <= len(name) <= 40:
        raise RuleError("Informe um nome com 2 a 40 caracteres.")
    # Validação de formato apenas: não consulta nem autentica uma conta Riot.
    if not re.fullmatch(r"[^#\x00-\x1f]{3,16}#[A-Za-z0-9]{3,5}", riot_id):
        raise RuleError("Use o formato Nome#TAG: nome de 3 a 16 caracteres e tag de 3 a 5 letras ou números.")
    if rank not in RANKS:
        raise RuleError("Selecione seu rank atual.")
    if any(p["riot_id"].casefold() == riot_id.casefold() for p in state["players"]):
        raise RuleError("Este Riot ID já está inscrito.")
    player = {"id": max((p["id"] for p in state["players"]), default=0) + 1,
              "name": name, "riot_id": riot_id, "rank": rank,
              "level": RANKS.index(rank) + 1}
    state["players"].append(player)
    return player


def remove_player(state, player_id):
    if state["phase"] != "registration":
        raise RuleError("Só é possível remover inscrições antes do sorteio.")
    if not any(p["id"] == player_id for p in state["players"]):
        raise RuleError("Inscrição não encontrada.")
    state["players"] = [p for p in state["players"] if p["id"] != player_id]


def new_match(state, a, b, group=None, round_number=0):
    match = {"id": len(state["matches"]) + 1, "a": a, "b": b,
             "group": group, "round": round_number, "score_a": None, "score_b": None}
    state["matches"].append(match)
    return match


def draw(state, rng=None):
    if state["phase"] != "registration":
        raise RuleError("O sorteio já foi realizado.")
    if len(state["players"]) != state["capacity"] * 2:
        raise RuleError("Preencha todas as vagas antes de sortear.")
    rng = rng or random.SystemRandom()
    players = state["players"][:]
    rng.shuffle(players)  # Sorteia a ordem entre jogadores do mesmo nível.
    players.sort(key=lambda p: p["level"])
    count = state["capacity"]
    for i in range(count):
        members = [players[i], players[-i - 1]]
        state["teams"].append({"id": i + 1, "name": f"Dupla {i + 1:02d}",
                               "players": members,
                               "strength": sum(p["level"] for p in members)})
    order = list(range(1, count + 1))
    rng.shuffle(order)
    for i in range(count // 4):
        # A ordem sorteada também define o último critério de desempate.
        members = order[i * 4:i * 4 + 4]
        group = {"name": chr(65 + i), "teams": members}
        state["groups"].append(group)
        for a, b in combinations(members, 2):
            new_match(state, a, b, group=group["name"])
    state["phase"] = "groups"


def standings(state, group):
    rows = {team: {"team": team, "played": 0, "wins": 0, "losses": 0,
                   "points": 0, "for": 0, "against": 0, "diff": 0,
                   "seed": i + 1}
            for i, team in enumerate(group["teams"])}
    for match in state["matches"]:
        if match["group"] != group["name"] or match["score_a"] is None:
            continue
        for own, other, scored, conceded in [
            (match["a"], match["b"], match["score_a"], match["score_b"]),
            (match["b"], match["a"], match["score_b"], match["score_a"]),
        ]:
            row = rows[own]
            row["played"] += 1
            row["for"] += scored
            row["against"] += conceded
            row["diff"] = row["for"] - row["against"]
            row["wins"] += int(scored > conceded)
            row["losses"] += int(scored < conceded)
            row["points"] = row["wins"] * 3
    return sorted(rows.values(), key=lambda r: (-r["points"], -r["diff"], -r["for"], r["seed"]))


def set_score(state, match_id, a, b):
    match = next((m for m in state["matches"] if m["id"] == match_id), None)
    if not match:
        raise RuleError("Partida não encontrada.")
    editable = ((state["phase"] == "groups" and match["group"] is not None)
                or (state["phase"] == "knockout" and match["round"] == state["round"]))
    if not editable:
        raise RuleError("Esta fase já foi encerrada. Seus resultados estão bloqueados.")
    if type(a) is not int or type(b) is not int or not (0 <= a <= 99 and 0 <= b <= 99) or a == b:
        raise RuleError("Informe rounds inteiros de 0 a 99, sem empate.")
    match["score_a"], match["score_b"] = a, b


def winner(match):
    return match["a"] if match["score_a"] > match["score_b"] else match["b"]


def advance(state):
    if state["phase"] == "groups":
        if any(m["score_a"] is None for m in state["matches"]):
            raise RuleError("Registre todos os resultados dos grupos antes de avançar.")
        classified = [standings(state, g)[:2] for g in state["groups"]]
        # Em 16 duplas, parceiros de grupo ficam em metades opostas da chave.
        pairings = [(0, 0, 1, 1), (1, 0, 0, 1)]
        if state["capacity"] == 16:
            pairings = [(0, 0, 1, 1), (2, 0, 3, 1), (1, 0, 0, 1), (3, 0, 2, 1)]
        state["round"] = 1
        for ga, pa, gb, pb in pairings:
            new_match(state, classified[ga][pa]["team"], classified[gb][pb]["team"], round_number=1)
        state["phase"] = "knockout"
    elif state["phase"] == "knockout":
        matches = [m for m in state["matches"] if m["round"] == state["round"]]
        if any(m["score_a"] is None for m in matches):
            raise RuleError("Registre todos os resultados desta rodada antes de avançar.")
        winners = [winner(m) for m in matches]
        if len(winners) == 1:
            state["champion"] = winners[0]
            state["phase"] = "finished"
        else:
            state["round"] += 1
            for a, b in zip(winners[::2], winners[1::2]):
                new_match(state, a, b, round_number=state["round"])
    else:
        raise RuleError("Não é possível avançar nesta fase.")

