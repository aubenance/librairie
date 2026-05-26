"""
LibrairieCI Pro - Application principale
Point d'entrée desktop
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "frames"))

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from theme import setup_theme, VERT, VERT_SOMBRE, VERT_CLAIR, BLANC, GRIS_CLAIR, GRIS, GRIS_TEXTE, NOIR_TEXTE, ROUGE, ORANGE, BLEU
from api_client import session
from frames.login_frame     import LoginFrame
from frames.dashboard_frame import DashboardFrame
from frames.articles_frame  import ArticlesFrame
from frames.vente_frame     import VenteFrame
from frames.stock_frame     import StockFrame
from frames.users_frame     import UsersFrame
from frames.rapports_frame  import RapportsFrame


class LibrairieApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        # ── Fix encodage Unicode/Emoji sur Windows ──
        try:
            self.tk.call("encoding", "system", "utf-8")
        except Exception:
            pass

        setup_theme()
        self.title("LibrairieCI  –  Gestion de Librairie")
        self.geometry("1280x780")
        self.minsize(1024, 680)
        self.configure(fg_color=GRIS_CLAIR)

        # Icône (si disponible)
        try:
            self.iconbitmap(os.path.join(os.path.dirname(__file__), "icon.ico"))
        except Exception:
            pass

        self._current_frame = None
        self._sidebar       = None
        self._content       = None
        self._sidebar_btns  = {}

        self._show_login()

    # ═══════════════════════════════════════════════
    #  ÉCRAN DE CONNEXION
    # ═══════════════════════════════════════════════

    def _show_login(self):
        for w in self.winfo_children():
            w.destroy()
        self.geometry("1100x680")
        self.resizable(True, True)

        frame = LoginFrame(self, on_success=self._after_login)
        frame.pack(fill="both", expand=True)

    def _after_login(self):
        self.geometry("1280x780")
        self._build_main()
        self._navigate("dashboard")

    # ═══════════════════════════════════════════════
    #  LAYOUT PRINCIPAL
    # ═══════════════════════════════════════════════

    def _build_main(self):
        for w in self.winfo_children():
            w.destroy()

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ── SIDEBAR ──────────────────────────
        self._sidebar = ctk.CTkFrame(self, fg_color=VERT, width=230, corner_radius=0)
        self._sidebar.grid(row=0, column=0, sticky="nsew")
        self._sidebar.grid_propagate(False)
        self._sidebar.grid_rowconfigure(10, weight=1)

        # Logo / Titre
        logo_frame = ctk.CTkFrame(self._sidebar, fg_color=VERT_SOMBRE, height=90, corner_radius=0)
        logo_frame.pack(fill="x")
        logo_frame.pack_propagate(False)

        ctk.CTkLabel(logo_frame, text="📚  LibrairieCI",
                     font=ctk.CTkFont(size=19, weight="bold"),
                     text_color=BLANC).pack(pady=(18, 2))
        ctk.CTkLabel(logo_frame, text="Gestion Professionnelle",
                     font=ctk.CTkFont(size=10), text_color="#A5D6A7").pack()

        # Infos utilisateur
        user_card = ctk.CTkFrame(self._sidebar, fg_color="#005F2B", height=68, corner_radius=0)
        user_card.pack(fill="x")
        user_card.pack_propagate(False)

        ctk.CTkLabel(user_card,
                     text=f"👤  {session.nom_complet}",
                     font=ctk.CTkFont(size=12, weight="bold"), text_color=BLANC
                     ).pack(pady=(10,0))
        ctk.CTkLabel(user_card,
                     text=f"{'🔑 Administrateur' if session.is_admin else '👷 Employé'}",
                     font=ctk.CTkFont(size=10), text_color="#C8E6C9"
                     ).pack()

        # Séparateur
        ctk.CTkFrame(self._sidebar, fg_color="#81C784", height=1).pack(fill="x", pady=8)

        # ── Boutons navigation ──
        menus = [
            ("dashboard", "🏠",  "Tableau de bord",      True),
            ("vente",     "🛒",  "Nouvelle Vente",        True),
            ("stock",     "📦",  "Stock",                 True),
            ("articles",  "📖",  "Articles",              session.is_admin),
            ("rapports",  "📊",  "Rapports & Stats",      session.is_admin),
            ("users",     "👥",  "Utilisateurs",          session.is_admin),
        ]

        for section, icon, label, visible in menus:
            if not visible:
                continue
            btn = ctk.CTkButton(
                self._sidebar,
                text=f"  {icon}  {label}",
                command=lambda s=section: self._navigate(s),
                anchor="w",
                fg_color="transparent",
                hover_color="#00A04A",
                text_color=BLANC,
                font=ctk.CTkFont(size=13),
                height=44,
                corner_radius=0,
            )
            btn.pack(fill="x")
            self._sidebar_btns[section] = btn

        # Séparateur bas
        ctk.CTkFrame(self._sidebar, fg_color="#81C784", height=1).pack(fill="x", side="bottom", pady=0)

        # Bouton déconnexion
        ctk.CTkButton(
            self._sidebar,
            text="  ⬅  Déconnexion",
            command=self._deconnecter,
            anchor="w",
            fg_color="#B71C1C",
            hover_color="#7F0000",
            text_color=BLANC,
            font=ctk.CTkFont(size=13),
            height=46,
            corner_radius=0,
        ).pack(fill="x", side="bottom")

        # Version
        ctk.CTkLabel(self._sidebar, text="v2.0 – LibrairieCI",
                     font=ctk.CTkFont(size=9), text_color="#81C784"
                     ).pack(side="bottom", pady=4)

        # ── ZONE CONTENU ──────────────────────
        self._content = ctk.CTkFrame(self, fg_color=GRIS_CLAIR, corner_radius=0)
        self._content.grid(row=0, column=1, sticky="nsew")

    # ═══════════════════════════════════════════════
    #  NAVIGATION
    # ═══════════════════════════════════════════════

    def _navigate(self, section: str):
        # Surbrillance bouton actif
        for s, btn in self._sidebar_btns.items():
            btn.configure(fg_color="#00A04A" if s == section else "transparent",
                          font=ctk.CTkFont(size=13, weight="bold" if s == section else "normal"))

        # Détruire TOUT le contenu précédent
        if self._current_frame:
            self._current_frame.destroy()
            self._current_frame = None
        for w in self._content.winfo_children():
            w.destroy()

        # Charger nouveau frame
        frame_map = {
            "dashboard": lambda: DashboardFrame(self._content, self._navigate),
            "vente":     lambda: VenteFrame(self._content),
            "stock":     lambda: StockFrame(self._content),
            "articles":  lambda: ArticlesFrame(self._content) if session.is_admin else None,
            "rapports":  lambda: RapportsFrame(self._content) if session.is_admin else None,
            "users":     lambda: UsersFrame(self._content)    if session.is_admin else None,
        }

        builder = frame_map.get(section)
        if builder:
            try:
                frame = builder()
                if frame:
                    frame.pack(fill="both", expand=True)
                    self._current_frame = frame
            except Exception as e:
                lbl = ctk.CTkLabel(
                    self._content,
                    text=f"❌ Erreur lors du chargement de la page :\n"
                         f"{type(e).__name__}: {e}\n\n"
                         f"Vérifiez la console pour plus de détails.",
                    text_color=ROUGE,
                    font=ctk.CTkFont(size=13),
                    wraplength=700,
                    justify="center")
                lbl.pack(pady=80, padx=40)

    def _deconnecter(self):
        if messagebox.askyesno("Déconnexion", "Voulez-vous vraiment vous déconnecter ?"):
            session.token      = ""
            session.role       = ""
            session.nom_complet = ""
            session.user_id    = 0
            self._current_frame = None
            self._sidebar_btns  = {}
            self._show_login()


# ═══════════════════════════════════════════════
#  POINT D'ENTRÉE
# ═══════════════════════════════════════════════

if __name__ == "__main__":
    app = LibrairieApp()
    app.mainloop()
