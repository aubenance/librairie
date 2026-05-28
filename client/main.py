# =========================
# main.py
# =========================

import customtkinter as ctk

from frames.dashboard_frame import DashboardFrame
from frames.vente_frame import VenteFrame
from frames.stock_frame import StockFrame
from frames.articles_frame import ArticlesFrame
from frames.rapports_frame import RapportsFrame
from frames.users_frame import UsersFrame

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")


class LibrairieApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("LibrairieCI — Gestion de Librairie")
        self.geometry("1600x900")

        # ======================
        # SIDEBAR
        # ======================

        self.sidebar = ctk.CTkFrame(
            self,
            width=260,
            fg_color="#008F39",
            corner_radius=0
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # ======================
        # CONTENT
        # ======================

        self.content = ctk.CTkFrame(
            self,
            fg_color="#EDEFF3",
            corner_radius=0
        )
        self.content.pack(side="right", fill="both", expand=True)

        # ======================
        # LOGO
        # ======================

        logo = ctk.CTkLabel(
            self.sidebar,
            text="📚  LibrairieCI",
            font=("Arial", 24, "bold"),
            text_color="white"
        )
        logo.pack(pady=(30, 10))

        subtitle = ctk.CTkLabel(
            self.sidebar,
            text="Gestion Professionnelle",
            font=("Arial", 14),
            text_color="#DDEBDD"
        )
        subtitle.pack(pady=(0, 30))

        # ======================
        # USER BOX
        # ======================

        user_box = ctk.CTkFrame(
            self.sidebar,
            fg_color="#007532",
            corner_radius=0,
            height=90
        )
        user_box.pack(fill="x")

        user_title = ctk.CTkLabel(
            user_box,
            text="👤  Système Admin",
            font=("Arial", 16, "bold"),
            text_color="white"
        )
        user_title.pack(pady=(18, 4))

        user_name = ctk.CTkLabel(
            user_box,
            text="🗝 Administrateur",
            font=("Arial", 13),
            text_color="#DDEBDD"
        )
        user_name.pack()

        # ======================
        # PAGES
        # ======================

        self.frames = {}

        self.frames["dashboard"] = DashboardFrame(self.content)
        self.frames["vente"] = VenteFrame(self.content)
        self.frames["stock"] = StockFrame(self.content)
        self.frames["articles"] = ArticlesFrame(self.content)
        self.frames["rapports"] = RapportsFrame(self.content)
        self.frames["users"] = UsersFrame(self.content)

        # ======================
        # MENU BUTTONS
        # ======================

        self.create_menu_button(
            "🏠  Tableau de bord",
            "dashboard"
        )

        self.create_menu_button(
            "🛒  Nouvelle Vente",
            "vente"
        )

        self.create_menu_button(
            "📦  Stock",
            "stock"
        )

        self.create_menu_button(
            "📘  Articles",
            "articles"
        )

        self.create_menu_button(
            "📊  Rapports & Stats",
            "rapports"
        )

        self.create_menu_button(
            "👥  Utilisateurs",
            "users"
        )

        # ======================
        # PAGE PAR DEFAUT
        # ======================

        self.show_frame("dashboard")

    # =========================
    # MENU BUTTON
    # =========================

    def create_menu_button(self, text, frame_name):

        btn = ctk.CTkButton(
            self.sidebar,
            text=text,
            height=50,
            anchor="w",
            fg_color="#008F39",
            hover_color="#00A944",
            corner_radius=0,
            font=("Arial", 15, "bold"),
            command=lambda: self.show_frame(frame_name)
        )

        btn.pack(fill="x")

    # =========================
    # SHOW FRAME
    # =========================

    def show_frame(self, name):

        # cacher toutes les pages
        for frame in self.frames.values():
            frame.pack_forget()

        # afficher une seule page
        frame = self.frames[name]
        frame.pack(fill="both", expand=True)


# =========================
# START APP
# =========================

if __name__ == "__main__":
    app = LibrairieApp()
    app.mainloop()