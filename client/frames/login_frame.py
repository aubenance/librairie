"""
LibrairieCI - Écran de connexion
"""

import customtkinter as ctk
import tkinter as tk
from theme import *
from api_client import APIClient, session, load_config, save_config
import threading


class LoginFrame(ctk.CTkFrame):

 def __init__(self, parent, on_success):
 super().__init__(parent, fg_color=GRIS_CLAIR)
 self.on_success = on_success
 self._build()

 def _build(self):
 self.grid_columnconfigure(0, weight=1)
 self.grid_columnconfigure(1, weight=1)
 self.grid_rowconfigure(0, weight=1)

 # ── Panneau gauche : bannière verte ──
 left = ctk.CTkFrame(self, fg_color=VERT, corner_radius=0)
 left.grid(row=0, column=0, sticky="nsew")
 left.grid_rowconfigure((0,1,2,3,4), weight=1)

 ctk.CTkLabel(left, text="", font=ctk.CTkFont(size=72)).grid(row=1, pady=(40,10))
 ctk.CTkLabel(left, text="LibrairieCI",
 font=ctk.CTkFont(size=36, weight="bold"),
 text_color=BLANC).grid(row=2)
 ctk.CTkLabel(left, text="Gestion de Librairie\nCôte d'Ivoire",
 font=ctk.CTkFont(size=15), text_color="#C8E6C9",
 justify="center").grid(row=3, pady=(10, 0))
 ctk.CTkLabel(left, text="Version 2.0 • Professionnel",
 font=ctk.CTkFont(size=11), text_color="#81C784").grid(row=4, pady=(0,30))

 # ── Panneau droit : formulaire ──
 right = ctk.CTkFrame(self, fg_color=BLANC, corner_radius=0)
 right.grid(row=0, column=1, sticky="nsew")
 right.grid_rowconfigure((0,1,2,3,4,5,6,7,8), weight=1)
 right.grid_columnconfigure(0, weight=1)

 ctk.CTkLabel(right, text="Connexion",
 font=ctk.CTkFont(size=26, weight="bold"),
 text_color=NOIR_TEXTE).grid(row=1, pady=(40, 4))
 ctk.CTkLabel(right, text="Entrez vos identifiants pour accéder",
 font=ctk.CTkFont(size=13), text_color=GRIS_TEXTE).grid(row=2, pady=(0,20))

 # Serveur URL
 srv_frame = ctk.CTkFrame(right, fg_color=GRIS_CLAIR, corner_radius=8)
 srv_frame.grid(row=3, padx=60, sticky="ew", pady=(0,8))
 ctk.CTkLabel(srv_frame, text=" Serveur :", font=ctk.CTkFont(size=12),
 text_color=GRIS_TEXTE).pack(side="left", padx=10, pady=8)
 self.entry_server = ctk.CTkEntry(srv_frame, width=220, height=30,
 font=ctk.CTkFont(size=12))
 self.entry_server.insert(0, session.config.get("server_url", "http://localhost:8000"))
 self.entry_server.pack(side="left", padx=6, pady=8)
 self.lbl_conn = ctk.CTkLabel(srv_frame, text="", font=ctk.CTkFont(size=11), width=60)
 self.lbl_conn.pack(side="left", padx=4)

 # Identifiant
 ctk.CTkLabel(right, text="Identifiant",
 font=ctk.CTkFont(size=13, weight="bold"),
 text_color=GRIS_TEXTE, anchor="w").grid(row=4, padx=60, sticky="ew")
 self.entry_user = make_entry(right, "ex: admin", width=0)
 self.entry_user.grid(row=5, padx=60, sticky="ew", pady=(2, 8))

 # Mot de passe
 ctk.CTkLabel(right, text="Mot de passe",
 font=ctk.CTkFont(size=13, weight="bold"),
 text_color=GRIS_TEXTE, anchor="w").grid(row=6, padx=60, sticky="ew")
 self.entry_pass = make_entry(right, "••••••••", show="•", width=0)
 self.entry_pass.grid(row=7, padx=60, sticky="ew", pady=(2, 4))
 self.entry_pass.bind("<Return>", lambda e: self._do_login())

 # Message erreur
 self.lbl_err = ctk.CTkLabel(right, text="", text_color=ROUGE,
 font=ctk.CTkFont(size=12), wraplength=320)
 self.lbl_err.grid(row=8, padx=60, pady=4)

 # Bouton connexion
 self.btn_login = make_button(right, " SE CONNECTER ", self._do_login,
 width=0, height=44, size=14)
 self.btn_login.grid(row=9, padx=60, sticky="ew", pady=(4, 6))

 # Tester connexion
 ctk.CTkButton(right, text="Tester la connexion serveur", command=self._test_conn,
 fg_color="transparent", text_color=VERT, hover_color=VERT_CLAIR,
 font=ctk.CTkFont(size=12), height=30).grid(row=10, pady=(0,30))

 def _test_conn(self):
 url = self.entry_server.get().strip()
 cfg = load_config()
 cfg["server_url"] = url
 save_config(cfg)
 session.config = cfg
 self.lbl_conn.configure(text="⏳", text_color=ORANGE)
 self.update_idletasks()

 def check():
 ok = APIClient.test_connection()
 self.lbl_conn.configure(
 text="✅ OK" if ok else "❌ Hors ligne",
 text_color=VERT if ok else ROUGE
 )
 threading.Thread(target=check, daemon=True).start()

 def _do_login(self):
 url = self.entry_server.get().strip()
 user = self.entry_user.get().strip()
 pwd = self.entry_pass.get()

 if not url or not user or not pwd:
 self.lbl_err.configure(text="⚠ Tous les champs sont requis.")
 return

 # Sauvegarder l'URL du serveur
 cfg = load_config()
 cfg["server_url"] = url
 save_config(cfg)
 session.config = cfg

 self.btn_login.configure(text="Connexion...", state="disabled")
 self.lbl_err.configure(text="")
 self.update_idletasks()

 def do():
 result = APIClient.login(user, pwd)
 self.btn_login.configure(text=" SE CONNECTER ", state="normal")
 if result["ok"]:
 self.on_success()
 else:
 self.lbl_err.configure(text=result["error"])

 threading.Thread(target=do, daemon=True).start()
