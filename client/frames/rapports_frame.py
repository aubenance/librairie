"""
LibrairieCI - Rapports & Statistiques (Admin)
"""

import customtkinter as ctk
from tkinter import ttk, messagebox
from theme import *
from api_client import APIClient
import threading
from datetime import datetime, date


class RapportsFrame(ctk.CTkFrame):

 def __init__(self, parent):
 super().__init__(parent, fg_color=GRIS_CLAIR)
 self._ventes = []
 self._build()
 self._load_ventes()
 self._load_top()

 def _build(self):
 self.grid_columnconfigure(0, weight=1)
 self.grid_rowconfigure(2, weight=1)

 # ── En-tête ──
 header = ctk.CTkFrame(self, fg_color=BLANC, corner_radius=0, height=65)
 header.grid(row=0, column=0, sticky="ew")
 header.grid_propagate(False)
 header.grid_columnconfigure(1, weight=1)

 ctk.CTkLabel(header, text=" Rapports & Statistiques",
 font=ctk.CTkFont(size=20, weight="bold"),
 text_color=NOIR_TEXTE).grid(row=0, column=0, padx=20, pady=18, sticky="w")

 # ── Cartes résumé ──
 cards_frame = ctk.CTkFrame(self, fg_color=GRIS_CLAIR, height=100)
 cards_frame.grid(row=1, column=0, sticky="ew", padx=16, pady=(12,0))
 self._lbl_stats = {}
 defs = [
 ("nb_ventes", "", "Ventes affichées", "0", VERT),
 ("ca_total", "", "Chiffre d'affaires","0 FCFA", ORANGE),
 ("panier_moy","", "Panier moyen", "0 FCFA", BLEU),
 ]
 for i, (key, icon, title, val, color) in enumerate(defs):
 card = ctk.CTkFrame(cards_frame, fg_color=BLANC, corner_radius=10,
 border_width=2, border_color=color, width=230, height=78)
 card.grid(row=0, column=i, padx=8, pady=6, sticky="nsew")
 card.grid_propagate(False)
 top = ctk.CTkFrame(card, fg_color=BLANC)
 top.pack(fill="x", padx=10, pady=(8,0))
 ctk.CTkLabel(top, text=icon, font=ctk.CTkFont(size=18), text_color=color).pack(side="left")
 ctk.CTkLabel(top, text=title, font=ctk.CTkFont(size=10), text_color=GRIS_TEXTE).pack(side="left", padx=6)
 lbl = ctk.CTkLabel(card, text=val, font=ctk.CTkFont(size=17, weight="bold"), text_color=color)
 lbl.pack()
 self._lbl_stats[key] = lbl

 # ── Onglets ──
 self.tabs = ctk.CTkTabview(self, fg_color=BLANC, corner_radius=10)
 self.tabs.grid(row=2, column=0, sticky="nsew", padx=12, pady=12)
 self.tabs.add(" Historique des Ventes")
 self.tabs.add(" Top Articles")

 # ── Onglet 1 : Historique ──
 tab1 = self.tabs.tab(" Historique des Ventes")
 tab1.grid_columnconfigure(0, weight=1)
 tab1.grid_rowconfigure(1, weight=1)

 # Filtres de période
 filt = ctk.CTkFrame(tab1, fg_color=GRIS_CLAIR, corner_radius=8)
 filt.grid(row=0, column=0, sticky="ew", pady=(6,8))

 ctk.CTkLabel(filt, text="Période :", font=ctk.CTkFont(size=12, weight="bold"),
 text_color=GRIS_TEXTE).pack(side="left", padx=12, pady=8)

 today = date.today()
 ctk.CTkLabel(filt, text="Du :", font=ctk.CTkFont(size=12)).pack(side="left", padx=4)
 self.entry_debut = ctk.CTkEntry(filt, width=110, height=32, font=ctk.CTkFont(size=12))
 self.entry_debut.insert(0, f"{today.year}-{today.month:02d}-01")
 self.entry_debut.pack(side="left", padx=4, pady=8)

 ctk.CTkLabel(filt, text="Au :", font=ctk.CTkFont(size=12)).pack(side="left", padx=4)
 self.entry_fin = ctk.CTkEntry(filt, width=110, height=32, font=ctk.CTkFont(size=12))
 self.entry_fin.insert(0, today.strftime("%Y-%m-%d"))
 self.entry_fin.pack(side="left", padx=4, pady=8)

 make_button(filt, " Filtrer", self._load_ventes, width=90, height=32).pack(side="left", padx=8)

 for label, d_str, f_str in [
 ("Aujourd'hui", today.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d")),
 ("Ce mois", f"{today.year}-{today.month:02d}-01", today.strftime("%Y-%m-%d")),
 ("Tout", "2020-01-01", today.strftime("%Y-%m-%d")),
 ]:
 make_button(filt, label,
 lambda d=d_str, f=f_str: self._quick_filter(d, f),
 color=GRIS_TEXTE, hover_color="#424242", width=90, height=32
 ).pack(side="left", padx=3, pady=8)

 # Split historique + détail
 split = ctk.CTkFrame(tab1, fg_color=BLANC)
 split.grid(row=1, column=0, sticky="nsew")
 split.grid_columnconfigure(0, weight=2)
 split.grid_columnconfigure(1, weight=1)
 split.grid_rowconfigure(0, weight=1)

 # Grille ventes
 v_frame = ctk.CTkFrame(split, fg_color=BLANC)
 v_frame.grid(row=0, column=0, sticky="nsew", padx=(6,4), pady=6)
 v_frame.grid_columnconfigure(0, weight=1)
 v_frame.grid_rowconfigure(0, weight=1)

 v_cols = ("id","numero","date_vente","employe","total")
 v_widths = {"id":0,"numero":140,"date_vente":140,"employe":150,"total":110}
 self.tree_ventes, scr_v = make_treeview(v_frame, v_cols, v_widths)
 for c, h in {"id":"ID","numero":"N° Vente","date_vente":"Date/Heure",
 "employe":"Vendeur","total":"Total (FCFA)"}.items():
 self.tree_ventes.heading(c, text=h)
 self.tree_ventes.column("id", width=0, stretch=False)
 self.tree_ventes.column("total", anchor="e")
 self.tree_ventes.grid(row=0, column=0, sticky="nsew")
 scr_v.grid(row=0, column=1, sticky="ns")
 self.tree_ventes.bind("<<TreeviewSelect>>", self._on_vente_select)

 # Détail vente
 d_frame = ctk.CTkFrame(split, fg_color=GRIS_CLAIR, corner_radius=8)
 d_frame.grid(row=0, column=1, sticky="nsew", padx=(4,6), pady=6)
 d_frame.grid_columnconfigure(0, weight=1)
 d_frame.grid_rowconfigure(1, weight=1)

 ctk.CTkLabel(d_frame, text="Détail de la vente sélectionnée",
 font=ctk.CTkFont(size=12, weight="bold"), text_color=BLEU
 ).grid(row=0, column=0, padx=10, pady=(8,4), sticky="w")

 d_cols = ("titre","code","qte","prix","sous_total")
 d_widths = {"titre":140,"code":60,"qte":40,"prix":80,"sous_total":90}
 style = ttk.Style()
 style.configure("Detail.Treeview.Heading", background=BLEU, foreground=BLANC,
 font=("Segoe UI",10,"bold"))
 self.tree_detail, scr_d = make_treeview(d_frame, d_cols, d_widths)
 self.tree_detail.configure(style="Pro.Treeview")
 for c, h in {"titre":"Article","code":"Code","qte":"Qté",
 "prix":"Prix unit.","sous_total":"Sous-total"}.items():
 self.tree_detail.heading(c, text=h)
 self.tree_detail.column("qte", anchor="center")
 self.tree_detail.column("prix", anchor="e")
 self.tree_detail.column("sous_total", anchor="e")
 self.tree_detail.grid(row=1, column=0, sticky="nsew", padx=4, pady=(0,6))
 scr_d.grid(row=1, column=1, sticky="ns", pady=(0,6))

 # ── Onglet 2 : Top Articles ──
 tab2 = self.tabs.tab(" Top Articles")
 tab2.grid_columnconfigure(0, weight=1)
 tab2.grid_rowconfigure(1, weight=1)

 ctk.CTkLabel(tab2, text=" Les 10 articles les plus vendus (tous temps)",
 font=ctk.CTkFont(size=13, weight="bold"), text_color=ORANGE
 ).grid(row=0, column=0, padx=10, pady=8, sticky="w")

 top_frame = ctk.CTkFrame(tab2, fg_color=BLANC)
 top_frame.grid(row=1, column=0, sticky="nsew", padx=6, pady=(0,6))
 top_frame.grid_columnconfigure(0, weight=1)
 top_frame.grid_rowconfigure(0, weight=1)

 t_style = ttk.Style()
 t_style.configure("Top.Treeview.Heading", background=ORANGE, foreground=BLANC,
 font=("Segoe UI",10,"bold"))
 t_cols = ("rang","titre","total_vendu","recette")
 t_widths = {"rang":50,"titre":350,"total_vendu":130,"recette":160}
 self.tree_top, scr_top = make_treeview(top_frame, t_cols, t_widths)
 self.tree_top.configure(style="Pro.Treeview")
 for c, h in {"rang":"","titre":"Titre / Article","total_vendu":"Qté vendue",
 "recette":"Recette (FCFA)"}.items():
 self.tree_top.heading(c, text=h)
 self.tree_top.column("rang", anchor="center", width=50)
 self.tree_top.column("total_vendu", anchor="center")
 self.tree_top.column("recette", anchor="e")
 self.tree_top.grid(row=0, column=0, sticky="nsew")
 scr_top.grid(row=0, column=1, sticky="ns")

 # ─────────────────────────────────────
 # DONNÉES
 # ─────────────────────────────────────

 def _quick_filter(self, debut, fin):
 self.entry_debut.delete(0,"end"); self.entry_debut.insert(0, debut)
 self.entry_fin.delete(0,"end"); self.entry_fin.insert(0, fin)
 self._load_ventes()

 def _load_ventes(self):
 debut = self.entry_debut.get().strip()
 fin = self.entry_fin.get().strip()

 def fetch():
 result = APIClient.get_ventes(debut or None, fin or None)
 if result["ok"]:
 self._ventes = result["data"]
 self._populate_ventes()
 self._update_stats()
 else:
 messagebox.showerror("Erreur", result["error"])

 threading.Thread(target=fetch, daemon=True).start()

 def _populate_ventes(self):
 for row in self.tree_ventes.get_children():
 self.tree_ventes.delete(row)
 for v in self._ventes:
 total = f"{int(v.get('total',0)):,}".replace(",", " ")
 self.tree_ventes.insert("", "end", iid=v["id"],
 values=(v["id"], v.get("numero",""),
 v.get("date_vente",""),
 v.get("employe",""), total))

 def _update_stats(self):
 nb = len(self._ventes)
 ca = sum(v.get("total",0) for v in self._ventes)
 moy = ca / nb if nb else 0
 self._lbl_stats["nb_ventes"].configure(text=str(nb))
 self._lbl_stats["ca_total"].configure(text=format_fcfa(ca))
 self._lbl_stats["panier_moy"].configure(text=format_fcfa(moy))

 def _on_vente_select(self, _=None):
 sel = self.tree_ventes.selection()
 if not sel:
 return
 vente_id = int(sel[0])

 def fetch():
 result = APIClient.get_vente_details(vente_id)
 if result["ok"]:
 for row in self.tree_detail.get_children():
 self.tree_detail.delete(row)
 for d in result["data"]:
 self.tree_detail.insert("", "end",
 values=(d.get("titre","")[:22],
 d.get("code",""),
 d.get("quantite",""),
 f"{int(d.get('prix_unitaire',0)):,}".replace(","," "),
 f"{int(d.get('sous_total',0)):,}".replace(","," ")))

 threading.Thread(target=fetch, daemon=True).start()

 def _load_top(self):
 def fetch():
 result = APIClient.get_top_articles()
 if result["ok"]:
 medailles = ["","",""]
 tags_map = ["or","argent","bronze"]
 for row in self.tree_top.get_children():
 self.tree_top.delete(row)
 for i, art in enumerate(result["data"]):
 rang = medailles[i] if i < 3 else f"#{i+1}"
 tag = tags_map[i] if i < 3 else ""
 self.tree_top.insert("", "end",
 values=(rang, art.get("titre",""),
 art.get("total_vendu",""),
 f"{int(art.get('recette',0)):,}".replace(","," ")),
 tags=(tag,))

 threading.Thread(target=fetch, daemon=True).start()
