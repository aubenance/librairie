"""
LibrairieCI - Client API
Version finale stable Railway
"""

import requests
import urllib3
import json
import os

# Désactiver les warnings SSL Railway/Windows
urllib3.disable_warnings(
    urllib3.exceptions.InsecureRequestWarning
)

# ─────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────

CONFIG_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "config.json"
)

DEFAULT_CONFIG = {
    "server_url": "https://librairie-production-eaf9.up.railway.app",
    "app_name": "LibrairieCI",
    "version": "2.0",
    "timeout": 15
}


def load_config() -> dict:

    if os.path.exists(CONFIG_FILE):

        try:

            with open(
                CONFIG_FILE,
                "r",
                encoding="utf-8"
            ) as f:

                cfg = json.load(f)

                DEFAULT_CONFIG.update(cfg)

        except Exception as e:

            print("Erreur config :", e)

    return DEFAULT_CONFIG


def save_config(cfg: dict):

    try:

        with open(
            CONFIG_FILE,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                cfg,
                f,
                indent=2
            )

    except Exception as e:

        print("Erreur sauvegarde :", e)

# ─────────────────────────────────────────
# SESSION
# ─────────────────────────────────────────

class Session:

    token = ""
    role = ""
    nom_complet = ""
    user_id = 0
    config = {}

    @property
    def is_admin(self):

        return self.role == "admin"

    @property
    def headers(self):

        if self.token:

            return {
                "Authorization": f"Bearer {self.token}"
            }

        return {}


session = Session()
session.config = load_config()

# ─────────────────────────────────────────
# CLIENT API
# ─────────────────────────────────────────

class APIClient:

    # ─────────────────────────────────────
    # OUTILS
    # ─────────────────────────────────────

    @staticmethod
    def _base_url():

        return session.config.get(
            "server_url",
            DEFAULT_CONFIG["server_url"]
        ).rstrip("/")

    @classmethod
    def _url(cls, path: str):

        return f"{cls._base_url()}{path}"

    @staticmethod
    def _timeout():

        return session.config.get(
            "timeout",
            15
        )

    # ─────────────────────────────────────
    # TEST CONNEXION
    # ─────────────────────────────────────

    @classmethod
    def test_connection(cls):

        try:

            url = cls._url("/health")

            print("══════════════════════════")
            print("TEST SERVEUR")
            print("URL :", url)

            response = requests.get(
                url,
                timeout=10,
                verify=False
            )

            print("STATUS :", response.status_code)
            print("REPONSE :", response.text)

            return response.status_code == 200

        except Exception as e:

            print("ERREUR CONNEXION :", e)

            return False

    # ─────────────────────────────────────
    # AUTHENTIFICATION
    # ─────────────────────────────────────

    @classmethod
    def login(
        cls,
        username: str,
        password: str
    ):

        try:

            url = cls._url("/auth/login")

            print("══════════════════════════")
            print("LOGIN")
            print("URL :", url)

            response = requests.post(
                url,
                json={
                    "username": username,
                    "password": password
                },
                timeout=15,
                verify=False
            )

            print("STATUS :", response.status_code)
            print("REPONSE :", response.text)

            response.raise_for_status()

            data = response.json()

            session.token = data.get("token", "")
            session.role = data.get("role", "")
            session.nom_complet = data.get(
                "nom_complet",
                ""
            )
            session.user_id = data.get("id", 0)

            return {
                "ok": True,
                "data": data
            }

        except requests.exceptions.HTTPError:

            try:

                detail = response.json().get(
                    "detail",
                    "Erreur connexion"
                )

            except Exception:

                detail = "Erreur HTTP"

            return {
                "ok": False,
                "error": detail
            }

        except requests.exceptions.ConnectionError:

            return {
                "ok": False,
                "error": "Impossible de contacter le serveur"
            }

        except requests.exceptions.Timeout:

            return {
                "ok": False,
                "error": "Le serveur ne répond pas"
            }

        except Exception as e:

            return {
                "ok": False,
                "error": str(e)
            }

    # ─────────────────────────────────────
    # GET
    # ─────────────────────────────────────

    @classmethod
    def _get(
        cls,
        path: str,
        params: dict = None
    ):

        try:

            response = requests.get(
                cls._url(path),
                headers=session.headers,
                params=params,
                timeout=cls._timeout(),
                verify=False
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
    # POST
    # ─────────────────────────────────────

    @classmethod
    def _post(
        cls,
        path: str,
        data: dict = None
    ):

        try:

            response = requests.post(
                cls._url(path),
                headers=session.headers,
                json=data,
                timeout=cls._timeout(),
                verify=False
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
    # PUT
    # ─────────────────────────────────────

    @classmethod
    def _put(
        cls,
        path: str,
        data: dict = None
    ):

        try:

            response = requests.put(
                cls._url(path),
                headers=session.headers,
                json=data,
                timeout=cls._timeout(),
                verify=False
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
    def _delete(
        cls,
        path: str
    ):

        try:

            response = requests.delete(
                cls._url(path),
                headers=session.headers,
                timeout=cls._timeout(),
                verify=False
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
    # ARTICLES
    # ─────────────────────────────────────

    @classmethod
    def get_articles(cls, q=""):

        params = {}

        if q:
            params["q"] = q

        return cls._get(
            "/articles",
            params=params
        )

    @classmethod
    def create_article(
        cls,
        data: dict
    ):

        return cls._post(
            "/articles",
            data
        )

    @classmethod
    def update_article(
        cls,
        article_id: int,
        data: dict
    ):

        return cls._put(
            f"/articles/{article_id}",
            data
        )

    @classmethod
    def delete_article(
        cls,
        article_id: int
    ):

        return cls._delete(
            f"/articles/{article_id}"
        )

    # ─────────────────────────────────────
    # STATS
    # ─────────────────────────────────────

    @classmethod
    def get_stats(cls):

        return cls._get(
            "/stats/dashboard"
        )

    @classmethod
    def get_top_articles(cls):

        return cls._get(
            "/stats/top_articles"
        )

    # ─────────────────────────────────────
    # UTILISATEURS
    # ─────────────────────────────────────

    @classmethod
    def get_users(cls):

        return cls._get("/users")

    @classmethod
    def create_user(
        cls,
        data: dict
    ):

        return cls._post(
            "/users",
            data
        )

    @classmethod
    def update_user(
        cls,
        user_id: int,
        data: dict
    ):

        return cls._put(
            f"/users/{user_id}",
            data
        )

    @classmethod
    def reset_password(
        cls,
        user_id: int,
        password: str
    ):

        return cls._put(
            f"/users/{user_id}/password",
            {
                "password": password
            }
        )