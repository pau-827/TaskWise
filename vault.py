# vault.py
import os
import stat
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from cryptography.fernet import Fernet, InvalidToken

# Load .env in project root
PROJECT_ROOT = Path(__file__).resolve().parent
ENV_PATH = PROJECT_ROOT / ".env"
VAULT_KEY_PATH = PROJECT_ROOT / ".vault_key"

# Load environment variables from .env (if present)
load_dotenv(dotenv_path=ENV_PATH)

# ---------------------------
# Key management
# ---------------------------
def _ensure_key() -> bytes:
    """
    Ensure a Fernet key exists in .vault_key (create if missing).
    Returns the raw key bytes.
    """
    if VAULT_KEY_PATH.exists():
        key = VAULT_KEY_PATH.read_bytes()
        # key is stored as the raw bytes of the base64 key
        return key
    else:
        # generate a secure key
        key = Fernet.generate_key()
        try:
            # write atomically
            tmp = VAULT_KEY_PATH.with_suffix(".tmp")
            tmp.write_bytes(key)
            # set permissions: owner read/write only where supported
            try:
                os.chmod(tmp, stat.S_IRUSR | stat.S_IWUSR)
            except Exception:
                # On Windows, chmod may be no-op; ignore
                pass
            tmp.replace(VAULT_KEY_PATH)
            try:
                os.chmod(VAULT_KEY_PATH, stat.S_IRUSR | stat.S_IWUSR)
            except Exception:
                pass
        except Exception:
            # fallback: write directly
            VAULT_KEY_PATH.write_bytes(key)
        return key


# Create/load the Fernet instance (singleton)
_KEY = _ensure_key()
_FERNET = Fernet(_KEY)


# ---------------------------
# Public API
# ---------------------------
def get_secret(key: str, default: Optional[str] = None) -> Optional[str]:
    """
    Retrieve a secret from environment (.env). If the env value is encrypted,
    it must be in the form: ENC(<fernet-token>) and this function will decrypt it.
    Otherwise the environment value is returned as-is.

    Returns default if the key is not set in the environment.
    """
    raw = os.getenv(key)
    if raw is None:
        return default

    raw = raw.strip()

    # Encrypted value wrapper: ENC(<token>)
    if raw.startswith("ENC(") and raw.endswith(")"):
        token = raw[4:-1]
        try:
            plain = _FERNET.decrypt(token.encode())
            return plain.decode()
        except (InvalidToken, Exception):
            # If decryption fails, raise an informative error so you can re-encrypt properly
            raise RuntimeError(f"Failed to decrypt secret for key '{key}'. The token might be invalid or the vault key changed.")
    else:
        # Plain text (ok for development; for production you should encrypt)
        return raw


def encrypt_value(plaintext: str) -> str:
    """
    Encrypt a plaintext string and return the value formatted for .env:
        ENC(<token>)
    Use this function or the CLI below to produce encrypted entries to put into .env.
    """
    token = _FERNET.encrypt(plaintext.encode()).decode()
    return f"ENC({token})"


# ---------------------------
# CLI helper (encrypt a value)
# ---------------------------
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python vault.py <secret-to-encrypt>")
        print("Example: python vault.py Admin123")
        sys.exit(1)

    secret = sys.argv[1]
    wrapped = encrypt_value(secret)
    print(wrapped)
    print("\nPaste the returned line as the value in your .env, for example:\n")
    print(f"ADMIN_DEFAULT_PASSWORD={wrapped}")