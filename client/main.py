import customtkinter as ctk

from theme import *

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
        self.geometry("1400x800")

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.current_frame = None

        self.build_sidebar()
        self.build_content()

        self.show_frame("dashboard")

    # =====================================================
    # SIDEBAR
    # =====================================================

    def build_sidebar(self):

        self.sidebar = ctk.CTkFrame(
            self,
            width=260,
            fg_color="#008f39",
            corner_radius=0
        )

        self.sidebar.grid(row=0, column=0, sticky="ns")

        # LOGO
        logo = ctk.CTkLabel(
            self.sidebar,
            text="📚  LibrairieCI",
            font=("Arial", 32, "bold"),
            text_color="white"
        )

        logo.pack(pady=(40, 10))

        subtitle = ctk.CTkLabel(
            self.sidebar,
            text="Gestion Professionnelle",
            font=("Arial", 16),
            text_color="#d1fae5"
        )

        subtitle.pack(pady=(0, 30))

        # USER
        user_frame = ctk.CTkFrame(
            self.sidebar,
            fg_color="#00732d",
            corner_radius=0,
            height=80
        )

        user_frame.pack(fill="x")

        user_label = ctk.CTkLabel(
            user_frame,
            text="👤  Système Admin",
            font=("Arial", 20, "bold"),
            text_color="white"
        )

        user_label.pack(pady=(20, 5))

        role_label = ctk.CTkLabel(
            user_frame,
            text="🔑 Administrateur",
            font=("Arial", 14),
            text_color="#d1fae5"
        )

        role_label.pack()

        # MENU
        menus = [
            ("🏠 Tableau de bord", "dashboard"),
            ("🛒 Nouvelle Vente", "vente"),
            ("📦 Stock", "stock"),
            ("📚 Articles", "articles"),
            ("📊 Rapports & Stats", "rapports"),
            ("👥 Utilisateurs", "users"),
        ]

        for text, page in menus:

            btn = ctk.CTkButton(
                self.sidebar,
                text=text,
                height=50,
                corner_radius=0,
                anchor="w",
                fg_color="#008f39",
                hover_color="#00a63f",
                font=("Arial", 18),
                command=lambda p=page: self.show_frame(p)
            )

            btn.pack(fill="x")

    # =====================================================
    # CONTENT
    # =====================================================

    def build_content(self):

        self.content_frame = ctk.CTkFrame(
            self,
            fg_color="#ecf0f1",
            corner_radius=0
        )

        self.content_frame.grid(
            row=0,
            column=1,
            sticky="nsew"
        )

        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)

    # =====================================================
    # SHOW FRAME
    # =====================================================

    def clear_content(self):

        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def show_frame(self, page):

        self.clear_content()

        if page == "dashboard":
            frame = DashboardFrame(self.content_frame)

        elif page == "vente":
            frame = VenteFrame(self.content_frame)

        elif page == "stock":
            frame = StockFrame(self.content_frame)

        elif page == "articles":
            frame = ArticlesFrame(self.content_frame)

        elif page == "rapports":
            frame = RapportsFrame(self.content_frame)

        elif page == "users":
            frame = UsersFrame(self.content_frame)

        else:
            return

        frame.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        self.current_frame = frame


if __name__ == "__main__":

    app = LibrairieApp()
    app.mainloop()