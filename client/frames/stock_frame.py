"""
LibrairieCI - Gestion du Stock
"""

import customtkinter as ctk
from tkinter import ttk, messagebox
from theme import *
from api_client import APIClient
import threading


class StockFrame(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(parent, fg_color=GRIS_CLAIR)
        self._articles = []
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.build_ui()
        self.load_articles()

    def build_ui(self):

        # HEADER
        header = ctk.CTkFrame(self, fg_color=BLANC, height=70, corner_radius=0)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_propagate(False)
        header.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            header,
            text="📦  Gestion du Stock",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=NOIR_TEXTE
        ).grid(row=0, column=0, padx=20, pady=18, sticky="w")

        self.lbl_status = ctk.CTkLabel(
            header, text="", font=ctk.CTkFont(size=12), text_color=GRIS_TEXTE
        )
        self.lbl_status.grid(row=0, column=1, padx=10, sticky="e")

        ctk.CTkButton(
            header,
            text="🔄 Actualiser",
            command=self.load_articles,
            fg_color=VERT,
            hover_color=VERT_SOMBRE,
            font=ctk.CTkFont(size=13, weight="bold"),
            width=130,
            height=38,
            corner_radius=6
        ).grid(row=0, column=2, padx=20)

        # SEARCH
        search_frame = ctk.CTkFrame(self, fg_color=BLANC, corner_radius=8)
        search_frame.grid(row=1, column=0, sticky="ew", padx=15, pady=10)

        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="🔍  Rechercher par titre, code, catégorie...",
            width=350,
            height=38,
            font=ctk.CTkFont(size=13)
        )
        self.search_entry.pack(side="left", padx=10, pady=10)
        self.search_entry.bind("<Return>", lambda e: self.search_articles())

        ctk.CTkButton(
            search_frame,
            text="Rechercher",
            command=self.search_articles,
            fg_color=VERT,
            hover_color=VERT_SOMBRE,
            font=ctk.CTkFont(size=13, weight="bold"),
            height=38,
            corner_radius=6
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            search_frame,
            text="Tout afficher",
            command=self.show_all,
            fg_color="#607D8B",
            hover_color="#455A64",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=38,
            corner_radius=6
        ).pack(side="left", padx=5)

        # TABLE
        table_frame = ctk.CTkFrame(self, fg_color=BLANC, corner_radius=8)
        table_frame.grid(row=2, column=0, sticky="nsew", padx=15, pady=(0, 15))
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Stock.Treeview",
                         background=BLANC, foreground=NOIR_TEXTE,
                         fieldbackground=BLANC, rowheight=32,
                         font=("Segoe UI", 11))
        style.configure("Stock.Treeview.Heading",
                         background=VERT, foreground=BLANC,
                         font=("Segoe UI", 11, "bold"),
                         relief="flat")
        style.map("Stock.Treeview",
                  background=[("selected", VERT_CLAIR)],
                  foreground=[("selected", VERT_SOMBRE)])

        columns = ("code", "titre", "auteur", "categorie", "prix_achat", "prix_vente", "stock", "statut")

        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            style="Stock.Treeview",
            selectmode="browse"
        )

        entetes = {
            "code": ("Code", 100),
            "titre": ("Titre / Nom", 240),
            "auteur": ("Auteur", 150),
            "categorie": ("Catégorie", 130),
            "prix_achat": ("P. Achat (FCFA)", 130),
            "prix_vente": ("P. Vente (FCFA)", 130),
            "stock": ("Stock", 80),
            "statut": ("Statut", 100),
        }

        for col, (label, width) in entetes.items():
            self.tree.heading(col, text=label)
            self.tree.column(col, width=width, minwidth=60)

        self.tree.column("stock", anchor="center")
        self.tree.column("prix_achat", anchor="e")
        self.tree.column("prix_vente", anchor="e")

        self.tree.tag_configure("rupture", background="#FFEBEE", foreground=ROUGE)
        self.tree.tag_configure("alerte",  background="#FFF8E1", foreground=ORANGE)
        self.tree.tag_configure("normal",  background=BLANC,     foreground=NOIR_TEXTE)

        self.tree.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)

        h_scroll = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        h_scroll.grid(row=1, column=0, sticky="ew")
        self.tree.configure(xscrollcommand=h_scroll.set)

    def load_articles(self):
        """Chargement asynchrone pour ne pas bloquer l'UI"""
        self.lbl_status.configure(text="⏳ Chargement...")

        def fetch():
            result = APIClient.get_articles()
            if result["ok"]:
                self._articles = result["data"]
                self.after(0, lambda: self.populate_table(self._articles))
                self.after(0, lambda: self.lbl_status.configure(
                    text=f"✅ {len(self._articles)} article(s)"))
            else:
                self.after(0, lambda: self.lbl_status.configure(text="❌ Erreur de connexion"))

        threading.Thread(target=fetch, daemon=True).start()

    def populate_table(self, data):
        self.tree.delete(*self.tree.get_children())

        for article in data:
            qte = article.get("quantite", 0)
            tag = "rupture" if qte == 0 else ("alerte" if qte <= 5 else "normal")
            statut = "⛔ Rupture" if qte == 0 else ("⚠️ Alerte" if qte <= 5 else "✅ OK")

            prix_a = f"{int(article.get('prix_achat', 0)):,}".replace(",", " ")
            prix_v = f"{int(article.get('prix_vente', 0)):,}".replace(",", " ")

            self.tree.insert(
                "", "end",
                values=(
                    article.get("code", ""),
                    article.get("titre", ""),
                    article.get("auteur", ""),
                    article.get("categorie", ""),
                    prix_a,
                    prix_v,
                    qte,
                    statut
                ),
                tags=(tag,)
            )

    def search_articles(self):
        query = self.search_entry.get().lower().strip()
        if not query:
            self.populate_table(self._articles)
            return
        filtered = [
            a for a in self._articles
            if query in a.get("titre", "").lower()
            or query in a.get("code", "").lower()
            or query in a.get("categorie", "").lower()
            or query in a.get("auteur", "").lower()
        ]
        self.populate_table(filtered)
        self.lbl_status.configure(text=f"🔍 {len(filtered)} résultat(s)")

    def show_all(self):
        self.search_entry.delete(0, "end")
        self.populate_table(self._articles)
        self.lbl_status.configure(text=f"✅ {len(self._articles)} article(s)")
