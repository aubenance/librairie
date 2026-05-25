"""
LibrairieCI - Tableau de bord
"""

import customtkinter as ctk
from theme import *
from api_client import APIClient, session
import threading
from datetime import datetime


class DashboardFrame(ctk.CTkFrame):

    def __init__(self, parent, navigate):
        super().__init__(parent, fg_color=GRIS_CLAIR)
        self.navigate = navigate
        self._build()
        self._load_stats()
        self._auto_refresh()

    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # ── En-tête ──
        header = ctk.CTkFrame(self, fg_color=BLANC, corner_radius=0, height=70)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_propagate(False)
        header.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(header, text=f"  Bonjour, {session.nom_complet} !",
                     font=ctk.CTkFont(size=20, weight="bold"),
                     text_color=NOIR_TEXTE).grid(row=0, column=0, padx=20, pady=15, sticky="w")

        role_txt = "Administrateur" if session.is_admin else "Employe"
        role_clr = VERT if session.is_admin else ORANGE
        ctk.CTkLabel(header, text=role_txt, font=ctk.CTkFont(size=13),
                     text_color=role_clr).grid(row=0, column=1, sticky="e", padx=20)

        self.lbl_heure = ctk.CTkLabel(header, text="", font=ctk.CTkFont(size=12),
                                       text_color=GRIS_TEXTE)
        self.lbl_heure.grid(row=0, column=2, padx=20)
        self._update_clock()

        ctk.CTkFrame(self, fg_color=GRIS, height=1).grid(row=1, column=0, sticky="ew")

        # ── Zone scrollable ──
        scroll = ctk.CTkScrollableFrame(self, fg_color=GRIS_CLAIR)
        scroll.grid(row=2, column=0, sticky="nsew")
        scroll.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(scroll, text="Vue d'ensemble du jour",
                     font=ctk.CTkFont(size=16, weight="bold"),
                     text_color=NOIR_TEXTE).grid(row=0, column=0, sticky="w", padx=24, pady=(20,10))

        cards_f = ctk.CTkFrame(scroll, fg_color=GRIS_CLAIR)
        cards_f.grid(row=1, column=0, sticky="ew", padx=20, pady=(0,20))

        self.card_vj  = self._stat_card(cards_f, "Ventes Aujourd'hui", "--", VERT,   0)
        self.card_caj = self._stat_card(cards_f, "CA Aujourd'hui",     "--", ORANGE, 1)
        self.card_vm  = self._stat_card(cards_f, "Ventes ce Mois",     "--", BLEU,   2)
        self.card_cam = self._stat_card(cards_f, "CA ce Mois",         "--", "#7B1FA2", 3)

        if session.is_admin:
            ctk.CTkLabel(scroll, text="Etat du Stock",
                         font=ctk.CTkFont(size=16, weight="bold"),
                         text_color=NOIR_TEXTE).grid(row=2, column=0, sticky="w", padx=24, pady=(10,10))
            sf = ctk.CTkFrame(scroll, fg_color=GRIS_CLAIR)
            sf.grid(row=3, column=0, sticky="ew", padx=20, pady=(0,20))
            self.card_art = self._stat_card(sf, "Total Articles",  "--", VERT,   0)
            self.card_fbl = self._stat_card(sf, "Stock Faible",    "--", ORANGE, 1)
            self.card_rup = self._stat_card(sf, "Rupture de Stock","--", ROUGE,  2)
        else:
            self.card_art = self.card_fbl = self.card_rup = None

        ctk.CTkLabel(scroll, text="Acces rapide",
                     font=ctk.CTkFont(size=16, weight="bold"),
                     text_color=NOIR_TEXTE).grid(row=4, column=0, sticky="w", padx=24, pady=(10,10))

        rf = ctk.CTkFrame(scroll, fg_color=GRIS_CLAIR)
        rf.grid(row=5, column=0, sticky="ew", padx=20, pady=(0,30))

        shortcuts = [("Nouvelle Vente","vente",VERT),("Stock","stock",BLEU)]
        if session.is_admin:
            shortcuts += [("Articles","articles","#7B1FA2"),
                          ("Rapports","rapports",ORANGE),
                          ("Utilisateurs","users","#00838F")]
        for i,(title,nav,color) in enumerate(shortcuts):
            self._shortcut(rf, title, nav, color, i)

    def _stat_card(self, parent, title, value, color, col):
        card = ctk.CTkFrame(parent, fg_color=BLANC, corner_radius=12,
                            border_width=2, border_color=color)
        card.grid(row=0, column=col, padx=8, pady=4, sticky="nsew", ipadx=10, ipady=10)
        parent.grid_columnconfigure(col, weight=1)
        ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=11),
                     text_color=GRIS_TEXTE).pack(pady=(14,2))
        lbl = ctk.CTkLabel(card, text=value,
                           font=ctk.CTkFont(size=20, weight="bold"), text_color=color)
        lbl.pack(pady=(4,14))
        return lbl

    def _shortcut(self, parent, title, nav, color, col):
        card = ctk.CTkFrame(parent, fg_color=BLANC, corner_radius=12, cursor="hand2")
        card.grid(row=0, column=col, padx=8, pady=4, sticky="nsew", ipadx=16, ipady=16)
        parent.grid_columnconfigure(col, weight=1)
        ctk.CTkFrame(card, fg_color=color, height=5, corner_radius=0).pack(fill="x")
        btn = make_button(card, title, lambda n=nav: self.navigate(n),
                          color=color, hover_color=color, width=140, height=44)
        btn.pack(pady=18)
        card.bind("<Button-1>", lambda e, n=nav: self.navigate(n))

    def _load_stats(self):
        def fetch():
            r = APIClient.get_stats()
            if r["ok"]:
                self.after(0, lambda: self._update_cards(r["data"]))
        threading.Thread(target=fetch, daemon=True).start()

    def _update_cards(self, d):
        try:
            self.card_vj.configure(text=str(d.get("ventes_jour",0)))
            self.card_caj.configure(text=format_fcfa(d.get("ca_jour",0)))
            self.card_vm.configure(text=str(d.get("ventes_mois",0)))
            self.card_cam.configure(text=format_fcfa(d.get("ca_mois",0)))
            if self.card_art:
                self.card_art.configure(text=str(d.get("total_articles",0)))
                self.card_fbl.configure(text=str(d.get("stock_faible",0)))
                rup = d.get("rupture",0)
                self.card_rup.configure(text=str(rup), text_color=ROUGE if rup>0 else VERT)
        except Exception:
            pass

    def _auto_refresh(self):
        self._load_stats()
        self.after(30000, self._auto_refresh)

    def _update_clock(self):
        self.lbl_heure.configure(text=datetime.now().strftime("%d/%m/%Y  %H:%M:%S"))
        self.after(1000, self._update_clock)
