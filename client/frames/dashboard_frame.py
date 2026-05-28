import customtkinter as ctk

VERT = "#008F39"

class DashboardFrame(ctk.CTkFrame):

    def __init__(self, parent, api):

        super().__init__(parent, fg_color="#ECEFF1")

        self.api = api

        titre = ctk.CTkLabel(
            self,
            text="📊 Tableau de bord",
            font=("Arial", 28, "bold"),
            text_color="#222"
        )
        titre.pack(pady=20)

        cards = ctk.CTkFrame(self, fg_color="transparent")
        cards.pack(fill="x", padx=20)

        self.card_articles = self._card(cards, "Articles", "0")
        self.card_articles.pack(side="left", expand=True, fill="both", padx=10)

        self.card_stock = self._card(cards, "Stock", "0")
        self.card_stock.pack(side="left", expand=True, fill="both", padx=10)

        self.card_users = self._card(cards, "Utilisateurs", "0")
        self.card_users.pack(side="left", expand=True, fill="both", padx=10)

        self.load_data()

    def _card(self, parent, titre, valeur):

        frame = ctk.CTkFrame(parent, fg_color="white", corner_radius=12)

        ctk.CTkLabel(
            frame,
            text=titre,
            font=("Arial", 18, "bold")
        ).pack(pady=(20,10))

        label = ctk.CTkLabel(
            frame,
            text=valeur,
            font=("Arial", 35, "bold"),
            text_color=VERT
        )
        label.pack(pady=(0,20))

        frame.valeur = label

        return frame

    def load_data(self):

        try:

            result = self.api.get_dashboard()

            print(result)

            if not result["ok"]:
                return

            data = result["data"]

            self.card_articles.valeur.configure(
                text=str(data.get("articles", 0))
            )

            self.card_stock.valeur.configure(
                text=str(data.get("stock", 0))
            )

            self.card_users.valeur.configure(
                text=str(data.get("users", 0))
            )

        except Exception as e:
            print("Dashboard Error :", e)