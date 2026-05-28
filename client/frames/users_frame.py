import customtkinter as ctk
from tkinter import ttk, messagebox
from theme import *
from api_client import APIClient


class UsersFrame(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(parent, fg_color=GRIS_CLAIR)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.build_ui()
        self.load_users()

    def build_ui(self):

        header = ctk.CTkFrame(self, fg_color=BLANC, height=70)
        header.grid(row=0, column=0, sticky="ew")

        title = ctk.CTkLabel(
            header,
            text="Gestion des Utilisateurs",
            font=("Arial", 24, "bold")
        )

        title.pack(side="left", padx=20, pady=20)

        content = ctk.CTkFrame(self, fg_color=BLANC)
        content.grid(row=1, column=0, sticky="nsew", padx=15, pady=15)

        content.grid_rowconfigure(0, weight=1)
        content.grid_columnconfigure(0, weight=1)

        columns = (
            "nom",
            "prenom",
            "username",
            "role"
        )

        self.tree = ttk.Treeview(
            content,
            columns=columns,
            show="headings"
        )

        self.tree.heading("nom", text="Nom")
        self.tree.heading("prenom", text="Prénom")
        self.tree.heading("username", text="Identifiant")
        self.tree.heading("role", text="Rôle")

        self.tree.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(
            content,
            orient="vertical",
            command=self.tree.yview
        )

        scrollbar.grid(row=0, column=1, sticky="ns")

        self.tree.configure(yscrollcommand=scrollbar.set)

    def load_users(self):

        result = APIClient.get_users()

        if not result["ok"]:
            messagebox.showerror("Erreur", result["error"])
            return

        self.tree.delete(*self.tree.get_children())

        for user in result["data"]:

            self.tree.insert(
                "",
                "end",
                values=(
                    user.get("nom", ""),
                    user.get("prenom", ""),
                    user.get("username", ""),
                    user.get("role", "")
                )
            )