# -*- coding: utf-8 -*-
"""
LibrairieCI - Client API
"""
import requests, json, os

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
DEFAULT_CONFIG = {
    "server_url": "https://librairie-production-4481.up.railway.app",
    "timeout": 15
}

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                DEFAULT_CONFIG.update(json.load(f))
        except Exception:
            pass
    return DEFAULT_CONFIG

class Session:
    token: str = ""; role: str = ""; nom_complet: str = ""; user_id: int = 0; config: dict = {}
    @property
    def is_admin(self): return self.role == "admin"
    @property
    def headers(self): return {"Authorization": f"Bearer {self.token}"} if self.token else {}

session = Session()
session.config = load_config()

class APIClient:

    @staticmethod
    def _url(path): return session.config.get("server_url","").rstrip("/") + path
    @staticmethod
    def _timeout(): return session.config.get("timeout", 15)

    @classmethod
    def _get(cls, path, params=None):
        try:
            r = requests.get(cls._url(path), headers=session.headers, params=params, timeout=cls._timeout())
            r.raise_for_status()
            return {"ok": True, "data": r.json()}
        except requests.exceptions.ConnectionError:
            return {"ok": False, "error": "Connexion impossible au serveur."}
        except requests.exceptions.Timeout:
            return {"ok": False, "error": "Le serveur ne repond pas (timeout)."}
        except requests.exceptions.HTTPError as e:
            try: detail = r.json().get("detail", str(e))
            except: detail = str(e)
            return {"ok": False, "error": detail}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    @classmethod
    def _post(cls, path, data=None, auth=True):
        try:
            headers = session.headers if auth else {}
            r = requests.post(cls._url(path), headers=headers, json=data, timeout=cls._timeout())
            r.raise_for_status()
            return {"ok": True, "data": r.json()}
        except requests.exceptions.ConnectionError:
            return {"ok": False, "error": "Connexion impossible au serveur."}
        except requests.exceptions.Timeout:
            return {"ok": False, "error": "Le serveur ne repond pas (timeout)."}
        except requests.exceptions.HTTPError as e:
            try: detail = r.json().get("detail", str(e))
            except: detail = str(e)
            return {"ok": False, "error": detail}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    @classmethod
    def _put(cls, path, data=None):
        try:
            r = requests.put(cls._url(path), headers=session.headers, json=data, timeout=cls._timeout())
            r.raise_for_status()
            return {"ok": True, "data": r.json()}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    @classmethod
    def _delete(cls, path):
        try:
            r = requests.delete(cls._url(path), headers=session.headers, timeout=cls._timeout())
            r.raise_for_status()
            return {"ok": True, "data": r.json()}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    # AUTH
    @classmethod
    def login(cls, username, password):
        result = cls._post("/auth/login", {"username": username, "password": password}, auth=False)
        if result["ok"]:
            d = result["data"]
            session.token = d.get("token",""); session.role = d.get("role","")
            session.nom_complet = d.get("nom_complet",""); session.user_id = d.get("id",0)
        return result

    @classmethod
    def test_connection(cls):
        try: return requests.get(cls._url("/health"), timeout=5).status_code == 200
        except: return False

    # ARTICLES
    @classmethod
    def get_articles(cls, q=""): return cls._get("/articles", {"q": q} if q else None)
    @classmethod
    def get_article(cls, aid): return cls._get(f"/articles/{aid}")
    @classmethod
    def create_article(cls, data): return cls._post("/articles", data)
    @classmethod
    def update_article(cls, aid, data): return cls._put(f"/articles/{aid}", data)
    @classmethod
    def delete_article(cls, aid): return cls._delete(f"/articles/{aid}")

    # VENTES
    @classmethod
    def create_vente(cls, lignes, total):
        return cls._post("/ventes", {"lignes": lignes, "total": total})
    @classmethod
    def get_ventes(cls, debut=None, fin=None):
        params = {}
        if debut: params["debut"] = debut
        if fin:   params["fin"]   = fin
        return cls._get("/ventes", params or None)
    @classmethod
    def get_vente_details(cls, vid): return cls._get(f"/ventes/{vid}/details")

    # STATS
    @classmethod
    def get_stats(cls): return cls._get("/stats/dashboard")
    @classmethod
    def get_top_articles(cls): return cls._get("/stats/top_articles")

    # USERS
    @classmethod
    def get_users(cls): return cls._get("/users")
    @classmethod
    def create_user(cls, data): return cls._post("/users", data)
    @classmethod
    def update_user(cls, uid, data): return cls._put(f"/users/{uid}", data)
    @classmethod
    def reset_password(cls, uid, pwd): return cls._put(f"/users/{uid}/password", {"password": pwd})
