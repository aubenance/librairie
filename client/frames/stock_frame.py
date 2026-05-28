import customtkinter as ctk
from tkinter import ttk, messagebox
from theme import *
from api_client import APIClient


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
        header = ctk.CTkFrame(self, fg_color=BLANC, height=70)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(1, weight=1)

        title = ctk.CTkLabel(
            header,
            text="Gestion du Stock",
            font=("Arial", 24, "bold"),
            text_color=NOIR_TEXTE
        )
        title.grid(row=0, column=0, padx=20, pady=20, sticky="w")

        refresh_btn = ctk.CTkButton(
            header,
            text="Actualiser",
            command=self.load_articles,
            fg_color=VERT
        )
        refresh_btn.grid(row=0, column=2, padx=20)

        # SEARCH
        search_frame = ctk.CTkFrame(self, fg_color=BLANC)
        search_frame.grid(row=1, column=0, sticky="ew", padx=15, pady=10)

        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Rechercher un article...",
            width=300
        )
        self.search_entry.pack(side="left", padx=10, pady=10)

        search_btn = ctk.CTkButton(
            search_frame,
            text="Rechercher",
            command=self.search_articles
        )
        search_btn.pack(side="left", padx=5)

        # TABLE
        table_frame = ctk.CTkFrame(self, fg_color=BLANC)
        table_frame.grid(row=2, column=0, sticky="nsew", padx=15, pady=(0, 15))

        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        columns = (
            "code",
            "titre",
            "categorie",
            "prix",
            "stock"
        )

        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings"
        )

        self.tree.heading("code", text="Code")
        self.tree.heading("titre", text="Titre")
        self.tree.heading("categorie", text="Catégorie")
        self.tree.heading("prix", text="Prix")
        self.tree.heading("stock", text="Stock")

        self.tree.column("code", width=100)
        self.tree.column("titre", width=250)
        self.tree.column("categorie", width=150)
        self.tree.column("prix", width=120)
        self.tree.column("stock", width=100)

        self.tree.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.tree.yview
        )

        scrollbar.grid(row=0, column=1, sticky="ns")

        self.tree.configure(yscrollcommand=scrollbar.set)

    def load_articles(self):

        self.tree.delete(*self.tree.get_children())

        result = APIClient.get_articles()

        if not result["ok"]:
            messagebox.showerror("Erreur", result["error"])
            return

        self._articles = result["data"]

        self.populate_table(self._articles)

    def populate_table(self, data):

        self.tree.delete(*self.tree.get_children())

        for article in data:

            self.tree.insert(
                "",
                "end",
                values=(
                    article.get("code", ""),
                    article.get("titre", ""),
                    article.get("categorie", ""),
                    article.get("prix_vente", 0),
                    article.get("quantite", 0)
                )
            )

    def search_articles(self):

        query = self.search_entry.get().lower()

        filtered = [
            a for a in self._articles
            if query in a.get("titre", "").lower()
            or query in a.get("code", "").lower()
        ]

        self.populate_table(filtered)