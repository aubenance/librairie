"""
LibrairieCI - Rapports & Statistiques
"""

import customtkinter as ctk
from tkinter import ttk
from theme import *
from api_client import APIClient
import threading
from datetime import datetime


class RapportsFrame(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(parent, fg_color=GRIS_CLAIR)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.build_ui()
        self.load_stats()

    def build_ui(self):

        # ── HEADER ──
        header = ctk.CTkFrame(self, fg_color=BLANC, height=70, corner_radius=0)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_propagate(False)
        header.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            header,
            text="📊  Rapports & Statistiques",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=NOIR_TEXTE
        ).grid(row=0, column=0, padx=20, pady=18, sticky="w")

        self.lbl_date = ctk.CTkLabel(
            header,
            text=f"📅  {datetime.now().strftime('%d/%m/%Y  •  %H:%M')}",
            font=ctk.CTkFont(size=12),
            text_color=GRIS_TEXTE
        )
        self.lbl_date.grid(row=0, column=1, padx=10, sticky="e")

        ctk.CTkButton(
            header,
            text="🔄 Actualiser",
            command=self.load_stats,
            fg_color=VERT, hover_color=VERT_SOMBRE,
            font=ctk.CTkFont(size=13, weight="bold"),
            width=130, height=38, corner_radius=6
        ).grid(row=0, column=2, padx=20)

        # ── CONTENU SCROLLABLE ──
        scroll = ctk.CTkScrollableFrame(self, fg_color=GRIS_CLAIR)
        scroll.grid(row=1, column=0, sticky="nsew", padx=15, pady=15)
        scroll.grid_columnconfigure(0, weight=1)
        self._scroll = scroll

        # ── CARTES STATS ──
        cards_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        cards_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        for i in range(4):
            cards_frame.grid_columnconfigure(i, weight=1)

        self._cards = {}
        card_defs = [
            ("ventes_jour",   "🛒", "Ventes aujourd'hui", "0",     VERT),
            ("ca_jour",       "💰", "CA aujourd'hui",     "0 FCFA", BLEU),
            ("total_articles","📚", "Total articles",     "0",     ORANGE),
            ("ruptures",      "⛔", "Ruptures de stock",  "0",     ROUGE),
        ]
        for col, (key, icon, titre, val_def, couleur) in enumerate(card_defs):
            card = ctk.CTkFrame(cards_frame, fg_color=BLANC, corner_radius=12,
                                border_width=2, border_color=couleur, height=100)
            card.grid(row=0, column=col, sticky="nsew", padx=8)
            card.grid_propagate(False)
            card.grid_columnconfigure(0, weight=1)

            top = ctk.CTkFrame(card, fg_color="transparent")
            top.grid(row=0, column=0, sticky="ew", padx=14, pady=(14, 0))
            ctk.CTkLabel(top, text=icon, font=ctk.CTkFont(size=22),
                         text_color=couleur).pack(side="left")
            ctk.CTkLabel(top, text=titre, font=ctk.CTkFont(size=11),
                         text_color=GRIS_TEXTE).pack(side="left", padx=6)

            lbl_val = ctk.CTkLabel(card, text=val_def,
                                    font=ctk.CTkFont(size=20, weight="bold"),
                                    text_color=couleur)
            lbl_val.grid(row=1, column=0, pady=(4, 14))
            self._cards[key] = lbl_val

        # ── TOP ARTICLES ──
        top_frame = ctk.CTkFrame(scroll, fg_color=BLANC, corner_radius=10)
        top_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 20))
        top_frame.grid_columnconfigure(0, weight=1)
        top_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(top_frame, text="🏆  Articles les plus vendus",
                     font=ctk.CTkFont(size=15, weight="bold"),
                     text_color=VERT).grid(row=0, column=0, padx=20, pady=(16, 8), sticky="w")

        tree_frame = ctk.CTkFrame(top_frame, fg_color=BLANC)
        tree_frame.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))
        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.grid_rowconfigure(0, weight=1)

        style = ttk.Style()
        style.configure("Top.Treeview",
                         background=BLANC, foreground=NOIR_TEXTE,
                         fieldbackground=BLANC, rowheight=30,
                         font=("Segoe UI", 11))
        style.configure("Top.Treeview.Heading",
                         background=VERT, foreground=BLANC,
                         font=("Segoe UI", 11, "bold"), relief="flat")
        style.map("Top.Treeview",
                  background=[("selected", VERT_CLAIR)],
                  foreground=[("selected", VERT_SOMBRE)])

        self.top_tree = ttk.Treeview(
            tree_frame,
            columns=("rang", "titre", "auteur", "categorie", "vendu", "ca"),
            show="headings",
            style="Top.Treeview",
            height=8
        )
        entetes_top = {
            "rang": ("🏅", 50),
            "titre": ("Titre", 260),
            "auteur": ("Auteur", 160),
            "categorie": ("Catégorie", 130),
            "vendu": ("Qté vendue", 100),
            "ca": ("CA généré (FCFA)", 140),
        }
        for col, (label, w) in entetes_top.items():
            self.top_tree.heading(col, text=label)
            self.top_tree.column(col, width=w, minwidth=40)
        self.top_tree.column("rang", anchor="center")
        self.top_tree.column("vendu", anchor="center")
        self.top_tree.column("ca", anchor="e")
        self.top_tree.tag_configure("or",     background="#FFF9C4")
        self.top_tree.tag_configure("argent", background="#F5F5F5")
        self.top_tree.tag_configure("bronze", background="#FBE9E7")

        self.top_tree.grid(row=0, column=0, sticky="nsew")
        scr = ttk.Scrollbar(tree_frame, orient="vertical", command=self.top_tree.yview)
        scr.grid(row=0, column=1, sticky="ns")
        self.top_tree.configure(yscrollcommand=scr.set)

        # ── MESSAGE STATUS ──
        self.lbl_status = ctk.CTkLabel(scroll, text="",
                                        font=ctk.CTkFont(size=13, slant="italic"),
                                        text_color=GRIS_TEXTE)
        self.lbl_status.grid(row=2, column=0, pady=10)

    def load_stats(self):
        self.lbl_status.configure(text="⏳ Chargement des statistiques...")

        def fetch():
            result_stats = APIClient.get_stats()
            result_top   = APIClient.get_top_articles()
            self.after(0, lambda: self._update_ui(result_stats, result_top))

        threading.Thread(target=fetch, daemon=True).start()

    def _update_ui(self, result_stats, result_top):
        # Stats dashboard
        if result_stats["ok"]:
            d = result_stats["data"]
            self._cards["ventes_jour"].configure(
                text=str(d.get("ventes_aujourd_hui", d.get("ventes_jour", "—"))))
            ca = d.get("ca_aujourd_hui", d.get("ca_jour", 0))
            self._cards["ca_jour"].configure(text=format_fcfa(ca))
            self._cards["total_articles"].configure(
                text=str(d.get("total_articles", "—")))
            self._cards["ruptures"].configure(
                text=str(d.get("ruptures_stock", d.get("ruptures", "—"))))
            self.lbl_status.configure(text="✅ Statistiques mises à jour")
        else:
            self.lbl_status.configure(text="⚠️ Impossible de charger les statistiques — vérifiez la connexion serveur")

        # Top articles
        self.top_tree.delete(*self.top_tree.get_children())
        if result_top["ok"]:
            medailles = {1: "or", 2: "argent", 3: "bronze"}
            rangs      = {1: "🥇", 2: "🥈", 3: "🥉"}
            for i, art in enumerate(result_top["data"], 1):
                tag  = medailles.get(i, "")
                rang = rangs.get(i, str(i))
                ca   = f"{int(art.get('ca', art.get('chiffre_affaires', 0))):,}".replace(",", " ")
                self.top_tree.insert("", "end", tags=(tag,),
                                     values=(rang,
                                             art.get("titre", ""),
                                             art.get("auteur", ""),
                                             art.get("categorie", ""),
                                             art.get("quantite_vendue", art.get("vendu", 0)),
                                             ca))
