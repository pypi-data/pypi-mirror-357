from dotenv import load_dotenv, set_key
from cryptography.fernet import Fernet
import os
from pathlib import Path

# region TODOs for future implementations:
# TODO [ ] Log errors instead of printing them (es. con logging module)
# TODO [ ] Raise custom exceptions for missing or invalid keys
# TODO [ ] Aggiungere supporto per rotazione chiavi e versionamento
# TODO [ ] Verificare validità della chiave (lunghezza, base64) prima di usarla
# TODO [ ] Creare un wrapper per criptare/dcriptare interi oggetti o dizionari
# endregion


DOTENV_PATH = Path(os.getenv("APPDATA")) / "my_app" / ".env"


def get_or_create_fernet(dotenv_path=DOTENV_PATH):
    if not dotenv_path.exists():
        dotenv_path.touch()

    load_dotenv(dotenv_path, override=True)
    key = os.getenv("FERNET_KEY")

    if not key:
        key = Fernet.generate_key().decode()
        set_key(str(dotenv_path), "FERNET_KEY", key)
        os.environ["FERNET_KEY"] = key

    return Fernet(key.encode())


def encrypt(text: str) -> str:
    """
    Encrypt a string using Fernet.
    """
    return get_or_create_fernet().encrypt(text.encode()).decode()


def decrypt(token: str) -> str:
    """
    Decrypt a Fernet-encrypted string.
    """
    return get_or_create_fernet().decrypt(token.encode()).decode()
