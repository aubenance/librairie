"""
LibrairieCI Pro - Serveur Backend
VERSION FINALE STABLE RAILWAY
"""

from fastapi import FastAPI, HTTPException, Depends, Body
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
    Text
)

from sqlalchemy.orm import (
    declarative_base,
    sessionmaker,
    Session
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

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "sqlite:///./librairie_ci.db"
)

# PostgreSQL Railway
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
# MODELS
# ─────────────────────────────────────────

class Utilisateur(Base):

    __tablename__ = "utilisateurs"

    id = Column(Integer, primary_key=True)

    nom = Column(String(100))

    prenom = Column(String(100))

    username = Column(
        String(100),
        unique=True
    )

    password = Column(String(255))

    role = Column(String(20))

    actif = Column(Boolean, default=True)

    date_creation = Column(
        DateTime,
        default=datetime.utcnow
    )


class Article(Base):

    __tablename__ = "articles"

    id = Column(Integer, primary_key=True)

    code = Column(String(50), unique=True)

    titre = Column(String(255))

    auteur = Column(String(255))

    categorie = Column(String(100))

    prix_achat = Column(Float)

    prix_vente = Column(Float)

    quantite = Column(Integer)

    description = Column(Text)

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


class ArticleCreate(BaseModel):

    code: str
    titre: str
    auteur: Optional[str] = ""
    categorie: Optional[str] = ""
    prix_achat: float = 0
    prix_vente: float
    quantite: int
    description: Optional[str] = ""


class ArticleOut(ArticleCreate):

    id: int

    class Config:
        from_attributes = True

# ─────────────────────────────────────────
# UTILITAIRES
# ─────────────────────────────────────────

def hash_password(password: str):

    return hashlib.sha256(
        (password + "LibrairieCI").encode()
    ).hexdigest()


def create_token(data: dict):

    payload = data.copy()

    payload["exp"] = datetime.utcnow() + timedelta(
        hours=12
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


def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()

# ─────────────────────────────────────────
# DONNÉES INITIALES
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
                role="admin",
                actif=True
            )

            db.add(admin)

            db.commit()

            print("✅ ADMIN CRÉÉ")

    except Exception as e:

        print("❌ INIT ERROR :", e)

        db.rollback()

    finally:

        db.close()

# ─────────────────────────────────────────
# APP
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

    print("🚀 SERVEUR LIBRAIRIECI")

    init_data()

    print("✅ SERVEUR PRÊT")

# ─────────────────────────────────────────
# ROUTES SYSTÈME
# ─────────────────────────────────────────

@app.get("/")
def root():

    return {
        "message": "LibrairieCI ONLINE"
    }


@app.get("/health")
def health():

    return {
        "status": "ok",
        "app": "LibrairieCI",
        "version": "2.0"
    }

# ─────────────────────────────────────────
# AUTHENTIFICATION
# ─────────────────────────────────────────

@app.post("/auth/login")
async def login(data: dict = Body(...)):

    try:

        username = data.get("username")
        password = data.get("password")

        print("══════════════════════════")
        print("LOGIN :", username)

        db = SessionLocal()

        user = db.query(Utilisateur).filter(
            Utilisateur.username == username,
            Utilisateur.password == hash_password(password),
            Utilisateur.actif == True
        ).first()

        if not user:

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

        print("❌ LOGIN ERROR :", e)

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

        query = query.filter(
            Article.titre.ilike(f"%{q}%")
        )

    return query.all()


@app.post(
    "/articles",
    response_model=ArticleOut
)
def create_article(
    data: ArticleCreate,
    db: Session = Depends(get_db),
    payload: dict = Depends(verify_token)
):

    article = Article(**data.model_dump())

    db.add(article)

    db.commit()

    db.refresh(article)

    return article

# ─────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8080)),
        reload=False
    )