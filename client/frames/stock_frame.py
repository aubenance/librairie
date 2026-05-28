import customtkinter as ctk
from tkinter import ttk, messagebox

VERT = "#008F39"

class StockFrame(ctk.CTkFrame):

    def __init__(self, parent, api):

        super().__init__(parent, fg_color="#ECEFF1")

        self.api = api
        self.articles = []

        titre = ctk.CTkLabel(
            self,
            text="📦 Gestion du Stock",
            font=("Arial", 28, "bold")
        )
        titre.pack(pady=20)

        self.table = ttk.Treeview(
            self,
            columns=("code","nom","stock"),
            show="headings",
            height=18
        )

        self.table.heading("code", text="Code")
        self.table.heading("nom", text="Article")
        self.table.heading("stock", text="Stock")

        self.table.pack(fill="both", expand=True, padx=20, pady=20)

        self.load_data()

    def load_data(self):

        try:

            result = self.api.get_articles()

            print(result)

            if not result["ok"]:
                messagebox.showerror("Erreur", str(result["error"]))
                return

            self.articles = result["data"]

            self.refresh_table()

        except Exception as e:
            messagebox.showerror("Erreur Stock", str(e))

    def refresh_table(self):

        for item in self.table.get_children():
            self.table.delete(item)

        for article in self.articles:

            self.table.insert(
                "",
                "end",
                values=(
                    article.get("code",""),
                    article.get("nom",""),
                    article.get("stock",0)
                )
            )