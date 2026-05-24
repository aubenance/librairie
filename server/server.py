"""
LibrairieCI - Serveur Backend (FastAPI)
Hébergeable sur Railway / Render (gratuit)
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
import jwt
import hashlib, os, json

# ─────────────────────────────────────────
#  CONFIG
# ─────────────────────────────────────────
SECRET_KEY = os.environ.get("SECRET_KEY", "LibrairieCI_SuperSecretKey_2024")
ALGORITHM  = "HS256"
TOKEN_EXPIRE_HOURS = 12

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./librairie_ci.db")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ─────────────────────────────────────────
#  MODÈLES SQLAlchemy
# ─────────────────────────────────────────

class Utilisateur(Base):
    __tablename__ = "utilisateurs"
    id         = Column(Integer, primary_key=True, index=True)
    nom        = Column(String(100), nullable=False)
    prenom     = Column(String(100), nullable=False)
    username   = Column(String(50), unique=True, nullable=False)
    password   = Column(String(200), nullable=False)
    role       = Column(String(20), default="employe")
    actif      = Column(Boolean, default=True)
    date_creation = Column(DateTime, default=datetime.utcnow)

class Article(Base):
    __tablename__ = "articles"
    id          = Column(Integer, primary_key=True, index=True)
    code        = Column(String(50), unique=True, nullable=False)
    titre       = Column(String(200), nullable=False)
    auteur      = Column(String(150), default="")
    categorie   = Column(String(100), default="")
    prix_achat  = Column(Float, default=0)
    prix_vente  = Column(Float, nullable=False)
    quantite    = Column(Integer, default=0)
    description = Column(Text, default="")
    date_ajout  = Column(DateTime, default=datetime.utcnow)
    modifie_le  = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Vente(Base):
    __tablename__ = "ventes"
    id          = Column(Integer, primary_key=True, index=True)
    numero      = Column(String(50), unique=True)
    date_vente  = Column(DateTime, default=datetime.utcnow)
    id_employe  = Column(Integer, ForeignKey("utilisateurs.id"))
    total       = Column(Float, nullable=False)
    employe     = relationship("Utilisateur")
    details     = relationship("DetailVente", back_populates="vente")

class DetailVente(Base):
    __tablename__ = "detail_ventes"
    id            = Column(Integer, primary_key=True, index=True)
    id_vente      = Column(Integer, ForeignKey("ventes.id"))
    id_article    = Column(Integer, ForeignKey("articles.id"))
    quantite      = Column(Integer, nullable=False)
    prix_unitaire = Column(Float, nullable=False)
    vente         = relationship("Vente", back_populates="details")
    article       = relationship("Article")

Base.metadata.create_all(bind=engine)

# ─────────────────────────────────────────
#  SCHEMAS Pydantic
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
    modifie_le: Optional[datetime] = None
    class Config: from_attributes = True

class LigneVenteIn(BaseModel):
    id_article: int
    quantite: int
    prix_unitaire: float

class VenteCreate(BaseModel):
    lignes: List[LigneVenteIn]
    total: float

class UtilisateurCreate(BaseModel):
    nom: str
    prenom: str
    username: str
    password: str
    role: str = "employe"

class UtilisateurUpdate(BaseModel):
    nom: str
    prenom: str
    role: str
    actif: bool

class UtilisateurOut(BaseModel):
    id: int
    nom: str
    prenom: str
    username: str
    role: str
    actif: bool
    class Config: from_attributes = True

# ─────────────────────────────────────────
#  AUTH
# ─────────────────────────────────────────

def hash_password(pwd: str) -> str:
    return hashlib.sha256((pwd + "LibrairieCI_Salt").encode()).hexdigest()

def create_token(data: dict) -> str:
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(hours=TOKEN_EXPIRE_HOURS)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())) -> dict:
    try:
        return jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expiré, reconnectez-vous")
    except Exception:
        raise HTTPException(status_code=401, detail="Token invalide")

def require_admin(payload: dict = Depends(verify_token)):
    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Accès réservé à l'administrateur")
    return payload

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ─────────────────────────────────────────
#  DONNÉES PAR DÉFAUT
# ─────────────────────────────────────────

def init_data():
    db = SessionLocal()
    try:
        if db.query(Utilisateur).count() == 0:
            users = [
                Utilisateur(nom="Admin", prenom="Système", username="admin",
                            password=hash_password("admin123"), role="admin"),
                Utilisateur(nom="Koné", prenom="Aminata", username="employe",
                            password=hash_password("emp123"), role="employe"),
            ]
            db.add_all(users)

            articles = [
                Article(code="LIV001", titre="Notre Dame de Paris", auteur="Victor Hugo",
                        categorie="Roman", prix_achat=1500, prix_vente=3500, quantite=25),
                Article(code="LIV002", titre="Le Petit Prince", auteur="Antoine de Saint-Exupéry",
                        categorie="Jeunesse", prix_achat=1200, prix_vente=2500, quantite=40),
                Article(code="LIV003", titre="L'Aventure Ambiguë", auteur="Cheikh Hamidou Kane",
                        categorie="Roman Africain", prix_achat=1800, prix_vente=4000, quantite=15),
                Article(code="LIV004", titre="Les Soleils des Indépendances", auteur="Ahmadou Kourouma",
                        categorie="Roman Africain", prix_achat=2000, prix_vente=4500, quantite=20),
                Article(code="SCO001", titre="Mathématiques Terminale", auteur="Collectif",
                        categorie="Scolaire", prix_achat=3000, prix_vente=6000, quantite=30),
                Article(code="SCO002", titre="Français 3ème", auteur="Collectif",
                        categorie="Scolaire", prix_achat=2500, prix_vente=5000, quantite=35),
            ]
            db.add_all(articles)
            db.commit()
    finally:
        db.close()

# ─────────────────────────────────────────
#  APPLICATION FastAPI
# ─────────────────────────────────────────

app = FastAPI(title="LibrairieCI API", version="2.0", description="Backend Gestion Librairie CI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    init_data()

# ── AUTH ──────────────────────────────────

@app.post("/auth/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(Utilisateur).filter(
        Utilisateur.username == data.username,
        Utilisateur.password == hash_password(data.password),
        Utilisateur.actif == True
    ).first()
    if not user:
        raise HTTPException(status_code=401, detail="Identifiant ou mot de passe incorrect")
    token = create_token({"sub": user.username, "role": user.role, "id": user.id})
    return {"token": token, "role": user.role, "nom_complet": f"{user.prenom} {user.nom}", "id": user.id}

@app.get("/auth/me")
def me(payload: dict = Depends(verify_token)):
    return payload

# ── ARTICLES ─────────────────────────────

@app.get("/articles", response_model=List[ArticleOut])
def get_articles(q: Optional[str] = None, db: Session = Depends(get_db),
                 _: dict = Depends(verify_token)):
    query = db.query(Article)
    if q:
        like = f"%{q}%"
        query = query.filter(
            Article.titre.ilike(like) | Article.code.ilike(like) |
            Article.auteur.ilike(like) | Article.categorie.ilike(like)
        )
    return query.order_by(Article.titre).all()

@app.get("/articles/{article_id}", response_model=ArticleOut)
def get_article(article_id: int, db: Session = Depends(get_db), _: dict = Depends(verify_token)):
    art = db.query(Article).filter(Article.id == article_id).first()
    if not art:
        raise HTTPException(404, "Article introuvable")
    return art

@app.post("/articles", response_model=ArticleOut, status_code=201)
def create_article(data: ArticleCreate, db: Session = Depends(get_db),
                   _: dict = Depends(require_admin)):
    if db.query(Article).filter(Article.code == data.code).first():
        raise HTTPException(400, f"Le code '{data.code}' existe déjà")
    art = Article(**data.model_dump())
    db.add(art)
    db.commit()
    db.refresh(art)
    return art

@app.put("/articles/{article_id}", response_model=ArticleOut)
def update_article(article_id: int, data: ArticleCreate, db: Session = Depends(get_db),
                   _: dict = Depends(require_admin)):
    art = db.query(Article).filter(Article.id == article_id).first()
    if not art:
        raise HTTPException(404, "Article introuvable")
    existing = db.query(Article).filter(Article.code == data.code, Article.id != article_id).first()
    if existing:
        raise HTTPException(400, f"Le code '{data.code}' est déjà utilisé")
    for k, v in data.model_dump().items():
        setattr(art, k, v)
    art.modifie_le = datetime.utcnow()
    db.commit()
    db.refresh(art)
    return art

@app.delete("/articles/{article_id}")
def delete_article(article_id: int, db: Session = Depends(get_db),
                   _: dict = Depends(require_admin)):
    art = db.query(Article).filter(Article.id == article_id).first()
    if not art:
        raise HTTPException(404, "Article introuvable")
    db.delete(art)
    db.commit()
    return {"message": "Article supprimé"}

# ── VENTES ───────────────────────────────

@app.post("/ventes", status_code=201)
def create_vente(data: VenteCreate, db: Session = Depends(get_db),
                 payload: dict = Depends(verify_token)):
    # Vérifier le stock
    for ligne in data.lignes:
        art = db.query(Article).filter(Article.id == ligne.id_article).first()
        if not art:
            raise HTTPException(404, f"Article {ligne.id_article} introuvable")
        if art.quantite < ligne.quantite:
            raise HTTPException(400, f"Stock insuffisant pour '{art.titre}' (dispo: {art.quantite})")

    numero = f"VTE-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    vente = Vente(numero=numero, id_employe=payload["id"], total=data.total)
    db.add(vente)
    db.flush()

    for ligne in data.lignes:
        dv = DetailVente(id_vente=vente.id, id_article=ligne.id_article,
                         quantite=ligne.quantite, prix_unitaire=ligne.prix_unitaire)
        db.add(dv)
        art = db.query(Article).filter(Article.id == ligne.id_article).first()
        art.quantite -= ligne.quantite

    db.commit()
    return {"id": vente.id, "numero": numero, "total": data.total}

@app.get("/ventes")
def get_ventes(debut: Optional[str] = None, fin: Optional[str] = None,
               db: Session = Depends(get_db), _: dict = Depends(require_admin)):
    query = db.query(Vente)
    if debut:
        query = query.filter(Vente.date_vente >= datetime.fromisoformat(debut))
    if fin:
        fin_dt = datetime.fromisoformat(fin).replace(hour=23, minute=59, second=59)
        query = query.filter(Vente.date_vente <= fin_dt)
    ventes = query.order_by(Vente.date_vente.desc()).all()
    result = []
    for v in ventes:
        result.append({
            "id": v.id, "numero": v.numero,
            "date_vente": v.date_vente.strftime("%d/%m/%Y %H:%M"),
            "employe": f"{v.employe.prenom} {v.employe.nom}" if v.employe else "",
            "total": v.total
        })
    return result

@app.get("/ventes/{vente_id}/details")
def get_vente_details(vente_id: int, db: Session = Depends(get_db),
                      _: dict = Depends(verify_token)):
    details = db.query(DetailVente).filter(DetailVente.id_vente == vente_id).all()
    return [{
        "titre": d.article.titre if d.article else "",
        "code":  d.article.code  if d.article else "",
        "quantite": d.quantite,
        "prix_unitaire": d.prix_unitaire,
        "sous_total": d.quantite * d.prix_unitaire
    } for d in details]

# ── STATS ─────────────────────────────────

@app.get("/stats/dashboard")
def get_stats(db: Session = Depends(get_db), _: dict = Depends(verify_token)):
    today = datetime.now().date()
    ventes_jour = db.query(func.count(Vente.id), func.coalesce(func.sum(Vente.total), 0))\
                    .filter(func.date(Vente.date_vente) == today).first()
    ventes_mois = db.query(func.count(Vente.id), func.coalesce(func.sum(Vente.total), 0))\
                    .filter(func.extract('month', Vente.date_vente) == today.month,
                            func.extract('year', Vente.date_vente) == today.year).first()
    total_articles = db.query(func.count(Article.id)).scalar()
    stock_faible   = db.query(func.count(Article.id)).filter(Article.quantite <= 5).scalar()
    rupture        = db.query(func.count(Article.id)).filter(Article.quantite == 0).scalar()
    return {
        "ventes_jour": ventes_jour[0], "ca_jour": ventes_jour[1],
        "ventes_mois": ventes_mois[0], "ca_mois": ventes_mois[1],
        "total_articles": total_articles, "stock_faible": stock_faible, "rupture": rupture
    }

@app.get("/stats/top_articles")
def top_articles(db: Session = Depends(get_db), _: dict = Depends(require_admin)):
    from sqlalchemy import desc
    rows = db.query(
        Article.titre,
        func.sum(DetailVente.quantite).label("total_vendu"),
        func.sum(DetailVente.quantite * DetailVente.prix_unitaire).label("recette")
    ).join(DetailVente, Article.id == DetailVente.id_article)\
     .group_by(Article.id)\
     .order_by(desc("total_vendu")).limit(10).all()
    return [{"titre": r.titre, "total_vendu": r.total_vendu, "recette": r.recette} for r in rows]

# ── UTILISATEURS ─────────────────────────

@app.get("/users", response_model=List[UtilisateurOut])
def get_users(db: Session = Depends(get_db), _: dict = Depends(require_admin)):
    return db.query(Utilisateur).order_by(Utilisateur.nom).all()

@app.post("/users", response_model=UtilisateurOut, status_code=201)
def create_user(data: UtilisateurCreate, db: Session = Depends(get_db),
                _: dict = Depends(require_admin)):
    if db.query(Utilisateur).filter(Utilisateur.username == data.username).first():
        raise HTTPException(400, f"L'identifiant '{data.username}' existe déjà")
    u = Utilisateur(nom=data.nom, prenom=data.prenom, username=data.username,
                    password=hash_password(data.password), role=data.role)
    db.add(u)
    db.commit()
    db.refresh(u)
    return u

@app.put("/users/{user_id}", response_model=UtilisateurOut)
def update_user(user_id: int, data: UtilisateurUpdate, db: Session = Depends(get_db),
                _: dict = Depends(require_admin)):
    u = db.query(Utilisateur).filter(Utilisateur.id == user_id).first()
    if not u:
        raise HTTPException(404, "Utilisateur introuvable")
    u.nom = data.nom; u.prenom = data.prenom
    u.role = data.role; u.actif = data.actif
    db.commit(); db.refresh(u)
    return u

@app.put("/users/{user_id}/password")
def reset_password(user_id: int, body: dict, db: Session = Depends(get_db),
                   _: dict = Depends(require_admin)):
    u = db.query(Utilisateur).filter(Utilisateur.id == user_id).first()
    if not u:
        raise HTTPException(404, "Utilisateur introuvable")
    u.password = hash_password(body["password"])
    db.commit()
    return {"message": "Mot de passe réinitialisé"}

@app.get("/health")
def health():
    return {"status": "ok", "version": "2.0", "app": "LibrairieCI"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("server:app", host="0.0.0.0", port=port, reload=False)
