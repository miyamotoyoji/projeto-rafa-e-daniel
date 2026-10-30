"""Aplicação Flask. Execute 'flask --app app init-admin' antes de organizar."""
from datetime import timedelta
from functools import wraps
import hmac
import os
import re
from pathlib import Path
import secrets
import sqlite3
import time

import click
from flask import Flask, abort, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

import storage
import tournament as rules

DUMMY_HASH = generate_password_hash("sem-usuario")


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    secret = os.environ.get("SECRET_KEY")
    if not secret and not test_config:
        key_path = Path(app.instance_path) / "secret.key"
        try:
            # Modo exclusivo impede duas instâncias de sobrescreverem a chave.
            with key_path.open("x", encoding="utf-8") as handle:
                handle.write(secrets.token_hex(32))
            key_path.chmod(0o600)
        except FileExistsError:
            pass
        secret = key_path.read_text(encoding="utf-8").strip()
    app.config.update(
        SECRET_KEY=secret, DATABASE=str(Path(app.instance_path) / "championship.sqlite3"),
        SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=os.environ.get("COOKIE_SECURE") == "1",
        PERMANENT_SESSION_LIFETIME=timedelta(hours=8),
        MAX_CONTENT_LENGTH=16 * 1024,
    )
    if test_config:
        app.config.update(test_config)
    storage.initialize(app.config["DATABASE"])

    def state():
        db = storage.connect(app.config["DATABASE"])
        try:
            return storage.read(db)
        finally:
            db.close()

    def csrf_token():
        if "csrf" not in session:
            session["csrf"] = secrets.token_urlsafe(32)
        return session["csrf"]

    def is_organizer():
        if not session.get("organizer"):
            return False
        db = storage.connect(app.config["DATABASE"])
        try:
            admin = db.execute("SELECT version FROM organizer WHERE id = 1").fetchone()
            return bool(admin and hmac.compare_digest(admin["version"], session["organizer"]))
        finally:
            db.close()

    def current_user():
        user_id = session.get("user")
        if not isinstance(user_id, int):
            return None
        db = storage.connect(app.config["DATABASE"])
        try:
            return db.execute("SELECT id, username, display_name FROM user WHERE id = ?",
                              (user_id,)).fetchone()
        finally:
            db.close()

    def user_required(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not current_user():
                if request.method == "POST":
                    abort(403)
                return redirect(url_for("user_login"))
            return fn(*args, **kwargs)
        return wrapper

    def protected(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not is_organizer():
                if request.method == "POST":
                    abort(403)
                return redirect(url_for("login"))
            return fn(*args, **kwargs)
        return wrapper

    @app.before_request
    def protect_forms():
        if request.method == "POST":
            supplied = request.form.get("csrf_token", "")
            expected = session.get("csrf", "")
            if not supplied or not expected or not hmac.compare_digest(supplied.encode("utf-8"), expected.encode("utf-8")):
                abort(400, description="A sessão do formulário expirou. Atualize a página e tente novamente.")

    @app.after_request
    def headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "same-origin"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self'; style-src 'self'; "
            "img-src 'self' data:; font-src 'self'; base-uri 'self'; "
            "form-action 'self'; frame-ancestors 'none'; object-src 'none'"
        )
        if not request.path.startswith("/static/"):
            response.headers["Cache-Control"] = "no-store"
        return response

    @app.context_processor
    def helpers():
        return {"csrf_token": csrf_token, "ranks": rules.RANKS,
                "phases": rules.PHASES, "organizer": is_organizer(), "current_user": current_user(),
                "team_name": lambda s, ident: next((t["name"] for t in s["teams"] if t["id"] == ident), "A definir"),
                "team_members": lambda s, ident: " / ".join(
                    p["name"] for t in s["teams"] if t["id"] == ident for p in t["players"])}

    def render(page, **extra):
        s = state()
        tables = [(g, rules.standings(s, g)) for g in s["groups"]] if s else []
        return render_template(page + ".html", s=s, tables=tables, **extra)

    @app.get("/")
    def home():
        return render("home")

    @app.route("/inscricao", methods=["GET", "POST"])
    def signup():
        if request.method == "POST":
            try:
                with storage.transaction(app.config["DATABASE"]) as db:
                    s = storage.read(db)
                    if not s:
                        raise rules.RuleError("O organizador ainda não abriu as inscrições.")
                    user = current_user()
                    rules.register(s, request.form.get("name", ""), request.form.get("riot_id", ""),
                                   request.form.get("rank", ""), user["id"] if user else None)
                    storage.save(db, s)
                flash("Inscrição confirmada. Acompanhe aqui o sorteio da sua dupla.", "success")
                return redirect(url_for("signup"))
            except rules.RuleError as error:
                return render("signup", error=str(error), values=request.form), 400
        user = current_user()
        return render("signup", values={"name": user["display_name"]} if user else {})

    @app.get("/duplas")
    def teams():
        return render("teams")

    @app.get("/grupos")
    def groups():
        return render("groups")

    @app.get("/mata-mata")
    def bracket():
        return render("bracket")

    def throttled(db, key, now):
        """Cinco falhas por endereço e tipo de login em 15 minutos (RNF05, RNF10)."""
        db.execute("DELETE FROM login_attempt WHERE started < ?", (now - 900,))
        attempt = db.execute("SELECT failures FROM login_attempt WHERE address = ?", (key,)).fetchone()
        return bool(attempt and attempt["failures"] >= 5)

    def register_failure(db, key, now):
        db.execute("INSERT INTO login_attempt (address, failures, started) VALUES (?, 1, ?) "
                   "ON CONFLICT(address) DO UPDATE SET failures = failures + 1", (key, now))

    @app.route("/conta/criar", methods=["GET", "POST"])
    def user_signup():
        if current_user():
            return redirect(url_for("account"))
        if request.method == "POST":
            username = request.form.get("username", "").strip()
            display_name = request.form.get("display_name", "").strip()
            password = request.form.get("password", "")
            error = None
            if not re.fullmatch(r"[A-Za-z0-9_.-]{3,30}", username):
                error = "Usuário com 3 a 30 letras, números, ponto, hífen ou sublinhado."
            elif not 2 <= len(display_name) <= 40:
                error = "Informe um nome com 2 a 40 caracteres."
            elif not 12 <= len(password) <= 1024:
                error = "A senha precisa ter de 12 a 1024 caracteres."
            elif password != request.form.get("password_confirm", ""):
                error = "As senhas não coincidem."
            if not error:
                try:
                    with storage.transaction(app.config["DATABASE"]) as db:
                        cursor = db.execute(
                            "INSERT INTO user (username, display_name, password_hash, created) VALUES (?, ?, ?, ?)",
                            (username, display_name, generate_password_hash(password), time.time()))
                        user_id = cursor.lastrowid
                except sqlite3.IntegrityError:
                    error = "Este usuário já existe. Escolha outro."
            if error:
                return render("user_signup", error=error, values=request.form), 400
            session.clear()
            session["user"] = user_id
            session.permanent = True
            flash("Conta criada. Você já pode se inscrever no campeonato.", "success")
            return redirect(url_for("account"))
        return render("user_signup", values={})

    @app.route("/conta/entrar", methods=["GET", "POST"])
    def user_login():
        if current_user():
            return redirect(url_for("account"))
        if request.method == "POST":
            key = "user:" + (request.remote_addr or "unknown")
            now = time.time()
            with storage.transaction(app.config["DATABASE"]) as db:
                if throttled(db, key, now):
                    return render("user_login", error="Muitas tentativas. Aguarde 15 minutos e tente novamente."), 429
                row = db.execute("SELECT * FROM user WHERE username = ?",
                                 (request.form.get("username", "").strip(),)).fetchone()
                # Sempre verifica um hash para não revelar se o usuário existe pelo tempo de resposta.
                valid = check_password_hash(row["password_hash"] if row else DUMMY_HASH,
                                            request.form.get("password", "")[:1024]) and bool(row)
                if valid:
                    db.execute("DELETE FROM login_attempt WHERE address = ?", (key,))
                    session.clear()
                    session["user"] = row["id"]
                    session.permanent = True
                    return redirect(url_for("account"))
                register_failure(db, key, now)
            return render("user_login", error="Usuário ou senha incorretos."), 401
        return render("user_login")

    @app.post("/conta/sair")
    @user_required
    def user_logout():
        session.clear()
        return redirect(url_for("home"))

    @app.get("/conta")
    @user_required
    def account():
        s = state()
        user = current_user()
        player = next((p for p in (s["players"] if s else []) if p.get("user_id") == user["id"]), None)
        team = next((t for t in (s["teams"] if s else []) if player and any(m["id"] == player["id"] for m in t["players"])), None)
        return render("account", player=player, team=team)

    @app.route("/organizador/entrar", methods=["GET", "POST"])
    def login():
        if is_organizer():
            return redirect(url_for("admin"))
        if request.method == "POST":
            address = request.remote_addr or "unknown"
            now = time.time()
            error = "Usuário ou senha incorretos."
            with storage.transaction(app.config["DATABASE"]) as db:
                if throttled(db, address, now):
                    return render("login", error="Muitas tentativas. Aguarde 15 minutos e tente novamente."), 429
                admin_row = db.execute("SELECT * FROM organizer WHERE id = 1").fetchone()
                valid = bool(admin_row and check_password_hash(
                    admin_row["password_hash"], request.form.get("password", "")[:1024]))
                if valid and admin_row["username"] == request.form.get("username", ""):
                    db.execute("DELETE FROM login_attempt WHERE address = ?", (address,))
                    session.clear()
                    session["organizer"] = admin_row["version"]
                    session.permanent = True
                    return redirect(url_for("admin"))
                register_failure(db, address, now)
            return render("login", error=error), 401
        return render("login")

    @app.post("/organizador/sair")
    @protected
    def logout():
        session.clear()
        return redirect(url_for("home"))

    @app.get("/organizador")
    @protected
    def admin():
        return render("admin")

    @app.post("/organizador/acao")
    @protected
    def admin_action():
        try:
            with storage.transaction(app.config["DATABASE"]) as db:
                s = storage.read(db)
                action = request.form.get("action")
                if action == "create":
                    if s:
                        raise rules.RuleError("Já existe um campeonato. Seus dados foram preservados.")
                    s = rules.create(request.form.get("name", ""), int(request.form.get("capacity", 0)))
                    message = "Campeonato criado. As inscrições estão abertas."
                else:
                    if not s:
                        raise rules.RuleError("Crie o campeonato primeiro.")
                    if action == "draw":
                        rules.draw(s)
                        message = "Duplas e grupos sorteados. As inscrições foram encerradas."
                    elif action == "score":
                        rules.set_score(s, int(request.form.get("match_id", 0)),
                                        int(request.form.get("score_a", "")), int(request.form.get("score_b", "")))
                        message = "Placar salvo."
                    elif action == "advance":
                        rules.advance(s)
                        message = "Fase encerrada. A classificação foi atualizada."
                    elif action == "remove":
                        rules.remove_player(s, int(request.form.get("player_id", 0)))
                        message = "Inscrição removida."
                    else:
                        raise rules.RuleError("Ação desconhecida.")
                storage.save(db, s)
            flash(message, "success")
        except rules.RuleError as error:
            flash(str(error), "error")
        except ValueError:
            flash("Preencha os campos numéricos corretamente.", "error")
        return redirect(url_for("admin"))

    @app.errorhandler(sqlite3.Error)
    def database_error(error):
        app.logger.exception("Falha no banco de dados")
        return render_template("error.html", code=503,
                               message="Não foi possível acessar os dados. Tente novamente em instantes."), 503

    @app.errorhandler(400)
    @app.errorhandler(403)
    @app.errorhandler(404)
    @app.errorhandler(413)
    def http_error(error):
        messages = {403: "Entre como organizador para realizar esta ação.",
                    404: "Esta página não foi encontrada.", 413: "O formulário enviado excede o tamanho permitido."}
        return render_template("error.html", code=error.code,
                               message=messages.get(error.code, error.description)), error.code

    @app.cli.command("init-admin")
    @click.option("--username", prompt="Usuário do organizador")
    @click.password_option(confirmation_prompt=True, prompt="Senha (mínimo 12 caracteres)")
    def init_admin(username, password):
        """Cria ou troca a credencial do organizador sem publicá-la no GitHub."""
        if not 3 <= len(username.strip()) <= 40 or not 12 <= len(password) <= 1024:
            raise click.ClickException("Use um usuário de 3 a 40 caracteres e uma senha de 12 a 1024.")
        with storage.transaction(app.config["DATABASE"]) as db:
            db.execute("INSERT INTO organizer VALUES (1, ?, ?, ?) ON CONFLICT(id) DO UPDATE SET "
                       "username = excluded.username, password_hash = excluded.password_hash, version = excluded.version",
                       (username.strip(), generate_password_hash(password), secrets.token_hex(16)))
        click.echo("Organizador configurado. Sessões anteriores foram invalidadas.")

    return app
