"""
LibrairieCI - Gestion des Utilisateurs (Admin)
"""

import customtkinter as ctk
from tkinter import messagebox
from theme import *
from api_client import APIClient
import threading


class UsersFrame(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(parent, fg_color=GRIS_CLAIR)
        self._users = []
        self._selected_id = None
        self._mode = None
        self._build()
        self._load()

    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # ── En-tête ──
        header = ctk.CTkFrame(self, fg_color=BLANC, corner_radius=0, height=65)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_propagate(False)
        header.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(header, text="👥  Gestion des Utilisateurs",
                     font=ctk.CTkFont(size=20, weight="bold"),
                     text_color=NOIR_TEXTE).grid(row=0, column=0, padx=20, pady=18, sticky="w")

        btn_frame = ctk.CTkFrame(header, fg_color=BLANC)
        btn_frame.grid(row=0, column=2, padx=16, pady=10)
        make_button(btn_frame, "➕ Nouveau",  self._open_add,  width=110, height=36).pack(side="left", padx=4)
        make_button(btn_frame, "✏ Modifier",  self._open_edit, color=BLEU, hover_color="#0D47A1", width=105, height=36).pack(side="left", padx=4)
        make_button(btn_frame, "🔑 Réinit. MDP", self._reset_mdp, color="#7B1FA2", hover_color="#4A148C", width=130, height=36).pack(side="left", padx=4)
        make_button(btn_frame, "🔄 Actualiser", self._load, color=GRIS_TEXTE, hover_color="#424242", width=115, height=36).pack(side="left", padx=4)

        # ── Split liste + formulaire ──
        split = ctk.CTkFrame(self, fg_color=GRIS_CLAIR)
        split.grid(row=1, column=0, sticky="nsew")
        split.grid_columnconfigure(0, weight=1)
        split.grid_rowconfigure(0, weight=1)

        # Liste
        list_frame = ctk.CTkFrame(split, fg_color=BLANC, corner_radius=0)
        list_frame.grid(row=0, column=0, sticky="nsew", padx=(12,0), pady=12)
        list_frame.grid_columnconfigure(0, weight=1)
        list_frame.grid_rowconfigure(0, weight=1)

        cols = ("id","nom","prenom","username","role","statut")
        widths = {"id":0,"nom":150,"prenom":150,"username":140,"role":100,"statut":90}
        self.tree, scroll = make_treeview(list_frame, cols, widths)
        for c, h in {"id":"ID","nom":"Nom","prenom":"Prénom","username":"Identifiant",
                      "role":"Rôle","statut":"Statut"}.items():
            self.tree.heading(c, text=h)
        self.tree.column("id", width=0, stretch=False)
        self.tree.column("role",   anchor="center")
        self.tree.column("statut", anchor="center")
        self.tree.grid(row=0, column=0, sticky="nsew")
        scroll.grid(row=0, column=1, sticky="ns")
        self.tree.bind("<<TreeviewSelect>>", self._on_select)
        self.tree.bind("<Double-1>", lambda e: self._open_edit())

        self.split = split

        # ── Formulaire (panneau droit) ──
        self.pnl_form = ctk.CTkFrame(split, fg_color=BLANC, corner_radius=0, width=360)
        self.pnl_form.grid(row=0, column=1, sticky="nsew", padx=(8,12), pady=12)
        self.pnl_form.grid_propagate(False)
        self.pnl_form.grid_remove()
        self._build_form()

    def _build_form(self):
        f = self.pnl_form
        f.grid_columnconfigure(0, weight=1)

        self.lbl_form_title = ctk.CTkLabel(f, text="Nouvel Utilisateur",
                                            font=ctk.CTkFont(size=16, weight="bold"), text_color=VERT)
        self.lbl_form_title.grid(row=0, column=0, padx=20, pady=(20,12), sticky="w")

        fields = [("Nom *","nom"),("Prénom *","prenom"),("Identifiant (login) *","username")]
        self._entries = {}
        for i, (lbl, key) in enumerate(fields):
            ctk.CTkLabel(f, text=lbl, font=ctk.CTkFont(size=12, weight="bold"),
                         text_color=GRIS_TEXTE).grid(row=i*2+1, column=0, padx=20, sticky="w", pady=(6,0))
            e = make_entry(f, width=300)
            e.grid(row=i*2+2, column=0, padx=20, sticky="ew")
            self._entries[key] = e

        # Rôle
        ctk.CTkLabel(f, text="Rôle *", font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=GRIS_TEXTE).grid(row=7, column=0, padx=20, sticky="w", pady=(8,0))
        self.cbo_role = ctk.CTkComboBox(f, values=["employe","admin"], width=300, height=36,
                                         font=ctk.CTkFont(size=13), state="readonly")
        self.cbo_role.set("employe")
        self.cbo_role.grid(row=8, column=0, padx=20, sticky="ew")

        # Statut
        self.chk_actif = ctk.CTkCheckBox(f, text="Compte actif",
                                          font=ctk.CTkFont(size=13), text_color=GRIS_TEXTE)
        self.chk_actif.select()
        self.chk_actif.grid(row=9, column=0, padx=20, pady=12, sticky="w")

        # Séparateur
        ctk.CTkFrame(f, fg_color=GRIS, height=1).grid(row=10, column=0, padx=20, sticky="ew", pady=4)

        # Mot de passe
        ctk.CTkLabel(f, text="Mot de passe *", font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=GRIS_TEXTE).grid(row=11, column=0, padx=20, sticky="w", pady=(8,0))
        self.entry_pwd = make_entry(f, show="•", width=300)
        self.entry_pwd.grid(row=12, column=0, padx=20, sticky="ew")

        ctk.CTkLabel(f, text="Confirmer le mot de passe *", font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=GRIS_TEXTE).grid(row=13, column=0, padx=20, sticky="w", pady=(8,0))
        self.entry_pwd2 = make_entry(f, show="•", width=300)
        self.entry_pwd2.grid(row=14, column=0, padx=20, sticky="ew")

        self.lbl_note_pwd = ctk.CTkLabel(f, text="(Laissez vide pour ne pas modifier)",
                                          font=ctk.CTkFont(size=10, slant="italic"), text_color=GRIS_TEXTE)
        self.lbl_note_pwd.grid(row=15, column=0, padx=20, sticky="w")

        # Erreur
        self.lbl_err = ctk.CTkLabel(f, text="", text_color=ROUGE,
                                     font=ctk.CTkFont(size=11), wraplength=310)
        self.lbl_err.grid(row=16, column=0, padx=20, pady=4)

        # Boutons
        btn_row = ctk.CTkFrame(f, fg_color=BLANC)
        btn_row.grid(row=17, column=0, padx=20, pady=8, sticky="ew")
        self.btn_save = make_button(btn_row, "💾  Enregistrer", self._save, width=150, height=38)
        self.btn_save.pack(side="left", padx=(0,8))
        make_button(btn_row, "✖  Annuler", self._close_form,
                    color="#757575", hover_color="#424242", width=110, height=38).pack(side="left")

    # ─────────────────────────────────────
    #  DONNÉES
    # ─────────────────────────────────────

    def _load(self):
        def fetch():
            result = APIClient.get_users()
            if result["ok"]:
                self._users = result["data"]
                self._populate()
            else:
                messagebox.showerror("Erreur", result["error"])
        threading.Thread(target=fetch, daemon=True).start()

    def _populate(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for u in self._users:
            actif = u.get("actif", True)
            statut = "✅ Actif" if actif else "❌ Inactif"
            role_icon = "🔑 admin" if u.get("role") == "admin" else "👷 employé"
            tag = "" if actif else "rupture"
            self.tree.insert("", "end", iid=u["id"],
                             values=(u["id"], u.get("nom",""), u.get("prenom",""),
                                     u.get("username",""), role_icon, statut),
                             tags=(tag,))

    def _on_select(self, _=None):
        sel = self.tree.selection()
        self._selected_id = int(sel[0]) if sel else None

    # ─────────────────────────────────────
    #  FORMULAIRE
    # ─────────────────────────────────────

    def _open_add(self):
        self._mode = "add"
        self._selected_id = None
        self.lbl_form_title.configure(text="➕  Nouvel Utilisateur", text_color=VERT)
        for e in self._entries.values():
            e.delete(0, "end")
        self.entry_pwd.delete(0, "end")
        self.entry_pwd2.delete(0, "end")
        self.cbo_role.set("employe")
        self.chk_actif.select()
        self._entries["username"].configure(state="normal")
        self.lbl_note_pwd.configure(text="")
        self.lbl_err.configure(text="")
        self.pnl_form.grid()

    def _open_edit(self):
        if not self._selected_id:
            messagebox.showinfo("Sélection requise", "Cliquez d'abord sur un utilisateur.")
            return
        u = next((x for x in self._users if x["id"] == self._selected_id), None)
        if not u:
            return
        self._mode = "edit"
        self.lbl_form_title.configure(text="✏  Modifier l'Utilisateur", text_color=BLEU)
        self._entries["nom"].delete(0,"end");    self._entries["nom"].insert(0, u.get("nom",""))
        self._entries["prenom"].delete(0,"end"); self._entries["prenom"].insert(0, u.get("prenom",""))
        self._entries["username"].delete(0,"end"); self._entries["username"].insert(0, u.get("username",""))
        self._entries["username"].configure(state="disabled")
        self.cbo_role.set(u.get("role","employe"))
        if u.get("actif"): self.chk_actif.select()
        else: self.chk_actif.deselect()
        self.entry_pwd.delete(0,"end")
        self.entry_pwd2.delete(0,"end")
        self.lbl_note_pwd.configure(text="(Laissez vide pour ne pas modifier)")
        self.lbl_err.configure(text="")
        self.pnl_form.grid()

    def _close_form(self):
        self._entries["username"].configure(state="normal")
        self.pnl_form.grid_remove()

    def _save(self):
        nom    = self._entries["nom"].get().strip()
        prenom = self._entries["prenom"].get().strip()
        uname  = self._entries["username"].get().strip()
        role   = self.cbo_role.get()
        actif  = self.chk_actif.get() == 1
        pwd    = self.entry_pwd.get()
        pwd2   = self.entry_pwd2.get()

        if not nom or not prenom or not uname:
            self.lbl_err.configure(text="⚠ Nom, Prénom et Identifiant sont obligatoires.")
            return

        if self._mode == "add":
            if not pwd:
                self.lbl_err.configure(text="⚠ Le mot de passe est obligatoire.")
                return
            if pwd != pwd2:
                self.lbl_err.configure(text="⚠ Les deux mots de passe ne correspondent pas.")
                return
            if len(pwd) < 4:
                self.lbl_err.configure(text="⚠ Mot de passe trop court (min 4 caractères).")
                return
        elif pwd and pwd != pwd2:
            self.lbl_err.configure(text="⚠ Les deux mots de passe ne correspondent pas.")
            return

        self.btn_save.configure(text="Enregistrement...", state="disabled")

        def do():
            if self._mode == "add":
                result = APIClient.create_user({"nom":nom,"prenom":prenom,
                                                "username":uname,"password":pwd,"role":role})
            else:
                result = APIClient.update_user(self._selected_id,
                                               {"nom":nom,"prenom":prenom,"role":role,"actif":actif})
                if result["ok"] and pwd:
                    APIClient.reset_password(self._selected_id, pwd)

            self.btn_save.configure(text="💾  Enregistrer", state="normal")
            if result["ok"]:
                self._close_form()
                self._load()
                messagebox.showinfo("✅ Succès",
                                    "Utilisateur créé avec succès !" if self._mode=="add"
                                    else "Utilisateur modifié avec succès !")
            else:
                self.lbl_err.configure(text=f"❌ {result['error']}")

        threading.Thread(target=do, daemon=True).start()

    def _reset_mdp(self):
        if not self._selected_id:
            messagebox.showinfo("Sélection requise", "Sélectionnez un utilisateur.")
            return
        u = next((x for x in self._users if x["id"] == self._selected_id), None)
        nom_complet = f"{u.get('prenom','')} {u.get('nom','')}" if u else ""

        dialog = ctk.CTkInputDialog(text=f"Nouveau mot de passe pour {nom_complet} :",
                                    title="Réinitialiser le mot de passe")
        pwd = dialog.get_input()
        if not pwd or len(pwd) < 4:
            if pwd is not None:
                messagebox.showwarning("Trop court", "Le mot de passe doit contenir au moins 4 caractères.")
            return

        def do():
            result = APIClient.reset_password(self._selected_id, pwd)
            if result["ok"]:
                messagebox.showinfo("✅ Succès", f"Mot de passe de {nom_complet} réinitialisé.")
            else:
                messagebox.showerror("Erreur", result["error"])

        threading.Thread(target=do, daemon=True).start()
