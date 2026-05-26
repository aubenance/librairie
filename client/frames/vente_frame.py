"""
LibrairieCI - Nouvelle Vente
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
from theme import *
from api_client import APIClient, session
import threading
from datetime import datetime
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from print_service import imprimer_recu


class VenteFrame(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(parent, fg_color=GRIS_CLAIR)
        self._articles = []
        self._panier   = []
        self._build()
        self._load_articles()

    # ─────────────────────────────────────
    #  BUILD
    # ─────────────────────────────────────

    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        self.grid_rowconfigure(1, weight=1)

        # ── En-tête ──
        header = ctk.CTkFrame(self, fg_color=BLANC, corner_radius=0, height=65)
        header.grid(row=0, column=0, columnspan=2, sticky="ew")
        header.grid_propagate(False)
        header.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(header, text=" Nouvelle Vente",
                     font=ctk.CTkFont(size=20, weight="bold"),
                     text_color=NOIR_TEXTE).grid(row=0, column=0, padx=20, pady=18, sticky="w")

        self.lbl_date = ctk.CTkLabel(
            header,
            text=datetime.now().strftime(" %A %d/%m/%Y  •  %H:%M"),
            font=ctk.CTkFont(size=12), text_color=GRIS_TEXTE)
        self.lbl_date.grid(row=0, column=1, padx=20, sticky="e")

        make_button(header, " Actualiser stock", self._load_articles,
                    color=GRIS_TEXTE, hover_color="#424242",
                    width=150, height=34).grid(row=0, column=2, padx=16)

        # ── GAUCHE : Catalogue ──
        left = ctk.CTkFrame(self, fg_color=BLANC, corner_radius=10)
        left.grid(row=1, column=0, sticky="nsew", padx=(12, 6), pady=12)
        left.grid_columnconfigure(0, weight=1)
        # ROW WEIGHTS : uniquement row=2 (treeview) s'agrandit
        left.grid_rowconfigure(2, weight=1)

        # Titre + compteur
        top_bar = ctk.CTkFrame(left, fg_color=BLANC)
        top_bar.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 4))
        ctk.CTkLabel(top_bar, text=" Catalogue",
                     font=ctk.CTkFont(size=15, weight="bold"),
                     text_color=VERT).pack(side="left")
        self.lbl_cat_count = ctk.CTkLabel(top_bar, text="",
                                           font=ctk.CTkFont(size=11),
                                           text_color=GRIS_TEXTE)
        self.lbl_cat_count.pack(side="right")

        # Recherche (row=1, taille fixe)
        search_row = ctk.CTkFrame(left, fg_color=GRIS_CLAIR, corner_radius=8)
        search_row.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 6))
        self.entry_search = ctk.CTkEntry(
            search_row,
            placeholder_text=" Titre, code, auteur...",
            height=34, font=ctk.CTkFont(size=12))
        self.entry_search.pack(side="left", fill="x", expand=True, padx=8, pady=6)
        self.entry_search.bind("<Return>",
                               lambda e: self._filter(self.entry_search.get()))
        make_button(search_row, "Chercher",
                    lambda: self._filter(self.entry_search.get()),
                    width=90, height=34).pack(side="left", padx=(0, 6), pady=6)

        # Treeview catalogue (row=2, s'agrandit)
        cat_frame = ctk.CTkFrame(left, fg_color=BLANC)
        cat_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0, 4))
        cat_frame.grid_columnconfigure(0, weight=1)
        cat_frame.grid_rowconfigure(0, weight=1)

        cols   = ("id", "code", "titre", "auteur", "prix_vente", "quantite")
        widths = {"id": 0, "code": 75, "titre": 220,
                  "auteur": 130, "prix_vente": 120, "quantite": 70}
        self.tree_cat, scr_cat = make_treeview(cat_frame, cols, widths)
        heads = {"id": "ID", "code": "Code", "titre": "Titre",
                 "auteur": "Auteur", "prix_vente": "Prix (FCFA)", "quantite": "Stock"}
        for c, h in heads.items():
            self.tree_cat.heading(c, text=h)
        self.tree_cat.column("id", width=0, stretch=False)
        self.tree_cat.column("prix_vente", anchor="e")
        self.tree_cat.column("quantite", anchor="center")
        self.tree_cat.grid(row=0, column=0, sticky="nsew")
        scr_cat.grid(row=0, column=1, sticky="ns")
        self.tree_cat.bind("<Double-1>", lambda e: self._add_to_cart())

        # Barre d'ajout rapide (row=3, taille fixe)
        add_bar = ctk.CTkFrame(left, fg_color=VERT_CLAIR, corner_radius=8)
        add_bar.grid(row=3, column=0, sticky="ew", padx=10, pady=(0, 10))

        ctk.CTkLabel(add_bar, text="Quantité :",
                     font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=VERT_SOMBRE).pack(side="left", padx=12, pady=8)
        self.entry_qty = ctk.CTkEntry(add_bar, width=70, height=34,
                                       font=ctk.CTkFont(size=13, weight="bold"))
        self.entry_qty.insert(0, "1")
        self.entry_qty.pack(side="left", pady=8)
        self.entry_qty.bind("<Return>", lambda e: self._add_to_cart())

        make_button(add_bar, "➕  Ajouter au panier", self._add_to_cart,
                    width=190, height=34).pack(side="left", padx=12, pady=8)

        ctk.CTkLabel(add_bar,
                     text="Double-clic pour ajouter",
                     font=ctk.CTkFont(size=11, slant="italic"),
                     text_color=GRIS_TEXTE).pack(side="right", padx=12)

        # ── DROITE : Panier ──
        right = ctk.CTkFrame(self, fg_color=BLANC, corner_radius=10, width=400)
        right.grid(row=1, column=1, sticky="nsew", padx=(0, 12), pady=12)
        right.grid_propagate(False)
        right.grid_columnconfigure(0, weight=1)
        right.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(right, text=" Panier",
                     font=ctk.CTkFont(size=15, weight="bold"),
                     text_color=ORANGE).grid(row=0, column=0,
                                              padx=16, pady=(14, 6), sticky="w")

        # Treeview panier
        pan_frame = ctk.CTkFrame(right, fg_color=BLANC)
        pan_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 4))
        pan_frame.grid_columnconfigure(0, weight=1)
        pan_frame.grid_rowconfigure(0, weight=1)

        p_cols   = ("titre", "prix", "qte", "sous_total")
        p_widths = {"titre": 140, "prix": 80, "qte": 40, "sous_total": 90}
        self.tree_pan, scr_pan = make_treeview(pan_frame, p_cols, p_widths)

        # Style orange pour le panier
        style = ttk.Style()
        style.configure("Panier.Treeview.Heading",
                        background=ORANGE, foreground=BLANC,
                        font=("Segoe UI", 10, "bold"))
        style.configure("Panier.Treeview", rowheight=30, font=("Segoe UI", 10))
        self.tree_pan.configure(style="Panier.Treeview")

        heads_p = {"titre": "Article", "prix": "Prix",
                   "qte": "Qté", "sous_total": "Sous-total"}
        for c, h in heads_p.items():
            self.tree_pan.heading(c, text=h)
        self.tree_pan.column("prix", anchor="e")
        self.tree_pan.column("qte", anchor="center")
        self.tree_pan.column("sous_total", anchor="e")
        self.tree_pan.grid(row=0, column=0, sticky="nsew")
        scr_pan.grid(row=0, column=1, sticky="ns")

        # Boutons panier
        btn_pan = ctk.CTkFrame(right, fg_color=BLANC)
        btn_pan.grid(row=2, column=0, padx=10, pady=4, sticky="ew")
        make_button(btn_pan, "Retirer", self._remove_line,
                    color=ROUGE, hover_color="#B71C1C",
                    width=110, height=32).pack(side="left", padx=4)
        make_button(btn_pan, " Vider", self._clear_cart,
                    color="#757575", hover_color="#424242",
                    width=90, height=32).pack(side="left")

        # Carte total
        total_card = ctk.CTkFrame(right, fg_color=VERT_CLAIR, corner_radius=10)
        total_card.grid(row=3, column=0, padx=10, pady=8, sticky="ew")
        ctk.CTkLabel(total_card, text="TOTAL À PAYER",
                     font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=VERT_SOMBRE).pack(pady=(12, 0))
        self.lbl_total = ctk.CTkLabel(total_card, text="0 FCFA",
                                       font=ctk.CTkFont(size=26, weight="bold"),
                                       text_color=VERT)
        self.lbl_total.pack(pady=(2, 12))

        # Bouton valider
        self.btn_valider = make_button(
            right, "✔  VALIDER LA VENTE",
            self._valider_vente, width=360, height=50, size=15)
        self.btn_valider.grid(row=4, column=0, padx=10, pady=(4, 14))

    # ─────────────────────────────────────
    #  CATALOGUE
    # ─────────────────────────────────────

    def _load_articles(self):
        self.lbl_cat_count.configure(text="⏳ Chargement...")

        def fetch():
            result = APIClient.get_articles()
            if result["ok"]:
                self._articles = result["data"]
                # Retour sur le thread principal (thread-safe)
                self.after(0, lambda: self._filter())
            else:
                self.after(0, lambda: self.lbl_cat_count.configure(
                    text="❌ Erreur réseau"))

        threading.Thread(target=fetch, daemon=True).start()

    def _filter(self, q=""):
        filtered = [
            a for a in self._articles
            if not q
            or q.lower() in a.get("titre", "").lower()
            or q.lower() in a.get("code", "").lower()
            or q.lower() in a.get("auteur", "").lower()
        ]
        for row in self.tree_cat.get_children():
            self.tree_cat.delete(row)
        for art in filtered:
            qte  = art.get("quantite", 0)
            prix = f"{int(art.get('prix_vente', 0)):,}".replace(",", " ")
            tag  = "rupture" if qte == 0 else ("alerte" if qte <= 5 else "")
            self.tree_cat.insert("", "end", iid=str(art["id"]),
                                 values=(art["id"], art.get("code", ""),
                                         art.get("titre", ""),
                                         art.get("auteur", ""),
                                         prix, qte),
                                 tags=(tag,))
        self.lbl_cat_count.configure(text=f"{len(filtered)} article(s)")

    # ─────────────────────────────────────
    #  PANIER
    # ─────────────────────────────────────

    def _get_selected_article(self):
        sel = self.tree_cat.selection()
        if not sel:
            return None
        art_id = int(sel[0])
        return next((a for a in self._articles if a["id"] == art_id), None)

    def _add_to_cart(self):
        art = self._get_selected_article()
        if not art:
            messagebox.showinfo("Sélection",
                                "Sélectionnez d'abord un article dans le catalogue.")
            return
        stock = art.get("quantite", 0)
        if stock == 0:
            messagebox.showwarning("Rupture de stock",
                                   f"« {art['titre']} » est en rupture de stock.")
            return
        try:
            qte = int(self.entry_qty.get())
            if qte <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Quantité invalide",
                                   "Entrez un nombre entier positif.")
            return

        existing   = next((l for l in self._panier if l["id"] == art["id"]), None)
        qte_totale = qte + (existing["qte"] if existing else 0)
        if qte_totale > stock:
            messagebox.showwarning(
                "Stock insuffisant",
                f"Stock disponible : {stock} exemplaire(s).\n"
                f"Déjà dans le panier : {existing['qte'] if existing else 0}")
            return

        if existing:
            existing["qte"] += qte
        else:
            self._panier.append({
                "id":    art["id"],
                "code":  art.get("code", ""),
                "titre": art.get("titre", ""),
                "prix":  art.get("prix_vente", 0),
                "qte":   qte
            })
        self._refresh_cart()
        self.entry_qty.delete(0, "end")
        self.entry_qty.insert(0, "1")

    def _remove_line(self):
        sel = self.tree_pan.selection()
        if not sel:
            return
        idx = int(sel[0])
        if 0 <= idx < len(self._panier):
            self._panier.pop(idx)
            self._refresh_cart()

    def _clear_cart(self):
        if self._panier and messagebox.askyesno("Vider le panier",
                                                "Vider tout le panier ?"):
            self._panier.clear()
            self._refresh_cart()

    def _refresh_cart(self):
        for row in self.tree_pan.get_children():
            self.tree_pan.delete(row)
        total = 0
        for i, lg in enumerate(self._panier):
            sous = lg["prix"] * lg["qte"]
            total += sous
            self.tree_pan.insert(
                "", "end", iid=str(i),
                values=(lg["titre"][:22],
                        f"{int(lg['prix']):,}".replace(",", " "),
                        lg["qte"],
                        f"{int(sous):,}".replace(",", " ")))
        self.lbl_total.configure(text=format_fcfa(total))

    # ─────────────────────────────────────
    #  VALIDATION VENTE
    # ─────────────────────────────────────

    def _valider_vente(self):
        if not self._panier:
            messagebox.showinfo("Panier vide",
                                "Ajoutez des articles avant de valider.")
            return

        total  = sum(lg["prix"] * lg["qte"] for lg in self._panier)
        recap  = "\n".join([
            f" • {lg['titre'][:28]}  x{lg['qte']}  →  {format_fcfa(lg['prix']*lg['qte'])}"
            for lg in self._panier])

        if not messagebox.askyesno(
                "Confirmer la vente",
                f"Résumé :\n\n{recap}\n\n{'─'*40}\n"
                f"TOTAL : {format_fcfa(total)}\n\nConfirmer ?"):
            return

        self.btn_valider.configure(text="⏳ Enregistrement...", state="disabled")

        lignes = [{"id_article": lg["id"],
                   "quantite": lg["qte"],
                   "prix_unitaire": lg["prix"]}
                  for lg in self._panier]

        panier_snapshot = list(self._panier)   # copie pour le reçu

        def do():
            result = APIClient.create_vente(lignes, total)
            self.after(0, lambda: self.btn_valider.configure(
                text="✔  VALIDER LA VENTE", state="normal"))

            if result["ok"]:
                numero = result["data"].get("numero", "N/A")
                self.after(0, lambda: self._apres_vente(
                    numero, total, panier_snapshot))
            else:
                self.after(0, lambda: messagebox.showerror(
                    "Erreur", result["error"]))

        threading.Thread(target=do, daemon=True).start()

    def _apres_vente(self, numero: str, total: float, panier: list):
        """Appelé après une vente réussie : reçu + impression."""
        self._panier.clear()
        self._refresh_cart()
        self._load_articles()

        # Fenêtre reçu + bouton imprimer
        self._afficher_recu(numero, total, panier)

    def _afficher_recu(self, numero: str, total: float, panier: list):
        """Affiche une fenêtre de reçu avec bouton d'impression."""
        win = ctk.CTkToplevel(self)
        win.title("✅ Vente enregistrée – Reçu")
        win.geometry("480x540")
        win.resizable(False, False)
        win.grab_set()
        win.focus()

        # Centrer la fenêtre
        win.update_idletasks()
        root = self.winfo_toplevel()
        x = root.winfo_rootx() + (root.winfo_width()  - 480) // 2
        y = root.winfo_rooty() + (root.winfo_height() - 540) // 2
        win.geometry(f"480x540+{x}+{y}")

        # En-tête vert
        hdr = ctk.CTkFrame(win, fg_color=VERT, height=70, corner_radius=0)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        ctk.CTkLabel(hdr, text="✅  Vente enregistrée avec succès !",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=BLANC).pack(expand=True)

        # Corps du reçu
        body = ctk.CTkScrollableFrame(win, fg_color="#FAFAFA", corner_radius=0)
        body.pack(fill="both", expand=True, padx=0, pady=0)

        now = datetime.now().strftime("%d/%m/%Y à %H:%M")

        def row_info(label, val, bold=False):
            f = ctk.CTkFrame(body, fg_color="#FAFAFA")
            f.pack(fill="x", padx=20, pady=1)
            ctk.CTkLabel(f, text=label, font=ctk.CTkFont(size=12),
                         text_color=GRIS_TEXTE, width=130, anchor="w").pack(side="left")
            ctk.CTkLabel(f, text=val,
                         font=ctk.CTkFont(size=12,
                                          weight="bold" if bold else "normal"),
                         text_color=NOIR_TEXTE, anchor="w").pack(side="left")

        ctk.CTkLabel(body, text="─" * 52, text_color=GRIS,
                     font=ctk.CTkFont(size=10)).pack(pady=(12, 4))
        row_info("N° Vente :", numero, bold=True)
        row_info("Date :", now)
        row_info("Vendeur :", session.nom_complet)
        ctk.CTkLabel(body, text="─" * 52, text_color=GRIS,
                     font=ctk.CTkFont(size=10)).pack(pady=6)

        # Lignes articles
        for lg in panier:
            sous = lg["prix"] * lg["qte"]
            f = ctk.CTkFrame(body, fg_color=BLANC, corner_radius=6)
            f.pack(fill="x", padx=20, pady=2)
            ctk.CTkLabel(f, text=f" {lg['titre'][:30]}",
                         font=ctk.CTkFont(size=12),
                         text_color=NOIR_TEXTE, anchor="w").pack(side="left",
                                                                  fill="x", expand=True)
            ctk.CTkLabel(f, text=f"x{lg['qte']}",
                         font=ctk.CTkFont(size=12),
                         text_color=GRIS_TEXTE, width=30).pack(side="left")
            ctk.CTkLabel(f, text=format_fcfa(sous),
                         font=ctk.CTkFont(size=12, weight="bold"),
                         text_color=VERT, width=110, anchor="e").pack(side="right",
                                                                       padx=8)

        ctk.CTkLabel(body, text="─" * 52, text_color=GRIS,
                     font=ctk.CTkFont(size=10)).pack(pady=6)

        # Total
        tf = ctk.CTkFrame(body, fg_color=VERT_CLAIR, corner_radius=8)
        tf.pack(fill="x", padx=20, pady=(0, 12))
        ctk.CTkLabel(tf, text="TOTAL PAYÉ",
                     font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=VERT_SOMBRE).pack(side="left", padx=16, pady=10)
        ctk.CTkLabel(tf, text=format_fcfa(total),
                     font=ctk.CTkFont(size=18, weight="bold"),
                     text_color=VERT).pack(side="right", padx=16)

        # Boutons
        btn_frame = ctk.CTkFrame(win, fg_color=BLANC, height=64, corner_radius=0)
        btn_frame.pack(fill="x", side="bottom")
        btn_frame.pack_propagate(False)

        def do_print():
            items = [{"titre": lg["titre"], "prix": lg["prix"], "qte": lg["qte"]}
                     for lg in panier]
            imprimer_recu(numero, session.nom_complet, items, total)

        make_button(btn_frame, " Imprimer le reçu", do_print,
                    color=BLEU, hover_color="#0D47A1",
                    width=200, height=40).pack(side="left", padx=16, pady=12)
        make_button(btn_frame, "Fermer", win.destroy,
                    color=GRIS_TEXTE, hover_color="#424242",
                    width=120, height=40).pack(side="right", padx=16, pady=12)
