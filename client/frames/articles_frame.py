"""
LibrairieCI - Gestion des Articles
"""

import customtkinter as ctk
from tkinter import ttk, messagebox
from theme import *
from api_client import APIClient
import threading


class ArticlesFrame(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(parent, fg_color=GRIS_CLAIR)
        self._articles = []
        self._selected_id = None
        self._mode = "nouveau"  # "nouveau" ou "modifier"

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.build_ui()
        self.load_articles()

    def build_ui(self):

        # ── HEADER ──
        header = ctk.CTkFrame(self, fg_color=BLANC, height=70, corner_radius=0)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_propagate(False)
        header.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            header,
            text="📚  Gestion des Articles",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=NOIR_TEXTE
        ).grid(row=0, column=0, padx=20, pady=18, sticky="w")

        btn_frame_h = ctk.CTkFrame(header, fg_color="transparent")
        btn_frame_h.grid(row=0, column=2, padx=15)

        ctk.CTkButton(btn_frame_h, text="+ Nouvel Article",
                      command=self.reset_form,
                      fg_color=VERT, hover_color=VERT_SOMBRE,
                      font=ctk.CTkFont(size=13, weight="bold"),
                      height=38, width=145, corner_radius=6
                      ).pack(side="left", padx=4)

        ctk.CTkButton(btn_frame_h, text="✏ Modifier",
                      command=self.charger_pour_modifier,
                      fg_color=BLEU, hover_color="#0D47A1",
                      font=ctk.CTkFont(size=13, weight="bold"),
                      height=38, width=110, corner_radius=6
                      ).pack(side="left", padx=4)

        ctk.CTkButton(btn_frame_h, text="🗑 Supprimer",
                      command=self.supprimer_article,
                      fg_color=ROUGE, hover_color="#B71C1C",
                      font=ctk.CTkFont(size=13, weight="bold"),
                      height=38, width=120, corner_radius=6
                      ).pack(side="left", padx=4)

        ctk.CTkButton(btn_frame_h, text="🔄 Actualiser",
                      command=self.load_articles,
                      fg_color="#607D8B", hover_color="#455A64",
                      font=ctk.CTkFont(size=13, weight="bold"),
                      height=38, width=120, corner_radius=6
                      ).pack(side="left", padx=4)

        # ── CONTENU ──
        content = ctk.CTkFrame(self, fg_color=GRIS_CLAIR)
        content.grid(row=1, column=0, sticky="nsew")
        content.grid_columnconfigure(0, weight=3)
        content.grid_columnconfigure(1, weight=0)
        content.grid_rowconfigure(1, weight=1)

        # ── BARRE RECHERCHE ──
        search_bar = ctk.CTkFrame(content, fg_color=BLANC, corner_radius=8)
        search_bar.grid(row=0, column=0, columnspan=2, sticky="ew", padx=15, pady=(12, 6))

        self.search_entry = ctk.CTkEntry(
            search_bar,
            placeholder_text="🔍  Rechercher par titre, code, auteur, catégorie...",
            height=38, font=ctk.CTkFont(size=13), width=400
        )
        self.search_entry.pack(side="left", padx=10, pady=8)
        self.search_entry.bind("<Return>", lambda e: self.search_articles())

        ctk.CTkButton(search_bar, text="Rechercher", command=self.search_articles,
                      fg_color=VERT, hover_color=VERT_SOMBRE,
                      font=ctk.CTkFont(size=13, weight="bold"), height=38, corner_radius=6
                      ).pack(side="left", padx=4, pady=8)

        ctk.CTkButton(search_bar, text="Tout afficher", command=self.show_all,
                      fg_color="#607D8B", hover_color="#455A64",
                      font=ctk.CTkFont(size=13, weight="bold"), height=38, corner_radius=6
                      ).pack(side="left", padx=4, pady=8)

        self.lbl_count = ctk.CTkLabel(search_bar, text="",
                                       font=ctk.CTkFont(size=12), text_color=GRIS_TEXTE)
        self.lbl_count.pack(side="right", padx=12)

        # ── TABLEAU ──
        table_frame = ctk.CTkFrame(content, fg_color=BLANC, corner_radius=8)
        table_frame.grid(row=1, column=0, sticky="nsew", padx=(15, 6), pady=(0, 15))
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        style = ttk.Style()
        style.configure("Art.Treeview",
                         background=BLANC, foreground=NOIR_TEXTE,
                         fieldbackground=BLANC, rowheight=32,
                         font=("Segoe UI", 11))
        style.configure("Art.Treeview.Heading",
                         background=VERT, foreground=BLANC,
                         font=("Segoe UI", 11, "bold"), relief="flat")
        style.map("Art.Treeview",
                  background=[("selected", VERT_CLAIR)],
                  foreground=[("selected", VERT_SOMBRE)])

        cols = ("code", "titre", "auteur", "categorie", "prix_vente", "stock")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings",
                                  style="Art.Treeview", selectmode="browse")

        entetes = {
            "code": ("Code", 90),
            "titre": ("Titre / Nom", 240),
            "auteur": ("Auteur", 150),
            "categorie": ("Catégorie", 130),
            "prix_vente": ("Prix Vente (FCFA)", 140),
            "stock": ("Stock", 80),
        }
        for col, (label, width) in entetes.items():
            self.tree.heading(col, text=label)
            self.tree.column(col, width=width, minwidth=60)
        self.tree.column("prix_vente", anchor="e")
        self.tree.column("stock", anchor="center")
        self.tree.tag_configure("rupture", background="#FFEBEE", foreground=ROUGE)
        self.tree.tag_configure("alerte", background="#FFF8E1", foreground=ORANGE)

        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        # ── FORMULAIRE (scrollable) ──
        form_outer = ctk.CTkFrame(content, fg_color=BLANC, corner_radius=8, width=340)
        form_outer.grid(row=1, column=1, sticky="nsew", padx=(0, 15), pady=(0, 15))
        form_outer.grid_propagate(False)
        form_outer.grid_columnconfigure(0, weight=1)
        form_outer.grid_rowconfigure(0, weight=0)
        form_outer.grid_rowconfigure(1, weight=1)

        # Titre formulaire
        self.form_title_lbl = ctk.CTkLabel(
            form_outer, text="✚  Nouvel Article",
            font=ctk.CTkFont(size=16, weight="bold"), text_color=VERT
        )
        self.form_title_lbl.grid(row=0, column=0, pady=(16, 6))

        # Scrollable pour les champs
        scroll_form = ctk.CTkScrollableFrame(form_outer, fg_color=BLANC, width=310)
        scroll_form.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))
        scroll_form.grid_columnconfigure(0, weight=1)

        def add_field(parent, label, placeholder, required=False):
            lbl_text = f"{label} *" if required else label
            ctk.CTkLabel(parent, text=lbl_text,
                         font=ctk.CTkFont(size=12, weight="bold"),
                         text_color=NOIR_TEXTE, anchor="w"
                         ).pack(fill="x", padx=12, pady=(8, 2))
            entry = ctk.CTkEntry(parent, placeholder_text=placeholder,
                                  height=38, font=ctk.CTkFont(size=13))
            entry.pack(fill="x", padx=12, pady=(0, 4))
            return entry

        self.code_entry       = add_field(scroll_form, "Code article", "ex: LIV-001", required=True)
        self.title_entry      = add_field(scroll_form, "Titre / Nom", "ex: Le Petit Prince", required=True)
        self.author_entry     = add_field(scroll_form, "Auteur / Editeur", "ex: Antoine de Saint-Exupéry")
        self.category_entry   = add_field(scroll_form, "Catégorie", "ex: Roman, Scolaire...")
        self.buy_price_entry  = add_field(scroll_form, "Prix d'achat (FCFA)", "ex: 2000")
        self.sell_price_entry = add_field(scroll_form, "Prix de vente (FCFA)", "ex: 3500", required=True)
        self.stock_entry      = add_field(scroll_form, "Quantité en stock", "ex: 50", required=True)

        # Boutons Enregistrer / Annuler
        btn_zone = ctk.CTkFrame(scroll_form, fg_color="transparent")
        btn_zone.pack(fill="x", padx=12, pady=(12, 16))

        self.save_btn = ctk.CTkButton(
            btn_zone, text="💾 Enregistrer",
            command=self.save_article,
            fg_color=VERT, hover_color=VERT_SOMBRE,
            font=ctk.CTkFont(size=13, weight="bold"),
            height=40, corner_radius=6
        )
        self.save_btn.pack(fill="x", pady=(0, 6))

        ctk.CTkButton(
            btn_zone, text="✖ Annuler",
            command=self.reset_form,
            fg_color=ROUGE, hover_color="#B71C1C",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=40, corner_radius=6
        ).pack(fill="x")

    # ─────────────────────────────────────
    #  DONNÉES
    # ─────────────────────────────────────

    def load_articles(self):
        self.lbl_count.configure(text="⏳ Chargement...")

        def fetch():
            result = APIClient.get_articles()
            if result["ok"]:
                self._articles = result["data"]
                self.after(0, lambda: self.populate_table(self._articles))
                self.after(0, lambda: self.lbl_count.configure(
                    text=f"{len(self._articles)} article(s)"))
            else:
                self.after(0, lambda: self.lbl_count.configure(text="❌ Erreur connexion"))

        threading.Thread(target=fetch, daemon=True).start()

    def populate_table(self, data):
        self.tree.delete(*self.tree.get_children())
        for article in data:
            qte = article.get("quantite", 0)
            tag = "rupture" if qte == 0 else ("alerte" if qte <= 5 else "")
            prix = f"{int(article.get('prix_vente', 0)):,}".replace(",", " ")
            self.tree.insert("", "end",
                             iid=str(article["id"]),
                             values=(
                                 article.get("code", ""),
                                 article.get("titre", ""),
                                 article.get("auteur", ""),
                                 article.get("categorie", ""),
                                 prix,
                                 qte
                             ),
                             tags=(tag,))

    def search_articles(self):
        q = self.search_entry.get().lower().strip()
        if not q:
            self.populate_table(self._articles)
            return
        filtered = [a for a in self._articles
                    if q in a.get("titre", "").lower()
                    or q in a.get("code", "").lower()
                    or q in a.get("auteur", "").lower()
                    or q in a.get("categorie", "").lower()]
        self.populate_table(filtered)
        self.lbl_count.configure(text=f"🔍 {len(filtered)} résultat(s)")

    def show_all(self):
        self.search_entry.delete(0, "end")
        self.populate_table(self._articles)
        self.lbl_count.configure(text=f"{len(self._articles)} article(s)")

    # ─────────────────────────────────────
    #  FORMULAIRE
    # ─────────────────────────────────────

    def on_select(self, event=None):
        sel = self.tree.selection()
        if sel:
            self._selected_id = int(sel[0])

    def reset_form(self):
        self._selected_id = None
        self._mode = "nouveau"
        self.form_title_lbl.configure(text="✚  Nouvel Article", text_color=VERT)
        self.save_btn.configure(text="💾 Enregistrer", fg_color=VERT, hover_color=VERT_SOMBRE)
        for entry in [self.code_entry, self.title_entry, self.author_entry,
                      self.category_entry, self.buy_price_entry,
                      self.sell_price_entry, self.stock_entry]:
            entry.delete(0, "end")

    def charger_pour_modifier(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Sélection", "Sélectionnez d'abord un article dans le tableau.")
            return
        art_id = int(sel[0])
        art = next((a for a in self._articles if a["id"] == art_id), None)
        if not art:
            return
        self._selected_id = art_id
        self._mode = "modifier"
        self.form_title_lbl.configure(text="✏  Modifier Article", text_color=BLEU)
        self.save_btn.configure(text="💾 Mettre à jour", fg_color=BLEU, hover_color="#0D47A1")

        self.code_entry.delete(0, "end")
        self.code_entry.insert(0, art.get("code", ""))
        self.title_entry.delete(0, "end")
        self.title_entry.insert(0, art.get("titre", ""))
        self.author_entry.delete(0, "end")
        self.author_entry.insert(0, art.get("auteur", ""))
        self.category_entry.delete(0, "end")
        self.category_entry.insert(0, art.get("categorie", ""))
        self.buy_price_entry.delete(0, "end")
        self.buy_price_entry.insert(0, str(art.get("prix_achat", "")))
        self.sell_price_entry.delete(0, "end")
        self.sell_price_entry.insert(0, str(art.get("prix_vente", "")))
        self.stock_entry.delete(0, "end")
        self.stock_entry.insert(0, str(art.get("quantite", "")))

    def save_article(self):
        code  = self.code_entry.get().strip()
        titre = self.title_entry.get().strip()

        if not code or not titre:
            messagebox.showwarning("Champs requis", "Le code et le titre sont obligatoires (*).")
            return

        try:
            prix_v = float(self.sell_price_entry.get().strip() or 0)
            qte    = int(self.stock_entry.get().strip() or 0)
        except ValueError:
            messagebox.showwarning("Valeur invalide", "Le prix de vente et la quantité doivent être numériques.")
            return

        payload = {
            "code":        code,
            "titre":       titre,
            "auteur":      self.author_entry.get().strip(),
            "categorie":   self.category_entry.get().strip(),
            "prix_achat":  float(self.buy_price_entry.get().strip() or 0),
            "prix_vente":  prix_v,
            "quantite":    qte,
        }

        self.save_btn.configure(state="disabled", text="⏳ En cours...")

        def do():
            if self._mode == "modifier" and self._selected_id:
                result = APIClient.update_article(self._selected_id, payload)
                msg_ok = "Article mis à jour avec succès !"
            else:
                result = APIClient.create_article(payload)
                msg_ok = "Article enregistré avec succès !"

            def after():
                self.save_btn.configure(state="normal",
                                        text="💾 Enregistrer" if self._mode == "nouveau" else "💾 Mettre à jour")
                if result["ok"]:
                    messagebox.showinfo("✅ Succès", msg_ok)
                    self.reset_form()
                    self.load_articles()
                else:
                    messagebox.showerror("Erreur", result["error"])

            self.after(0, after)

        threading.Thread(target=do, daemon=True).start()

    def supprimer_article(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Sélection", "Sélectionnez d'abord un article à supprimer.")
            return
        art_id = int(sel[0])
        art = next((a for a in self._articles if a["id"] == art_id), None)
        if not art:
            return
        if not messagebox.askyesno("Confirmer", f"Supprimer l'article :\n\n« {art.get('titre','')} » ?\n\nCette action est irréversible."):
            return

        def do():
            result = APIClient.delete_article(art_id)
            def after():
                if result["ok"]:
                    messagebox.showinfo("✅ Supprimé", "Article supprimé avec succès.")
                    self.reset_form()
                    self.load_articles()
                else:
                    messagebox.showerror("Erreur", result["error"])
            self.after(0, after)

        threading.Thread(target=do, daemon=True).start()
