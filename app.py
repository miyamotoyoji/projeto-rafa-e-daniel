"""Aplicação Flask. Execute 'flask --app app init-admin' antes de organizar."""
from datetime import timedelta
from functools import wraps
import hmac
import os
from pathlib import Path
import secrets
import sqlite3
import time

import click
from flask import Flask, abort, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

import storage
import tournament as rules


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
                "phases": rules.PHASES, "organizer": is_organizer(),
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
                    rules.register(s, request.form.get("name", ""), request.form.get("riot_id", ""),
                                   request.form.get("rank", ""))
                    storage.save(db, s)
                flash("Inscrição confirmada. Acompanhe aqui o sorteio da sua dupla.", "success")
                return redirect(url_for("signup"))
            except rules.RuleError as error:
                return render("signup", error=str(error), values=request.form), 400
        return render("signup", values={})

    @app.get("/duplas")
    def teams():
        return render("teams")

    @app.get("/grupos")
    def groups():
        return render("groups")

    @app.get("/mata-mata")
    def bracket():
        return render("bracket")

    @app.route("/organizador/entrar", methods=["GET", "POST"])
    def login():
        if is_organizer():
            return redirect(url_for("admin"))
        if request.method == "POST":
            address = request.remote_addr or "unknown"
            now = time.time()
            error = "Usuário ou senha incorretos."
            with storage.transaction(app.config["DATABASE"]) as db:
                db.execute("DELETE FROM login_attempt WHERE started < ?", (now - 900,))
                attempt = db.execute("SELECT * FROM login_attempt WHERE address = ?", (address,)).fetchone()
                if attempt and attempt["failures"] >= 5:
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
                db.execute("INSERT INTO login_attempt (address, failures, started) VALUES (?, 1, ?) "
                           "ON CONFLICT(address) DO UPDATE SET failures = failures + 1", (address, now))
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
