"""
LibrairieCI - Gestion des Articles (Admin)
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
from theme import *
from api_client import APIClient, session
import threading


class ArticlesFrame(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(parent, fg_color=GRIS_CLAIR)
        self._articles = []
        self._sel_id   = None
        self._mode     = None   # "add" | "edit"
        self._build()
        self.load_articles()

    # ──────────────────────────────────────
    #  CONSTRUCTION UI
    # ──────────────────────────────────────

    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # En-tête
        hdr = ctk.CTkFrame(self, fg_color=BLANC, corner_radius=0, height=64)
        hdr.grid(row=0, column=0, sticky="ew")
        hdr.grid_propagate(False)
        hdr.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(hdr, text="  Gestion des Articles",
                     font=ctk.CTkFont(size=18, weight="bold"),
                     text_color=NOIR_TEXTE).grid(row=0, column=0, padx=16, pady=14, sticky="w")

        btn_row = ctk.CTkFrame(hdr, fg_color=BLANC)
        btn_row.grid(row=0, column=2, padx=16, pady=10)

        make_button(btn_row, "+ Nouvel Article", self._open_add, width=150).pack(side="left", padx=4)
        make_button(btn_row, "Modifier", self._open_edit,
                    color=BLEU, hover="#0D47A1", width=110).pack(side="left", padx=4)
        make_button(btn_row, "Supprimer", self._delete,
                    color=ROUGE, hover="#B71C1C", width=110).pack(side="left", padx=4)
        make_button(btn_row, "Actualiser", self.load_articles,
                    color="#546E7A", hover="#37474F", width=110).pack(side="left", padx=4)

        ctk.CTkFrame(self, fg_color=GRIS, height=1).grid(row=0, column=0, sticky="ews")

        # Zone principale : liste + formulaire côte à côte
        main = ctk.CTkFrame(self, fg_color=GRIS_CLAIR)
        main.grid(row=1, column=0, sticky="nsew", padx=16, pady=12)
        main.grid_columnconfigure(0, weight=1)
        main.grid_rowconfigure(1, weight=1)

        # Barre de recherche
        search_row = ctk.CTkFrame(main, fg_color=GRIS_CLAIR)
        search_row.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0,8))

        self.entry_search = make_entry(search_row, "Rechercher par titre, code, auteur, categorie...", width=340)
        self.entry_search.pack(side="left", padx=(0,8))
        self.entry_search.bind("<Return>", lambda e: self.load_articles(self.entry_search.get()))
        make_button(search_row, "Rechercher",
                    lambda: self.load_articles(self.entry_search.get()), width=120).pack(side="left")
        make_button(search_row, "Tout afficher", lambda: self._reset_search(),
                    color="#546E7A", hover="#37474F", width=120).pack(side="left", padx=8)

        self.lbl_count = ctk.CTkLabel(search_row, text="", font=ctk.CTkFont(size=12),
                                       text_color=GRIS_TEXTE)
        self.lbl_count.pack(side="left", padx=12)

        # Treeview
        tree_frame = ctk.CTkFrame(main, fg_color=BLANC, corner_radius=10)
        tree_frame.grid(row=1, column=0, sticky="nsew")
        main.grid_columnconfigure(0, weight=1)
        main.grid_rowconfigure(1, weight=1)

        cols = ("id","code","titre","auteur","categorie","prix_vente","quantite")
        self.tree, vsb = make_treeview(tree_frame, cols, {
            "id":10,"code":90,"titre":240,"auteur":150,"categorie":120,
            "prix_vente":130,"quantite":80
        })
        self.tree.heading("id",        text="ID")
        self.tree.heading("code",      text="Code")
        self.tree.heading("titre",     text="Titre / Nom")
        self.tree.heading("auteur",    text="Auteur")
        self.tree.heading("categorie", text="Catégorie")
        self.tree.heading("prix_vente",text="Prix Vente (FCFA)")
        self.tree.heading("quantite",  text="Stock")
        self.tree.column("id", width=0, minwidth=0, stretch=False)
        self.tree.column("prix_vente", anchor="e")
        self.tree.column("quantite",   anchor="center")

        self.tree.pack(side="left", fill="both", expand=True, padx=8, pady=8)
        vsb.pack(side="right", fill="y", pady=8)
        self.tree.bind("<<TreeviewSelect>>", self._on_select)
        self.tree.bind("<Double-1>", lambda e: self._open_edit())

        # ── Panneau formulaire (droite, caché par défaut) ──
        self.form_panel = ctk.CTkFrame(main, fg_color=BLANC, corner_radius=10, width=320)
        self.form_panel.grid(row=1, column=1, sticky="nsew", padx=(10,0))
        self.form_panel.grid_remove()
        self.form_panel.grid_propagate(False)
        main.grid_columnconfigure(1, minsize=0)
        self._build_form()

    def _build_form(self):
        p = self.form_panel
        p.grid_columnconfigure(0, weight=1)

        self.lbl_form_title = ctk.CTkLabel(p, text="Nouvel Article",
                                            font=ctk.CTkFont(size=15, weight="bold"),
                                            text_color=VERT)
        self.lbl_form_title.grid(row=0, column=0, pady=(16,12), padx=18, sticky="w")

        fields = [
            ("Code article *",      "entry_code"),
            ("Titre / Nom *",       "entry_titre"),
            ("Auteur / Editeur",    "entry_auteur"),
            ("Categorie",           "entry_cat"),
            ("Prix d'achat (FCFA)", "entry_pa"),
            ("Prix de vente *",     "entry_pv"),
            ("Quantite en stock *", "entry_qte"),
        ]
        for i, (label, attr) in enumerate(fields):
            ctk.CTkLabel(p, text=label, font=ctk.CTkFont(size=11, weight="bold"),
                         text_color=GRIS_TEXTE).grid(row=i*2+1, column=0,
                                                      sticky="w", padx=18, pady=(4,0))
            e = make_entry(p, "", width=270)
            e.grid(row=i*2+2, column=0, padx=18, pady=(0,4))
            setattr(self, attr, e)

        # Description
        row_base = len(fields)*2 + 1
        ctk.CTkLabel(p, text="Description", font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=GRIS_TEXTE).grid(row=row_base, column=0, sticky="w", padx=18, pady=(4,0))
        self.entry_desc = ctk.CTkTextbox(p, width=270, height=60, font=ctk.CTkFont(size=12))
        self.entry_desc.grid(row=row_base+1, column=0, padx=18, pady=(0,4))

        # Boutons
        btn_row = ctk.CTkFrame(p, fg_color=BLANC)
        btn_row.grid(row=row_base+2, column=0, pady=10, padx=18)
        make_button(btn_row, "Enregistrer", self._save, width=128).pack(side="left", padx=4)
        make_button(btn_row, "Annuler", self._close_form,
                    color="#546E7A", hover="#37474F", width=100).pack(side="left", padx=4)

        self.lbl_form_err = ctk.CTkLabel(p, text="", text_color=ROUGE,
                                          font=ctk.CTkFont(size=11), wraplength=280)
        self.lbl_form_err.grid(row=row_base+3, column=0, padx=18, pady=(0,8))

    # ──────────────────────────────────────
    #  DONNÉES
    # ──────────────────────────────────────

    def load_articles(self, q=""):
        self.tree.delete(*self.tree.get_children())
        def fetch():
            r = APIClient.get_articles(q)
            if r["ok"]:
                self._articles = r["data"]
                self.after(0, self._fill_tree)
            else:
                self.after(0, lambda: messagebox.showerror("Erreur", r["error"]))
        threading.Thread(target=fetch, daemon=True).start()

    def _fill_tree(self):
        self.tree.delete(*self.tree.get_children())
        for art in self._articles:
            qte = art["quantite"]
            tag = "rupture" if qte == 0 else ("alerte" if qte <= 5 else "")
            self.tree.insert("", "end", iid=str(art["id"]),
                             values=(art["id"], art["code"], art["titre"],
                                     art.get("auteur",""), art.get("categorie",""),
                                     f"{int(art['prix_vente']):,}".replace(",", " "),
                                     qte),
                             tags=(tag,))
        self.lbl_count.configure(text=f"{len(self._articles)} article(s)")

    def _reset_search(self):
        self.entry_search.delete(0, "end")
        self.load_articles()

    def _on_select(self, e):
        sel = self.tree.selection()
        self._sel_id = int(sel[0]) if sel else None

    def _get_article_by_id(self, aid):
        return next((a for a in self._articles if a["id"] == aid), None)

    # ──────────────────────────────────────
    #  FORMULAIRE
    # ──────────────────────────────────────

    def _open_add(self):
        self._mode = "add"
        self.lbl_form_title.configure(text="  Nouvel Article", text_color=VERT)
        self._clear_form()
        self._show_form()

    def _open_edit(self):
        if not self._sel_id:
            messagebox.showinfo("Sélection", "Veuillez sélectionner un article.")
            return
        art = self._get_article_by_id(self._sel_id)
        if not art: return
        self._mode = "edit"
        self.lbl_form_title.configure(text="  Modifier l'Article", text_color=BLEU)
        self._clear_form()
        self.entry_code.insert(0, art.get("code",""))
        self.entry_titre.insert(0, art.get("titre",""))
        self.entry_auteur.insert(0, art.get("auteur",""))
        self.entry_cat.insert(0, art.get("categorie",""))
        self.entry_pa.insert(0, str(art.get("prix_achat",0)))
        self.entry_pv.insert(0, str(art.get("prix_vente",0)))
        self.entry_qte.insert(0, str(art.get("quantite",0)))
        self.entry_desc.insert("1.0", art.get("description",""))
        self._show_form()

    def _show_form(self):
        self.form_panel.grid()
        self.form_panel.master.grid_columnconfigure(1, minsize=340)

    def _close_form(self):
        self.form_panel.grid_remove()
        self.form_panel.master.grid_columnconfigure(1, minsize=0)

    def _clear_form(self):
        for attr in ("entry_code","entry_titre","entry_auteur","entry_cat",
                     "entry_pa","entry_pv","entry_qte"):
            getattr(self, attr).delete(0, "end")
        self.entry_desc.delete("1.0", "end")
        self.lbl_form_err.configure(text="")

    def _save(self):
        code  = self.entry_code.get().strip()
        titre = self.entry_titre.get().strip()
        pv    = self.entry_pv.get().strip()
        qte   = self.entry_qte.get().strip()

        if not code or not titre or not pv or not qte:
            self.lbl_form_err.configure(text="Les champs * sont obligatoires.")
            return
        try:
            pv_f  = float(pv.replace(",","."))
            pa_f  = float(self.entry_pa.get().replace(",",".") or "0")
            qte_i = int(qte)
        except ValueError:
            self.lbl_form_err.configure(text="Prix et quantite doivent etre des nombres.")
            return

        payload = {
            "code": code, "titre": titre,
            "auteur":      self.entry_auteur.get().strip(),
            "categorie":   self.entry_cat.get().strip(),
            "prix_achat":  pa_f, "prix_vente": pv_f,
            "quantite":    qte_i,
            "description": self.entry_desc.get("1.0","end").strip()
        }

        self.lbl_form_err.configure(text="Enregistrement...", text_color=VERT)

        def do():
            if self._mode == "add":
                r = APIClient.create_article(payload)
            else:
                r = APIClient.update_article(self._sel_id, payload)
            if r["ok"]:
                self.after(0, lambda: (self._close_form(), self.load_articles(),
                                       messagebox.showinfo("Succes",
                                       "Article enregistre avec succes !")))
            else:
                self.after(0, lambda: self.lbl_form_err.configure(
                    text=r["error"], text_color=ROUGE))
        threading.Thread(target=do, daemon=True).start()

    def _delete(self):
        if not self._sel_id:
            messagebox.showinfo("Selection", "Selectionnez un article.")
            return
        art = self._get_article_by_id(self._sel_id)
        if not messagebox.askyesno("Confirmer",
                f"Supprimer '{art['titre']}' ?\nCette action est irreversible."):
            return
        def do():
            r = APIClient.delete_article(self._sel_id)
            if r["ok"]:
                self.after(0, lambda: (self.load_articles(),
                                       messagebox.showinfo("Succes","Article supprime.")))
            else:
                self.after(0, lambda: messagebox.showerror("Erreur", r["error"]))
        threading.Thread(target=do, daemon=True).start()
        btns = ctk.CTkFrame(
    self.form_panel,
    fg_color="transparent"
)

btns.pack(fill="x", pady=15)

ctk.CTkButton(
    btns,
    text="💾 Enregistrer",
    height=40,
    command=self._save
).pack(side="left", expand=True, fill="x", padx=5)

ctk.CTkButton(
    btns,
    text="❌ Annuler",
    height=40,
    fg_color="red",
    command=self._clear_form
).pack(side="left", expand=True, fill="x", padx=5)
