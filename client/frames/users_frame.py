"""
LibrairieCI - Gestion des Utilisateurs
"""

import customtkinter as ctk
from tkinter import ttk, messagebox
from theme import *
from api_client import APIClient
import threading


class UsersFrame(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(parent, fg_color=GRIS_CLAIR)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.build_ui()
        self.load_users()

    def build_ui(self):

        # HEADER
        header = ctk.CTkFrame(self, fg_color=BLANC, height=70, corner_radius=0)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_propagate(False)
        header.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            header,
            text="👥  Gestion des Utilisateurs",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=NOIR_TEXTE
        ).grid(row=0, column=0, padx=20, pady=18, sticky="w")

        self.lbl_status = ctk.CTkLabel(
            header, text="", font=ctk.CTkFont(size=12), text_color=GRIS_TEXTE
        )
        self.lbl_status.grid(row=0, column=1, sticky="e", padx=10)

        ctk.CTkButton(
            header,
            text="🔄 Actualiser",
            command=self.load_users,
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
            placeholder_text="🔍  Rechercher par nom, prénom, identifiant...",
            width=350,
            height=38,
            font=ctk.CTkFont(size=13)
        )
        self.search_entry.pack(side="left", padx=10, pady=10)
        self.search_entry.bind("<Return>", lambda e: self.search_users())

        ctk.CTkButton(
            search_frame,
            text="Rechercher",
            command=self.search_users,
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
        content = ctk.CTkFrame(self, fg_color=BLANC, corner_radius=8)
        content.grid(row=2, column=0, sticky="nsew", padx=15, pady=(0, 15))
        content.grid_rowconfigure(0, weight=1)
        content.grid_columnconfigure(0, weight=1)

        style = ttk.Style()
        style.configure("Users.Treeview",
                         background=BLANC, foreground=NOIR_TEXTE,
                         fieldbackground=BLANC, rowheight=34,
                         font=("Segoe UI", 12))
        style.configure("Users.Treeview.Heading",
                         background=VERT, foreground=BLANC,
                         font=("Segoe UI", 11, "bold"),
                         relief="flat")
        style.map("Users.Treeview",
                  background=[("selected", VERT_CLAIR)],
                  foreground=[("selected", VERT_SOMBRE)])

        columns = ("nom", "prenom", "username", "role")

        self.tree = ttk.Treeview(
            content,
            columns=columns,
            show="headings",
            style="Users.Treeview",
            selectmode="browse"
        )

        entetes = {
            "nom": ("Nom", 180),
            "prenom": ("Prénom", 180),
            "username": ("Identifiant", 180),
            "role": ("Rôle", 140),
        }

        for col, (label, width) in entetes.items():
            self.tree.heading(col, text=label)
            self.tree.column(col, width=width, minwidth=80)

        self.tree.tag_configure("admin", background="#E8F5E9", foreground=VERT_SOMBRE)

        self.tree.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(content, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)

    def load_users(self):
        """Chargement asynchrone pour ne pas bloquer l'UI"""
        self.lbl_status.configure(text="⏳ Chargement...")

        def fetch():
            result = APIClient.get_users()
            if result["ok"]:
                self._users = result["data"]
                self.after(0, lambda: self.populate_table(self._users))
                self.after(0, lambda: self.lbl_status.configure(
                    text=f"✅ {len(self._users)} utilisateur(s)"))
            else:
                self.after(0, lambda: self.lbl_status.configure(text="❌ Erreur de connexion"))

        threading.Thread(target=fetch, daemon=True).start()

    def populate_table(self, data):
        self.tree.delete(*self.tree.get_children())
        for user in data:
            role = user.get("role", "")
            tag = "admin" if role == "admin" else ""
            self.tree.insert(
                "", "end",
                values=(
                    user.get("nom", ""),
                    user.get("prenom", ""),
                    user.get("username", ""),
                    role.capitalize()
                ),
                tags=(tag,)
            )

    def search_users(self):
        query = self.search_entry.get().lower().strip()
        if not query or not hasattr(self, "_users"):
            return
        filtered = [
            u for u in self._users
            if query in u.get("nom", "").lower()
            or query in u.get("prenom", "").lower()
            or query in u.get("username", "").lower()
        ]
        self.populate_table(filtered)
        self.lbl_status.configure(text=f"🔍 {len(filtered)} résultat(s)")

    def show_all(self):
        self.search_entry.delete(0, "end")
        if hasattr(self, "_users"):
            self.populate_table(self._users)
