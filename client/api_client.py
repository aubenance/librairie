"""
LibrairieCI - Client API
Gère toutes les communications avec le serveur
"""

import requests
import json
import os
from typing import Optional

# ─────────────────────────────────────────
#  CONFIG (modifiable via config.json)
# ─────────────────────────────────────────

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

DEFAULT_CONFIG = {
    "server_url": "http://localhost:8000",
    "app_name": "LibrairieCI",
    "version": "2.0",
    "timeout": 10
}

def load_config() -> dict:
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                cfg = json.load(f)
                DEFAULT_CONFIG.update(cfg)
        except Exception:
            pass
    return DEFAULT_CONFIG

def save_config(cfg: dict):
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f, indent=2)


# ─────────────────────────────────────────
#  SESSION
# ─────────────────────────────────────────

class Session:
    token: str = ""
    role: str = ""
    nom_complet: str = ""
    user_id: int = 0
    config: dict = {}

    @property
    def is_admin(self) -> bool:
        return self.role == "admin"

    @property
    def headers(self) -> dict:
        return {"Authorization": f"Bearer {self.token}"}

session = Session()
session.config = load_config()


# ─────────────────────────────────────────
#  CLASSE PRINCIPALE API
# ─────────────────────────────────────────

class APIClient:

    @staticmethod
    def _url(path: str) -> str:
        base = session.config.get("server_url", "http://localhost:8000").rstrip("/")
        return f"{base}{path}"

    @staticmethod
    def _timeout() -> int:
        return session.config.get("timeout", 10)

    @classmethod
    def _get(cls, path: str, params: dict = None) -> dict:
        try:
            r = requests.get(cls._url(path), headers=session.headers,
                             params=params, timeout=cls._timeout())
            r.raise_for_status()
            return {"ok": True, "data": r.json()}
        except requests.exceptions.ConnectionError:
            return {"ok": False, "error": "❌ Connexion impossible au serveur.\nVérifiez votre connexion internet."}
        except requests.exceptions.Timeout:
            return {"ok": False, "error": "⏱ Le serveur met trop de temps à répondre."}
        except requests.exceptions.HTTPError as e:
            try:
                detail = r.json().get("detail", str(e))
            except Exception:
                detail = str(e)
            return {"ok": False, "error": detail}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    @classmethod
    def _post(cls, path: str, data: dict = None, auth: bool = True) -> dict:
        try:
            headers = session.headers if auth else {}
            r = requests.post(cls._url(path), headers=headers,
                              json=data, timeout=cls._timeout())
            r.raise_for_status()
            return {"ok": True, "data": r.json()}
        except requests.exceptions.ConnectionError:
            return {"ok": False, "error": "❌ Connexion impossible au serveur.\nVérifiez votre connexion internet."}
        except requests.exceptions.Timeout:
            return {"ok": False, "error": "⏱ Le serveur ne répond pas."}
        except requests.exceptions.HTTPError as e:
            try:
                detail = r.json().get("detail", str(e))
            except Exception:
                detail = str(e)
            return {"ok": False, "error": detail}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    @classmethod
    def _put(cls, path: str, data: dict = None) -> dict:
        try:
            r = requests.put(cls._url(path), headers=session.headers,
                             json=data, timeout=cls._timeout())
            r.raise_for_status()
            return {"ok": True, "data": r.json()}
        except requests.exceptions.ConnectionError:
            return {"ok": False, "error": "❌ Connexion impossible au serveur."}
        except requests.exceptions.HTTPError as e:
            try:
                detail = r.json().get("detail", str(e))
            except Exception:
                detail = str(e)
            return {"ok": False, "error": detail}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    @classmethod
    def _delete(cls, path: str) -> dict:
        try:
            r = requests.delete(cls._url(path), headers=session.headers, timeout=cls._timeout())
            r.raise_for_status()
            return {"ok": True, "data": r.json()}
        except requests.exceptions.HTTPError as e:
            try:
                detail = r.json().get("detail", str(e))
            except Exception:
                detail = str(e)
            return {"ok": False, "error": detail}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    # ── AUTH ──────────────────────────────

    @classmethod
    def login(cls, username: str, password: str) -> dict:
        result = cls._post("/auth/login", {"username": username, "password": password}, auth=False)
        if result["ok"]:
            d = result["data"]
            session.token      = d["token"]
            session.role       = d["role"]
            session.nom_complet = d["nom_complet"]
            session.user_id    = d["id"]
        return result

    @classmethod
    def test_connection(cls) -> bool:
        try:
            r = requests.get(cls._url("/health"), timeout=5)
            return r.status_code == 200
        except Exception:
            return False

    # ── ARTICLES ─────────────────────────

    @classmethod
    def get_articles(cls, q: str = "") -> dict:
        params = {"q": q} if q else None
        return cls._get("/articles", params=params)

    @classmethod
    def get_article(cls, article_id: int) -> dict:
        return cls._get(f"/articles/{article_id}")

    @classmethod
    def create_article(cls, data: dict) -> dict:
        return cls._post("/articles", data)

    @classmethod
    def update_article(cls, article_id: int, data: dict) -> dict:
        return cls._put(f"/articles/{article_id}", data)

    @classmethod
    def delete_article(cls, article_id: int) -> dict:
        return cls._delete(f"/articles/{article_id}")

    # ── VENTES ───────────────────────────

    @classmethod
    def create_vente(cls, lignes: list, total: float) -> dict:
        return cls._post("/ventes", {"lignes": lignes, "total": total})

    @classmethod
    def get_ventes(cls, debut: str = None, fin: str = None) -> dict:
        params = {}
        if debut: params["debut"] = debut
        if fin:   params["fin"]   = fin
        return cls._get("/ventes", params or None)

    @classmethod
    def get_vente_details(cls, vente_id: int) -> dict:
        return cls._get(f"/ventes/{vente_id}/details")

    # ── STATS ────────────────────────────

    @classmethod
    def get_stats(cls) -> dict:
        return cls._get("/stats/dashboard")

    @classmethod
    def get_top_articles(cls) -> dict:
        return cls._get("/stats/top_articles")

    # ── UTILISATEURS ─────────────────────

    @classmethod
    def get_users(cls) -> dict:
        return cls._get("/users")

    @classmethod
    def create_user(cls, data: dict) -> dict:
        return cls._post("/users", data)

    @classmethod
    def update_user(cls, user_id: int, data: dict) -> dict:
        return cls._put(f"/users/{user_id}", data)

    @classmethod
    def reset_password(cls, user_id: int, password: str) -> dict:
        return cls._put(f"/users/{user_id}/password", {"password": password})
