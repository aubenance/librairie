# -*- coding: utf-8 -*-
"""
LibrairieCI Pro - Point d'entree principal
"""

# ══════════════════════════════════════════════════════════
#  ETAPE 1 : NETTOYAGE CACHE + ENCODAGE (AVANT TOUT IMPORT)
# ══════════════════════════════════════════════════════════
import os, sys, shutil

# Supprimer TOUS les __pycache__ pour forcer la recompilation
_base = os.path.dirname(os.path.abspath(__file__))
for _root, _dirs, _files in os.walk(_base):
    for _d in list(_dirs):
        if _d == "__pycache__":
            shutil.rmtree(os.path.join(_root, _d), ignore_errors=True)
            _dirs.remove(_d)
    for _f in _files:
        if _f.endswith(".pyc"):
            try: os.remove(os.path.join(_root, _f))
            except: pass

# Forcer l'encodage UTF-8 partout sur Windows
os.environ["PYTHONUTF8"]       = "1"
os.environ["PYTHONIOENCODING"] = "utf-8"
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# ══════════════════════════════════════════════════════════
#  ETAPE 2 : IMPORTS (apres nettoyage cache)
# ══════════════════════════════════════════════════════════
sys.path.insert(0, _base)
sys.path.insert(0, os.path.join(_base, "frames"))

import customtkinter as ctk
from tkinter import messagebox

from theme import setup_theme, VERT, VERT_SOMBRE, BLANC, GRIS_CLAIR, ROUGE
from api_client import session
from frames.login_frame     import LoginFrame
from frames.dashboard_frame import DashboardFrame
from frames.articles_frame  import ArticlesFrame
from frames.vente_frame     import VenteFrame
from frames.stock_frame     import StockFrame
from frames.users_frame     import UsersFrame
from frames.rapports_frame  import RapportsFrame


# ══════════════════════════════════════════════════════════
#  APPLICATION PRINCIPALE
# ══════════════════════════════════════════════════════════
class LibrairieApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        # Fix encodage Tcl/Tk (emojis sur Windows)
        try:
            self.tk.call("encoding", "system", "utf-8")
        except Exception:
            pass

        setup_theme()
        self.title("LibrairieCI - Gestion de Librairie")
        self.geometry("1280x780")
        self.minsize(1024, 680)
        self.configure(fg_color=GRIS_CLAIR)
        try:
            self.iconbitmap(os.path.join(_base, "icon.ico"))
        except Exception:
            pass

        self._current_frame = None
        self._sidebar       = None
        self._content       = None
        self._sidebar_btns  = {}

        self._show_login()

    # ── LOGIN ─────────────────────────────────────────────
    def _show_login(self):
        for w in self.winfo_children():
            w.destroy()
        self.geometry("1100x680")
        LoginFrame(self, on_success=self._after_login).pack(fill="both", expand=True)

    def _after_login(self):
        self.geometry("1280x780")
        self._build_main()
        self._navigate("dashboard")

    # ── LAYOUT PRINCIPAL ──────────────────────────────────
    def _build_main(self):
        for w in self.winfo_children():
            w.destroy()
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self._sidebar = ctk.CTkFrame(self, fg_color=VERT, width=240, corner_radius=0)
        self._sidebar.grid(row=0, column=0, sticky="nsew")
        self._sidebar.grid_propagate(False)

        top = ctk.CTkFrame(self._sidebar, fg_color=VERT_SOMBRE, height=100, corner_radius=0)
        top.pack(fill="x"); top.pack_propagate(False)
        ctk.CTkLabel(top, text="LibrairieCI",
                     font=ctk.CTkFont(size=24, weight="bold"),
                     text_color=BLANC).pack(pady=(20, 4))
        ctk.CTkLabel(top, text="Gestion Professionnelle",
                     font=ctk.CTkFont(size=11),
                     text_color="#C8E6C9").pack()

        user_card = ctk.CTkFrame(self._sidebar, fg_color="#005F2B", height=70, corner_radius=0)
        user_card.pack(fill="x"); user_card.pack_propagate(False)
        ctk.CTkLabel(user_card, text=session.nom_complet,
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=BLANC).pack(pady=(12, 0))
        ctk.CTkLabel(user_card,
                     text="Administrateur" if session.is_admin else "Employe",
                     font=ctk.CTkFont(size=11),
                     text_color="#C8E6C9").pack()

        menus = [
            ("dashboard", "Tableau de bord",  True),
            ("vente",     "Nouvelle Vente",    True),
            ("stock",     "Stock",             True),
            ("articles",  "Articles",          session.is_admin),
            ("rapports",  "Rapports & Stats",  session.is_admin),
            ("users",     "Utilisateurs",      session.is_admin),
        ]
        for section, label, visible in menus:
            if not visible:
                continue
            btn = ctk.CTkButton(
                self._sidebar, text=label,
                command=lambda s=section: self._navigate(s),
                anchor="w", fg_color="transparent",
                hover_color="#00A04A", text_color=BLANC,
                corner_radius=0, height=46,
                font=ctk.CTkFont(size=13))
            btn.pack(fill="x")
            self._sidebar_btns[section] = btn

        ctk.CTkButton(
            self._sidebar, text="Deconnexion",
            command=self._deconnecter,
            fg_color="#B71C1C", hover_color="#7F0000",
            text_color=BLANC, corner_radius=0, height=46
        ).pack(fill="x", side="bottom")

        self._content = ctk.CTkFrame(self, fg_color=GRIS_CLAIR, corner_radius=0)
        self._content.grid(row=0, column=1, sticky="nsew")

    # ── NAVIGATION ────────────────────────────────────────
    def _navigate(self, section: str):
        for s, btn in self._sidebar_btns.items():
            btn.configure(fg_color="#00A04A" if s == section else "transparent")

        # Vider le contenu precedent
        if self._current_frame:
            self._current_frame.destroy()
            self._current_frame = None
        for w in self._content.winfo_children():
            w.destroy()

        frame_map = {
            "dashboard": lambda: DashboardFrame(self._content, self._navigate),
            "vente":     lambda: VenteFrame(self._content),
            "stock":     lambda: StockFrame(self._content),
            "articles":  lambda: ArticlesFrame(self._content) if session.is_admin else None,
            "rapports":  lambda: RapportsFrame(self._content) if session.is_admin else None,
            "users":     lambda: UsersFrame(self._content)    if session.is_admin else None,
        }

        builder = frame_map.get(section)
        if not builder:
            return

        try:
            frame = builder()
            if frame:
                frame.pack(fill="both", expand=True)
                self._current_frame = frame
        except Exception as e:
            safe_err = str(e).encode("ascii", errors="replace").decode("ascii")
            ctk.CTkLabel(
                self._content,
                text=f"Erreur de chargement :\n{type(e).__name__}: {safe_err[:300]}",
                text_color=ROUGE,
                font=ctk.CTkFont(size=13),
                wraplength=700, justify="center"
            ).pack(pady=60, padx=40)

    # ── DECONNEXION ───────────────────────────────────────
    def _deconnecter(self):
        if messagebox.askyesno("Deconnexion", "Voulez-vous vous deconnecter ?"):
            session.token = ""; session.role = ""
            session.nom_complet = ""; session.user_id = 0
            self._current_frame = None
            self._sidebar_btns  = {}
            self._show_login()


# ══════════════════════════════════════════════════════════
#  LANCEMENT
# ══════════════════════════════════════════════════════════
if __name__ == "__main__":
    app = LibrairieApp()
    app.mainloop()
