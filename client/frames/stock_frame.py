"""
LibrairieCI - Consultation du Stock
"""

import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
from theme import *
from api_client import APIClient, session
import threading, csv, os


class StockFrame(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(parent, fg_color=GRIS_CLAIR)
        self.pack(fill="both", expand=True)
        self._articles = []
        self._build()
        self._load()

    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # ── En-tête ──
        header = ctk.CTkFrame(self, fg_color=BLANC, corner_radius=0, height=65)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_propagate(False)
        header.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(header, text="📦  Consultation du Stock",
                     font=ctk.CTkFont(size=20, weight="bold"),
                     text_color=NOIR_TEXTE).grid(row=0, column=0, padx=20, pady=18, sticky="w")

        btn_frame = ctk.CTkFrame(header, fg_color=BLANC)
        btn_frame.grid(row=0, column=2, padx=16, pady=10)
        make_button(btn_frame, "🔄 Actualiser", self._load,
                    color=VERT, width=120, height=36).pack(side="left", padx=4)
        if session.is_admin:
            make_button(btn_frame, "📄 Exporter CSV", self._export_csv,
                        color=BLEU, hover_color="#0D47A1", width=130, height=36).pack(side="left", padx=4)

        # ── Cartes stats ──
        stats_frame = ctk.CTkFrame(self, fg_color=GRIS_CLAIR, height=100)
        stats_frame.grid(row=1, column=0, sticky="ew", padx=16, pady=(12, 0))

        self._lbl_stats = {}
        defs = [
            ("total",   "📚", "Total articles",    "0",  VERT),
            ("faible",  "⚠",  "Stock faible (≤5)", "0",  ORANGE),
            ("rupture", "❌", "En rupture (= 0)",  "0",  ROUGE),
            ("valeur",  "💰", "Valeur stock",      "0 FCFA", BLEU),
        ]
        for i, (key, icon, title, val, color) in enumerate(defs):
            card = ctk.CTkFrame(stats_frame, fg_color=BLANC, corner_radius=10,
                                border_width=2, border_color=color, width=210, height=78)
            card.grid(row=0, column=i, padx=8, pady=6, sticky="nsew")
            card.grid_propagate(False)

            top = ctk.CTkFrame(card, fg_color=BLANC)
            top.pack(fill="x", padx=10, pady=(8, 0))
            ctk.CTkLabel(top, text=icon, font=ctk.CTkFont(size=18),
                         text_color=color).pack(side="left")
            ctk.CTkLabel(top, text=title, font=ctk.CTkFont(size=10),
                         text_color=GRIS_TEXTE).pack(side="left", padx=6)

            lbl = ctk.CTkLabel(card, text=val, font=ctk.CTkFont(size=17, weight="bold"),
                               text_color=color)
            lbl.pack()
            self._lbl_stats[key] = lbl

        # ── Filtres + Liste ──
        body = ctk.CTkFrame(self, fg_color=BLANC, corner_radius=0)
        body.grid(row=2, column=0, sticky="nsew", padx=12, pady=12)
        body.grid_columnconfigure(0, weight=1)
        body.grid_rowconfigure(1, weight=1)

        # Barre filtres
        filt = ctk.CTkFrame(body, fg_color=BLANC, height=50)
        filt.grid(row=0, column=0, sticky="ew", padx=10, pady=8)
        filt.grid_propagate(False)

        self.entry_search = ctk.CTkEntry(filt, placeholder_text="🔍 Rechercher...",
                                          width=280, height=34, font=ctk.CTkFont(size=12))
        self.entry_search.pack(side="left", padx=(0,8), pady=8)
        self.entry_search.bind("<Return>", lambda e: self._filter(self.entry_search.get()))
        make_button(filt, "Rechercher", lambda: self._filter(self.entry_search.get()),
                    width=100, height=34).pack(side="left", padx=2)

        # Filtres rapides
        ctk.CTkLabel(filt, text=" | Filtre :", font=ctk.CTkFont(size=12),
                     text_color=GRIS_TEXTE).pack(side="left", padx=(16, 6))

        for label, cmd_arg, color in [
            ("Tout", "",         GRIS_TEXTE),
            ("⚠ Stock faible", "faible",   ORANGE),
            ("❌ Rupture",      "rupture",  ROUGE),
        ]:
            make_button(filt, label,
                        lambda a=cmd_arg: self._filter_rapide(a),
                        color=color, hover_color="#424242" if color==GRIS_TEXTE else color,
                        width=120, height=34).pack(side="left", padx=3)

        self.lbl_count = ctk.CTkLabel(filt, text="", font=ctk.CTkFont(size=12), text_color=GRIS_TEXTE)
        self.lbl_count.pack(side="right", padx=16)

        # Grille stock
        grid_frame = ctk.CTkFrame(body, fg_color=BLANC)
        grid_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0,10))
        grid_frame.grid_columnconfigure(0, weight=1)
        grid_frame.grid_rowconfigure(0, weight=1)

        cols = ("id","code","titre","auteur","categorie","prix_achat","prix_vente","quantite")
        widths = {"id":0,"code":80,"titre":230,"auteur":150,"categorie":110,
                  "prix_achat":110,"prix_vente":120,"quantite":80}
        self.tree, scroll = make_treeview(grid_frame, cols, widths)
        heads = {"id":"ID","code":"Code","titre":"Titre / Nom","auteur":"Auteur",
                 "categorie":"Catégorie","prix_achat":"Prix Achat","prix_vente":"Prix Vente","quantite":"Qté Stock"}
        for c, h in heads.items():
            self.tree.heading(c, text=h)
        self.tree.column("id", width=0, stretch=False)
        self.tree.column("prix_achat", anchor="e")
        self.tree.column("prix_vente", anchor="e")
        self.tree.column("quantite", anchor="center")

        self.tree.grid(row=0, column=0, sticky="nsew")
        scroll.grid(row=0, column=1, sticky="ns")

    # ─────────────────────────────────────
    #  DONNÉES
    # ─────────────────────────────────────

    def _load(self):
        self.lbl_count.configure(text="⏳ Chargement...")

        def fetch():
            result = APIClient.get_articles()
            if result["ok"]:
                self._articles = result["data"]
                self._filter()
                self._update_stats()
            else:
                self.lbl_count.configure(text="❌ Erreur")

        threading.Thread(target=fetch, daemon=True).start()

    def _update_stats(self):
        total   = len(self._articles)
        faible  = sum(1 for a in self._articles if 0 < a.get("quantite",0) <= 5)
        rupture = sum(1 for a in self._articles if a.get("quantite",0) == 0)
        valeur  = sum(a.get("prix_vente",0) * a.get("quantite",0) for a in self._articles)

        self._lbl_stats["total"].configure(text=str(total))
        self._lbl_stats["faible"].configure(text=str(faible))
        self._lbl_stats["rupture"].configure(text=str(rupture))
        self._lbl_stats["valeur"].configure(text=format_fcfa(valeur))

    def _filter(self, q=""):
        if not q:
            data = self._articles
        else:
            q_low = q.lower()
            data = [a for a in self._articles
                    if q_low in a.get("titre","").lower()
                    or q_low in a.get("code","").lower()
                    or q_low in a.get("auteur","").lower()
                    or q_low in a.get("categorie","").lower()]
        self._populate(data)

    def _filter_rapide(self, mode: str):
        if mode == "faible":
            data = [a for a in self._articles if 0 < a.get("quantite",0) <= 5]
        elif mode == "rupture":
            data = [a for a in self._articles if a.get("quantite",0) == 0]
        else:
            data = self._articles
            self.entry_search.delete(0, "end")
        self._populate(data)

    def _populate(self, data):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for art in data:
            qte = art.get("quantite", 0)
            pa  = f"{int(art.get('prix_achat',0)):,}".replace(",", " ")
            pv  = f"{int(art.get('prix_vente',0)):,}".replace(",", " ")
            tag = "rupture" if qte == 0 else ("alerte" if qte <= 5 else "")
            self.tree.insert("", "end", iid=art["id"],
                             values=(art["id"], art.get("code",""), art.get("titre",""),
                                     art.get("auteur",""), art.get("categorie",""),
                                     pa, pv, qte),
                             tags=(tag,))
        self.lbl_count.configure(text=f"{len(data)} article(s) affiché(s)")

    def _export_csv(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("Fichier CSV", "*.csv")],
            initialfile=f"stock_librairie_{__import__('datetime').datetime.now().strftime('%Y%m%d')}.csv"
        )
        if not path:
            return
        try:
            with open(path, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f, delimiter=";")
                writer.writerow(["Code","Titre","Auteur","Catégorie","Prix Achat (FCFA)","Prix Vente (FCFA)","Quantité"])
                for art in self._articles:
                    writer.writerow([art.get("code",""), art.get("titre",""), art.get("auteur",""),
                                     art.get("categorie",""), art.get("prix_achat",0),
                                     art.get("prix_vente",0), art.get("quantite",0)])
            messagebox.showinfo("✅ Export réussi", f"Stock exporté avec succès :\n{path}")
            os.startfile(path)
        except Exception as ex:
            messagebox.showerror("Erreur", str(ex))
