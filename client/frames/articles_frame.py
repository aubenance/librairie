import customtkinter as ctk
from tkinter import ttk, messagebox
from theme import *
from api_client import APIClient


class ArticlesFrame(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(parent, fg_color=GRIS_CLAIR)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.build_ui()
        self.load_articles()

    def build_ui(self):

        # HEADER
        header = ctk.CTkFrame(self, fg_color=BLANC, height=70)
        header.grid(row=0, column=0, sticky="ew")

        title = ctk.CTkLabel(
            header,
            text="Gestion des Articles",
            font=("Arial", 24, "bold")
        )

        title.pack(side="left", padx=20, pady=20)

        # CONTENT
        content = ctk.CTkFrame(self, fg_color=GRIS_CLAIR)
        content.grid(row=1, column=0, sticky="nsew", padx=15, pady=15)

        content.grid_columnconfigure(0, weight=3)
        content.grid_columnconfigure(1, weight=1)
        content.grid_rowconfigure(0, weight=1)

        # TABLE
        table_frame = ctk.CTkFrame(content, fg_color=BLANC)
        table_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        columns = (
            "code",
            "titre",
            "auteur",
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
        self.tree.heading("auteur", text="Auteur")
        self.tree.heading("categorie", text="Catégorie")
        self.tree.heading("prix", text="Prix")
        self.tree.heading("stock", text="Stock")

        self.tree.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.tree.yview
        )

        scrollbar.grid(row=0, column=1, sticky="ns")

        self.tree.configure(yscrollcommand=scrollbar.set)

        # FORM
        form_frame = ctk.CTkFrame(content, fg_color=BLANC)
        form_frame.grid(row=0, column=1, sticky="nsew")

        title_form = ctk.CTkLabel(
            form_frame,
            text="Nouvel Article",
            font=("Arial", 20, "bold"),
            text_color=VERT
        )

        title_form.pack(pady=20)

        self.code_entry = ctk.CTkEntry(form_frame, placeholder_text="Code article")
        self.code_entry.pack(fill="x", padx=20, pady=5)

        self.title_entry = ctk.CTkEntry(form_frame, placeholder_text="Titre")
        self.title_entry.pack(fill="x", padx=20, pady=5)

        self.author_entry = ctk.CTkEntry(form_frame, placeholder_text="Auteur")
        self.author_entry.pack(fill="x", padx=20, pady=5)

        self.category_entry = ctk.CTkEntry(form_frame, placeholder_text="Catégorie")
        self.category_entry.pack(fill="x", padx=20, pady=5)

        self.buy_price_entry = ctk.CTkEntry(form_frame, placeholder_text="Prix achat")
        self.buy_price_entry.pack(fill="x", padx=20, pady=5)

        self.sell_price_entry = ctk.CTkEntry(form_frame, placeholder_text="Prix vente")
        self.sell_price_entry.pack(fill="x", padx=20, pady=5)

        self.stock_entry = ctk.CTkEntry(form_frame, placeholder_text="Quantité")
        self.stock_entry.pack(fill="x", padx=20, pady=5)

        # BUTTONS
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=20)

        save_btn = ctk.CTkButton(
            btn_frame,
            text="Enregistrer",
            fg_color=VERT,
            command=self.save_article
        )

        save_btn.pack(side="left", expand=True, padx=5)

        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="Annuler",
            fg_color=ROUGE,
            command=self.clear_fields
        )

        cancel_btn.pack(side="left", expand=True, padx=5)

    def load_articles(self):

        result = APIClient.get_articles()

        if not result["ok"]:
            return

        self.tree.delete(*self.tree.get_children())

        for article in result["data"]:

            self.tree.insert(
                "",
                "end",
                values=(
                    article.get("code", ""),
                    article.get("titre", ""),
                    article.get("auteur", ""),
                    article.get("categorie", ""),
                    article.get("prix_vente", 0),
                    article.get("quantite", 0)
                )
            )

    def save_article(self):

        code = self.code_entry.get()
        titre = self.title_entry.get()

        if not code or not titre:
            messagebox.showwarning(
                "Erreur",
                "Veuillez remplir les champs obligatoires"
            )
            return

        payload = {
            "code": code,
            "titre": titre,
            "auteur": self.author_entry.get(),
            "categorie": self.category_entry.get(),
            "prix_achat": self.buy_price_entry.get(),
            "prix_vente": self.sell_price_entry.get(),
            "quantite": self.stock_entry.get()
        }

        result = APIClient.create_article(payload)

        if result["ok"]:

            messagebox.showinfo(
                "Succès",
                "Article enregistré"
            )

            self.clear_fields()
            self.load_articles()

        else:

            messagebox.showerror(
                "Erreur",
                result["error"]
            )

    def clear_fields(self):

        self.code_entry.delete(0, "end")
        self.title_entry.delete(0, "end")
        self.author_entry.delete(0, "end")
        self.category_entry.delete(0, "end")
        self.buy_price_entry.delete(0, "end")
        self.sell_price_entry.delete(0, "end")
        self.stock_entry.delete(0, "end")