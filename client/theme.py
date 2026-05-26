"""
LibrairieCI - Thème UI professionnel
"""

import customtkinter as ctk
from tkinter import ttk
import tkinter as tk

# ─────────────────────────────────────────
#  COULEURS
# ─────────────────────────────────────────

VERT        = "#00823C"
VERT_SOMBRE = "#005F2B"
VERT_CLAIR  = "#E8F5E9"
ORANGE      = "#F06414"
ROUGE       = "#D32F2F"
BLEU        = "#1565C0"
BLANC       = "#FFFFFF"
GRIS_CLAIR  = "#F5F7FA"
GRIS        = "#E0E0E0"
GRIS_TEXTE  = "#616161"
NOIR_TEXTE  = "#212121"
JAUNE       = "#F9A825"

# ─────────────────────────────────────────
#  CONFIG GLOBALE CTK
# ─────────────────────────────────────────

def setup_theme():
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("green")


# ─────────────────────────────────────────
#  WIDGETS RÉUTILISABLES
# ─────────────────────────────────────────

def make_title(parent, text: str, size: int = 20) -> ctk.CTkLabel:
    return ctk.CTkLabel(parent, text=text, font=ctk.CTkFont(size=size, weight="bold"),
                        text_color=NOIR_TEXTE)

def make_label(parent, text: str, size: int = 13, color: str = GRIS_TEXTE) -> ctk.CTkLabel:
    return ctk.CTkLabel(parent, text=text, font=ctk.CTkFont(size=size), text_color=color)

def make_entry(parent, placeholder: str = "", width: int = 280,
               show: str = "") -> ctk.CTkEntry:
    return ctk.CTkEntry(parent, placeholder_text=placeholder, width=width,
                        show=show, height=38, font=ctk.CTkFont(size=13))

def make_button(parent, text: str, command=None, color: str = VERT,
                hover_color: str = VERT_SOMBRE, width: int = 160,
                height: int = 38, size: int = 13) -> ctk.CTkButton:
    return ctk.CTkButton(parent, text=text, command=command,
                         fg_color=color, hover_color=hover_color,
                         width=width, height=height,
                         font=ctk.CTkFont(size=size, weight="bold"),
                         corner_radius=6)

def make_card(parent, width: int = 200, height: int = 100,
              color: str = BLANC) -> ctk.CTkFrame:
    return ctk.CTkFrame(parent, width=width, height=height,
                        fg_color=color, corner_radius=10,
                        border_width=1, border_color=GRIS)


def format_fcfa(val) -> str:
    try:
        return f"{int(float(val)):,} FCFA".replace(",", " ")
    except Exception:
        return "0 FCFA"


# ─────────────────────────────────────────
#  TREEVIEW STYLISÉ (remplace DataGridView)
# ─────────────────────────────────────────

def make_treeview(parent, columns: list, heights: dict = None) -> ttk.Treeview:
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Pro.Treeview",
                    background=BLANC, foreground=NOIR_TEXTE,
                    fieldbackground=BLANC, rowheight=32,
                    font=("Segoe UI", 11))
    style.configure("Pro.Treeview.Heading",
                    background=VERT, foreground=BLANC,
                    font=("Segoe UI", 11, "bold"),
                    relief="flat", padding=(8, 6))
    style.map("Pro.Treeview",
              background=[("selected", VERT_CLAIR)],
              foreground=[("selected", VERT_SOMBRE)])
    style.map("Pro.Treeview.Heading",
              background=[("active", VERT_SOMBRE)])

    tree = ttk.Treeview(parent, columns=columns, show="headings",
                        style="Pro.Treeview", selectmode="browse")

    # Largeurs de colonnes
    if heights:
        for col, w in heights.items():
            if col in columns:
                tree.column(col, width=w, minwidth=40, anchor="w")

    # Scrollbar
    scrollbar = ttk.Scrollbar(parent, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)

    # Tags couleur
    tree.tag_configure("rupture", background="#FFEBEE", foreground=ROUGE)
    tree.tag_configure("alerte",  background="#FFF8E1", foreground=ORANGE)
    tree.tag_configure("or",      background="#FFF9C4")
    tree.tag_configure("argent",  background="#F5F5F5")
    tree.tag_configure("bronze",  background="#FBE9E7")

    return tree, scrollbar


# ─────────────────────────────────────────
#  BARRE DE RECHERCHE
# ─────────────────────────────────────────

def make_search_bar(parent, on_search, placeholder=" Rechercher...") -> tuple:
    frame = ctk.CTkFrame(parent, fg_color=BLANC, corner_radius=8,
                         border_width=1, border_color=GRIS)
    entry = ctk.CTkEntry(frame, placeholder_text=placeholder,
                         width=280, height=36, border_width=0,
                         fg_color=BLANC, font=ctk.CTkFont(size=13))
    entry.pack(side="left", padx=(8, 0), pady=4)
    entry.bind("<Return>", lambda e: on_search(entry.get()))

    btn = make_button(frame, "Rechercher", lambda: on_search(entry.get()),
                      width=110, height=36)
    btn.pack(side="left", padx=8, pady=4)
    return frame, entry


# ─────────────────────────────────────────
#  DIALOG MODAL SIMPLE
# ─────────────────────────────────────────

class SimpleDialog(ctk.CTkToplevel):
    def __init__(self, parent, title: str, width: int = 420, height: int = 280):
        super().__init__(parent)
        self.title(title)
        self.geometry(f"{width}x{height}")
        self.resizable(False, False)
        self.grab_set()
        self.focus()
        # Centrer
        self.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() - width) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")

    def result_label(self, text: str, color: str = ROUGE):
        lbl = ctk.CTkLabel(self, text=text, text_color=color,
                           font=ctk.CTkFont(size=12), wraplength=380)
        lbl.pack(pady=(4, 0))
        return lbl


# ─────────────────────────────────────────
#  STAT CARD
# ─────────────────────────────────────────

def make_stat_card(parent, icon: str, title: str, value: str,
                   color: str = VERT) -> ctk.CTkFrame:
    card = ctk.CTkFrame(parent, fg_color=BLANC, corner_radius=12,
                        border_width=2, border_color=color, width=195, height=90)
    card.pack_propagate(False)

    top = ctk.CTkFrame(card, fg_color=BLANC)
    top.pack(fill="x", padx=12, pady=(10, 0))

    ctk.CTkLabel(top, text=icon, font=ctk.CTkFont(size=22),
                 text_color=color).pack(side="left")
    ctk.CTkLabel(top, text=title, font=ctk.CTkFont(size=11),
                 text_color=GRIS_TEXTE).pack(side="left", padx=6)

    ctk.CTkLabel(card, text=value, font=ctk.CTkFont(size=18, weight="bold"),
                 text_color=color).pack(pady=(2, 8))
    return card
