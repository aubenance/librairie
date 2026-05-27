"""
LibrairieCI - Client API
Gère toutes les communications avec le serveur
"""

import requests
import json
import os
from typing import Optional

# ─────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────

CONFIG_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "config.json"
)

DEFAULT_CONFIG = {
    "server_url": "https://librairie-production-23ef.up.railway.app",
    "app_name": "LibrairieCI",
    "version": "2.0",
    "timeout": 15
}


def load_config() -> dict:
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                DEFAULT_CONFIG.update(cfg)
        except Exception as e:
            print("Erreur chargement config :", e)

    return DEFAULT_CONFIG


def save_config(cfg: dict):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2)
    except Exception as e:
        print("Erreur sauvegarde config :", e)


# ─────────────────────────────────────────
# SESSION
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
        if self.token:
            return {
                "Authorization": f"Bearer {self.token}"
            }
        return {}


session = Session()
session.config = load_config()


# ─────────────────────────────────────────
# API CLIENT
# ─────────────────────────────────────────

class APIClient:

    # ─────────────────────────────────────
    # OUTILS INTERNES
    # ─────────────────────────────────────

    @staticmethod
    def _base_url() -> str:
        return session.config.get(
            "server_url",
            DEFAULT_CONFIG["server_url"]
        ).rstrip("/")

    @classmethod
    def _url(cls, path: str) -> str:
        return f"{cls._base_url()}{path}"

    @staticmethod
    def _timeout() -> int:
        return session.config.get("timeout", 15)

    # ─────────────────────────────────────
    # GET
    # ─────────────────────────────────────

    @classmethod
    def _get(cls, path: str, params: dict = None) -> dict:
        try:
            response = requests.get(
                cls._url(path),
                headers=session.headers,
                params=params,
                timeout=cls._timeout()
            )

            response.raise_for_status()

            return {
                "ok": True,
                "data": response.json()
            }

        except requests.exceptions.ConnectionError:
            return {
                "ok": False,
                "error": "❌ Impossible de contacter le serveur."
            }

        except requests.exceptions.Timeout:
            return {
                "ok": False,
                "error": "⏱ Le serveur met trop de temps à répondre."
            }

        except requests.exceptions.HTTPError:
            try:
                detail = response.json().get("detail", "Erreur serveur")
            except Exception:
                detail = "Erreur HTTP"

            return {
                "ok": False,
                "error": detail
            }

        except Exception as e:
            return {
                "ok": False,
                "error": str(e)
            }

    # ─────────────────────────────────────
    # POST
    # ─────────────────────────────────────

    @classmethod
    def _post(cls, path: str, data: dict = None, auth: bool = True) -> dict:
        try:
            headers = session.headers if auth else {}

            response = requests.post(
                cls._url(path),
                headers=headers,
                json=data,
                timeout=cls._timeout()
            )

            response.raise_for_status()

            return {
                "ok": True,
                "data": response.json()
            }

        except requests.exceptions.ConnectionError:
            return {
                "ok": False,
                "error": "❌ Impossible de contacter le serveur."
            }

        except requests.exceptions.Timeout:
            return {
                "ok": False,
                "error": "⏱ Le serveur ne répond pas."
            }

        except requests.exceptions.HTTPError:
            try:
                detail = response.json().get("detail", "Erreur serveur")
            except Exception:
                detail = "Erreur HTTP"

            return {
                "ok": False,
                "error": detail
            }

        except Exception as e:
            return {
                "ok": False,
                "error": str(e)
            }

    # ─────────────────────────────────────
    # PUT
    # ─────────────────────────────────────

    @classmethod
    def _put(cls, path: str, data: dict = None) -> dict:
        try:
            response = requests.put(
                cls._url(path),
                headers=session.headers,
                json=data,
                timeout=cls._timeout()
            )

            response.raise_for_status()

            return {
                "ok": True,
                "data": response.json()
            }

        except Exception as e:
            return {
                "ok": False,
                "error": str(e)
            }

    # ─────────────────────────────────────
    # DELETE
    # ─────────────────────────────────────

    @classmethod
    def _delete(cls, path: str) -> dict:
        try:
            response = requests.delete(
                cls._url(path),
                headers=session.headers,
                timeout=cls._timeout()
            )

            response.raise_for_status()

            return {
                "ok": True,
                "data": response.json()
            }

        except Exception as e:
            return {
                "ok": False,
                "error": str(e)
            }

    # ─────────────────────────────────────
    # TEST CONNEXION
    # ─────────────────────────────────────

    @classmethod
    def test_connection(cls) -> bool:
        """
        Vérifie si le serveur Railway répond correctement
        """

        try:
            url = cls._url("/health")

            print("Test connexion :", url)

            response = requests.get(
                url,
                timeout=10
            )

            print("Status code :", response.status_code)
            print("Réponse :", response.text)

            return response.status_code == 200

        except Exception as e:
            print("Erreur connexion serveur :", e)
            return False

    # ─────────────────────────────────────
    # AUTHENTIFICATION
    # ─────────────────────────────────────

    @classmethod
    def login(cls, username: str, password: str) -> dict:

        result = cls._post(
            "/auth/login",
            {
                "username": username,
                "password": password
            },
            auth=False
        )

        if result["ok"]:
            data = result["data"]

            session.token = data["token"]
            session.role = data["role"]
            session.nom_complet = data["nom_complet"]
            session.user_id = data["id"]

        return result

    # ─────────────────────────────────────
    # ARTICLES
    # ─────────────────────────────────────

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

    # ─────────────────────────────────────
    # VENTES
    # ─────────────────────────────────────

    @classmethod
    def create_vente(cls, lignes: list, total: float) -> dict:
        return cls._post(
            "/ventes",
            {
                "lignes": lignes,
                "total": total
            }
        )

    @classmethod
    def get_ventes(cls, debut: str = None, fin: str = None) -> dict:
        params = {}

        if debut:
            params["debut"] = debut

        if fin:
            params["fin"] = fin

        return cls._get("/ventes", params or None)

    @classmethod
    def get_vente_details(cls, vente_id: int) -> dict:
        return cls._get(f"/ventes/{vente_id}/details")

    # ─────────────────────────────────────
    # STATS
    # ─────────────────────────────────────

    @classmethod
    def get_stats(cls) -> dict:
        return cls._get("/stats/dashboard")

    @classmethod
    def get_top_articles(cls) -> dict:
        return cls._get("/stats/top_articles")

    # ─────────────────────────────────────
    # UTILISATEURS
    # ─────────────────────────────────────

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
        return cls._put(
            f"/users/{user_id}/password",
            {"password": password}
        )