import customtkinter as ctk
from theme import *


class RapportsFrame(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(parent, fg_color=GRIS_CLAIR)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.build_ui()

    def build_ui(self):

        header = ctk.CTkFrame(self, fg_color=BLANC, height=70)
        header.grid(row=0, column=0, sticky="ew")

        title = ctk.CTkLabel(
            header,
            text="Rapports & Statistiques",
            font=("Arial", 24, "bold")
        )

        title.pack(side="left", padx=20, pady=20)

        content = ctk.CTkFrame(self, fg_color=BLANC)
        content.grid(row=1, column=0, sticky="nsew", padx=15, pady=15)

        label = ctk.CTkLabel(
            content,
            text="Module de rapports en cours de développement",
            font=("Arial", 18)
        )

        label.pack(pady=100)