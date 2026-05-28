import customtkinter as ctk
from tkinter import ttk, messagebox

class UsersFrame(ctk.CTkFrame):

    def __init__(self, parent, api):

        super().__init__(parent, fg_color="#ECEFF1")

        self.api = api

        titre = ctk.CTkLabel(
            self,
            text="👥 Gestion des utilisateurs",
            font=("Arial", 28, "bold")
        )
        titre.pack(pady=20)

        self.table = ttk.Treeview(
            self,
            columns=("username","role"),
            show="headings",
            height=20
        )

        self.table.heading("username", text="Utilisateur")
        self.table.heading("role", text="Rôle")

        self.table.pack(fill="both", expand=True, padx=20, pady=20)

        self.load_users()

    def load_users(self):

        try:

            result = self.api.get_users()

            print(result)

            if not result["ok"]:
                return

            users = result["data"]

            for item in self.table.get_children():
                self.table.delete(item)

            for user in users:

                self.table.insert(
                    "",
                    "end",
                    values=(
                        user.get("username",""),
                        user.get("role","")
                    )
                )

        except Exception as e:
            messagebox.showerror("Erreur Users", str(e))