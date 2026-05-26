# -*- coding: utf-8 -*-

"""
LibrairieCI - Login Frame
"""

import customtkinter as ctk

from tkinter import messagebox

from theme import *
from api_client import APIClient, session


class LoginFrame(ctk.CTkFrame):

    def __init__(self, parent, on_success):

        super().__init__(
            parent,
            fg_color=GRIS_CLAIR
        )

        self.on_success = on_success

        self._build()

    # ─────────────────────────────────────
    # UI
    # ─────────────────────────────────────

    def _build(self):

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        container = ctk.CTkFrame(
            self,
            width=460,
            height=520,
            fg_color=BLANC,
            corner_radius=18
        )

        container.grid(
            row=0,
            column=0
        )

        container.grid_propagate(False)

        # TITRE

        ctk.CTkLabel(
            container,
            text="Connexion",
            font=ctk.CTkFont(
                size=32,
                weight="bold"
            ),
            text_color=VERT
        ).pack(
            pady=(40, 10)
        )

        ctk.CTkLabel(
            container,
            text="Entrez vos identifiants",
            font=ctk.CTkFont(size=14),
            text_color=GRIS_TEXTE
        ).pack(
            pady=(0, 25)
        )

        # URL SERVEUR

        self.entry_server = ctk.CTkEntry(
            container,
            height=42,
            width=360
        )

        self.entry_server.insert(
            0,
            session.config.get(
                "server_url",
                ""
            )
        )

        self.entry_server.pack(
            pady=8
        )

        # USERNAME

        ctk.CTkLabel(
            container,
            text="Identifiant",
            anchor="w",
            text_color=NOIR_TEXTE
        ).pack(
            fill="x",
            padx=50,
            pady=(20, 4)
        )

        self.entry_user = ctk.CTkEntry(
            container,
            height=44,
            width=360
        )

        self.entry_user.pack()

        # PASSWORD

        ctk.CTkLabel(
            container,
            text="Mot de passe",
            anchor="w",
            text_color=NOIR_TEXTE
        ).pack(
            fill="x",
            padx=50,
            pady=(20, 4)
        )

        self.entry_pass = ctk.CTkEntry(
            container,
            show="*",
            height=44,
            width=360
        )

        self.entry_pass.pack()

        # STATUS

        self.lbl_status = ctk.CTkLabel(
            container,
            text="",
            text_color=ROUGE,
            font=ctk.CTkFont(size=12)
        )

        self.lbl_status.pack(
            pady=(20, 0)
        )

        # BTN LOGIN

        self.btn_login = ctk.CTkButton(
            container,
            text="SE CONNECTER",
            command=self._login,
            fg_color=VERT,
            hover_color=VERT_SOMBRE,
            height=48,
            width=360,
            font=ctk.CTkFont(
                size=15,
                weight="bold"
            )
        )

        self.btn_login.pack(
            pady=(30, 10)
        )

        # TEST

        ctk.CTkButton(
            container,
            text="Tester la connexion serveur",
            command=self._test_server,
            fg_color="transparent",
            text_color=VERT,
            hover_color="#E8F5E9"
        ).pack()

    # ─────────────────────────────────────
    # TEST SERVER
    # ─────────────────────────────────────

    def _test_server(self):

        url = self.entry_server.get().strip()

        session.config["server_url"] = url

        ok = APIClient.test_connection()

        if ok:

            self.lbl_status.configure(
                text="Connexion serveur OK",
                text_color=VERT
            )

        else:

            self.lbl_status.configure(
                text="Serveur inaccessible",
                text_color=ROUGE
            )

    # ─────────────────────────────────────
    # LOGIN
    # ─────────────────────────────────────

    def _login(self):

        username = self.entry_user.get().strip()

        password = self.entry_pass.get().strip()

        server = self.entry_server.get().strip()

        if not username or not password:

            self.lbl_status.configure(
                text="Veuillez remplir les champs"
            )

            return

        session.config["server_url"] = server

        self.btn_login.configure(
            state="disabled",
            text="Connexion..."
        )

        self.update()

        result = APIClient.login(
            username,
            password
        )

        self.btn_login.configure(
            state="normal",
            text="SE CONNECTER"
        )

        if result["ok"]:

            self.lbl_status.configure(
                text="Connexion reussie",
                text_color=VERT
            )

            self.after(
                500,
                self.on_success
            )

        else:

            self.lbl_status.configure(
                text=result.get(
                    "error",
                    "Erreur connexion"
                ),
                text_color=ROUGE
            )

            messagebox.showerror(
                "Connexion",
                result.get(
                    "error",
                    "Erreur connexion"
                )
            )