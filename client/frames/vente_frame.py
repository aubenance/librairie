import customtkinter as ctk
from tkinter import ttk, messagebox

VERT = "#008F39"

class VenteFrame(ctk.CTkFrame):

    def __init__(self, parent, api):

        super().__init__(parent, fg_color="#ECEFF1")

        self.api = api
        self.articles = []

        titre = ctk.CTkLabel(
            self,
            text="🛒 Nouvelle Vente",
            font=("Arial", 28, "bold")
        )
        titre.pack(pady=20)

        self.table = ttk.Treeview(
            self,
            columns=("nom","prix","stock"),
            show="headings",
            height=18
        )

        self.table.heading("nom", text="Article")
        self.table.heading("prix", text="Prix")
        self.table.heading("stock", text="Stock")

        self.table.pack(fill="both", expand=True, padx=20, pady=20)

        self.load_articles()

    def load_articles(self):

        try:

            result = self.api.get_articles()

            print(result)

            if not result["ok"]:
                messagebox.showerror("Erreur", str(result["error"]))
                return

            self.articles = result["data"]

            self.refresh()

        except Exception as e:
            messagebox.showerror("Erreur Vente", str(e))

    def refresh(self):

        for item in self.table.get_children():
            self.table.delete(item)

        for article in self.articles:

            self.table.insert(
                "",
                "end",
                values=(
                    article.get("nom",""),
                    article.get("prix_vente",0),
                    article.get("stock",0)
                )
            )