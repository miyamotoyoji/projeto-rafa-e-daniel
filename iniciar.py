"""Atalho de primeira execução: python iniciar.py (Python 3.11 ou mais novo)."""
from pathlib import Path
import os
import sqlite3
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
VENV = ROOT / ".venv"
PYTHON = VENV / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def run(*args):
    subprocess.run([str(PYTHON), *args], cwd=ROOT, check=True)


def main():
    if sys.version_info < (3, 11):
        raise SystemExit("Instale Python 3.11 ou mais novo para continuar.")
    if not PYTHON.exists():
        print("Preparando o ambiente do projeto…", flush=True)
        subprocess.run([sys.executable, "-m", "venv", str(VENV)], check=True)
    check = subprocess.run(
        [str(PYTHON), "-c",
         "from importlib.metadata import version; "
         "assert version('Flask') == '3.1.2'; assert version('waitress') == '3.0.2'"],
        capture_output=True,
    )
    if check.returncode:
        print("Instalando dependências…", flush=True)
        run("-m", "pip", "install", "-r", "requirements.txt")
    database = ROOT / "instance" / "championship.sqlite3"
    configured = False
    if database.exists():
        db = sqlite3.connect(database)
        try:
            configured = bool(db.execute("SELECT id FROM organizer WHERE id = 1").fetchone())
        except sqlite3.OperationalError:
            pass
        finally:
            db.close()
    if not configured:
        print("\nCrie o acesso do organizador. A senha não aparece enquanto você digita.", flush=True)
        run("-m", "flask", "--app", "app", "init-admin")
    print("\nAbra http://127.0.0.1:5173 no navegador.", flush=True)
    print("Entre em Organização para criar o campeonato. Para encerrar, pressione Ctrl+C.\n", flush=True)
    run("-m", "waitress", "--host=127.0.0.1", "--port=5173", "--call", "app:create_app")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nServidor encerrado.")
    except subprocess.CalledProcessError as error:
        raise SystemExit(f"Não foi possível concluir a etapa (código {error.returncode}). Confira a mensagem acima.")

