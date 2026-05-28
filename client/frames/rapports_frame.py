import customtkinter as ctk
from tkinter import ttk, messagebox

class RapportsFrame(ctk.CTkFrame):

    def __init__(self, parent, api):

        super().__init__(parent, fg_color="#ECEFF1")

        self.api = api

        titre = ctk.CTkLabel(
            self,
            text="📈 Rapports & Statistiques",
            font=("Arial", 28, "bold")
        )
        titre.pack(pady=20)

        self.table = ttk.Treeview(
            self,
            columns=("date","montant"),
            show="headings",
            height=20
        )

        self.table.heading("date", text="Date")
        self.table.heading("montant", text="Montant")

        self.table.pack(fill="both", expand=True, padx=20, pady=20)

        self.load_data()

    def load_data(self):

        try:

            result = self.api.get_ventes()

            print(result)

            if not result["ok"]:
                return

            ventes = result["data"]

            for item in self.table.get_children():
                self.table.delete(item)

            for vente in ventes:

                self.table.insert(
                    "",
                    "end",
                    values=(
                        vente.get("date",""),
                        vente.get("total",0)
                    )
                )

        except Exception as e:
            messagebox.showerror("Erreur Rapports", str(e))