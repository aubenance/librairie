"""
LibrairieCI Pro - Serveur Backend
VERSION STABLE RAILWAY
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    DateTime,
    Boolean,
    ForeignKey,
    Text,
    func,
    desc
)

from sqlalchemy.orm import (
    declarative_base,
    sessionmaker,
    Session,
    relationship
)

from pydantic import BaseModel

from typing import Optional, List

from datetime import datetime, timedelta

import jwt
from jwt import ExpiredSignatureError, InvalidTokenError

import hashlib
import os

# ─────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────

SECRET_KEY = os.environ.get(
    "SECRET_KEY",
    "LibrairieCI_SECRET_2026"
)

ALGORITHM = "HS256"
TOKEN_EXPIRE_HOURS = 12

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "sqlite:///./librairie_ci.db"
)

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace(
        "postgres://",
        "postgresql://",
        1
    )

connect_args = {}

if "sqlite" in DATABASE_URL:
    connect_args = {
        "check_same_thread": False
    }

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

# ─────────────────────────────────────────
# BASE DE DONNÉES
# ─────────────────────────────────────────

class Utilisateur(Base):

    __tablename__ = "utilisateurs"

    id = Column(Integer, primary_key=True, index=True)

    nom = Column(String(100), nullable=False)

    prenom = Column(String(100), nullable=False)

    username = Column(String(50), unique=True, nullable=False)

    password = Column(String(255), nullable=False)

    role = Column(String(20), default="employe")

    actif = Column(Boolean, default=True)

    date_creation = Column(
        DateTime,
        default=datetime.utcnow
    )


class Article(Base):

    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)

    code = Column(String(50), unique=True, nullable=False)

    titre = Column(String(255), nullable=False)

    auteur = Column(String(255), default="")

    categorie = Column(String(100), default="")

    prix_achat = Column(Float, default=0)

    prix_vente = Column(Float, nullable=False)

    quantite = Column(Integer, default=0)

    description = Column(Text, default="")

    date_ajout = Column(
        DateTime,
        default=datetime.utcnow
    )


# Création tables
Base.metadata.create_all(bind=engine)

# ─────────────────────────────────────────
# SCHÉMAS
# ─────────────────────────────────────────

class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    token: str
    role: str
    nom_complet: str
    id: int


class ArticleCreate(BaseModel):
    code: str
    titre: str
    auteur: Optional[str] = ""
    categorie: Optional[str] = ""
    prix_achat: Optional[float] = 0
    prix_vente: float
    quantite: int
    description: Optional[str] = ""


class ArticleOut(ArticleCreate):
    id: int

    class Config:
        from_attributes = True


# ─────────────────────────────────────────
# SÉCURITÉ
# ─────────────────────────────────────────

def hash_password(password: str):

    return hashlib.sha256(
        (password + "LibrairieCI").encode()
    ).hexdigest()


def create_token(data: dict):

    payload = data.copy()

    payload["exp"] = datetime.utcnow() + timedelta(
        hours=TOKEN_EXPIRE_HOURS
    )

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(
        HTTPBearer()
    )
):

    try:

        payload = jwt.decode(
            credentials.credentials,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        return payload

    except ExpiredSignatureError:

        raise HTTPException(
            status_code=401,
            detail="Session expirée"
        )

    except InvalidTokenError:

        raise HTTPException(
            status_code=401,
            detail="Token invalide"
        )

    except Exception as e:

        raise HTTPException(
            status_code=401,
            detail=str(e)
        )


def require_admin(
    payload: dict = Depends(verify_token)
):

    if payload.get("role") != "admin":

        raise HTTPException(
            status_code=403,
            detail="Accès administrateur requis"
        )

    return payload


def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()

# ─────────────────────────────────────────
# DONNÉES PAR DÉFAUT
# ─────────────────────────────────────────

def init_data():

    db = SessionLocal()

    try:

        count = db.query(Utilisateur).count()

        if count == 0:

            admin = Utilisateur(
                nom="Admin",
                prenom="Système",
                username="admin",
                password=hash_password("admin123"),
                role="admin"
            )

            db.add(admin)

            db.add_all([

                Article(
                    code="LIV001",
                    titre="Notre Dame de Paris",
                    auteur="Victor Hugo",
                    categorie="Roman",
                    prix_achat=1500,
                    prix_vente=3500,
                    quantite=20
                ),

                Article(
                    code="LIV002",
                    titre="Le Petit Prince",
                    auteur="Saint-Exupéry",
                    categorie="Jeunesse",
                    prix_achat=1200,
                    prix_vente=2500,
                    quantite=15
                )

            ])

            db.commit()

            print("✅ Données initiales créées")

    except Exception as e:

        print("❌ Erreur init data :", e)

        db.rollback()

    finally:

        db.close()

# ─────────────────────────────────────────
# APPLICATION
# ─────────────────────────────────────────

app = FastAPI(
    title="LibrairieCI API",
    version="2.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():

    print("🚀 Démarrage serveur LibrairieCI")

    init_data()

    print("✅ Serveur prêt")

# ─────────────────────────────────────────
# ROUTES SYSTÈME
# ─────────────────────────────────────────

@app.get("/")
def root():

    return {
        "message": "LibrairieCI API ONLINE"
    }


@app.get("/health")
def health():

    return {
        "status": "ok",
        "app": "LibrairieCI",
        "version": "2.0"
    }

# ─────────────────────────────────────────
# AUTH
# ─────────────────────────────────────────

@app.post("/auth/login")
def login(
    data: LoginRequest,
    db: Session = Depends(get_db)
):

    try:

        print("══════════════════════════════")
        print("LOGIN :", data.username)

        user = db.query(Utilisateur).filter(
            Utilisateur.username == data.username,
            Utilisateur.password == hash_password(data.password),
            Utilisateur.actif == True
        ).first()

        if not user:

            print("❌ LOGIN INCORRECT")

            raise HTTPException(
                status_code=401,
                detail="Identifiants incorrects"
            )

        token = create_token({
            "sub": user.username,
            "role": user.role,
            "id": user.id
        })

        print("✅ LOGIN OK")

        return {
            "token": token,
            "role": user.role,
            "nom_complet": f"{user.prenom} {user.nom}",
            "id": user.id
        }

    except HTTPException:
        raise

    except Exception as e:

        print("❌ ERREUR LOGIN :", e)

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@app.get("/auth/me")
def me(
    payload: dict = Depends(verify_token)
):

    return payload

# ─────────────────────────────────────────
# ARTICLES
# ─────────────────────────────────────────

@app.get(
    "/articles",
    response_model=List[ArticleOut]
)
def get_articles(
    q: Optional[str] = None,
    db: Session = Depends(get_db),
    payload: dict = Depends(verify_token)
):

    query = db.query(Article)

    if q:

        like = f"%{q}%"

        query = query.filter(
            Article.titre.ilike(like)
        )

    return query.order_by(
        Article.titre
    ).all()


@app.post(
    "/articles",
    response_model=ArticleOut
)
def create_article(
    data: ArticleCreate,
    db: Session = Depends(get_db),
    payload: dict = Depends(require_admin)
):

    article = Article(**data.model_dump())

    db.add(article)

    db.commit()

    db.refresh(article)

    return article

# ─────────────────────────────────────────
# LANCEMENT
# ─────────────────────────────────────────

if __name__ == "__main__":

    import uvicorn

    port = int(
        os.environ.get("PORT", 8000)
    )

    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=port,
        reload=False
    )