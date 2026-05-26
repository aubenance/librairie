# -*- coding: utf-8 -*-
"""
LibrairieCI - Theme et composants UI
"""
import customtkinter as ctk
from tkinter import ttk

# ── Couleurs ──────────────────────────────────────────────
VERT        = "#00823C"
VERT_SOMBRE = "#005F2B"
VERT_CLAIR  = "#E8F5E9"
BLANC       = "#FFFFFF"
GRIS_CLAIR  = "#F4F6F9"
GRIS        = "#E0E0E0"
GRIS_TEXTE  = "#607D8B"
NOIR_TEXTE  = "#1A1A2E"
BLEU        = "#1565C0"
ROUGE       = "#C62828"
ORANGE      = "#E65100"

# ── Fonction utilitaire : texte sans caracteres > U+FFFF ─
def _safe(text: str) -> str:
    """Supprime les caracteres incompatibles avec le codec Windows."""
    if text is None:
        return ""
    return "".join(c for c in str(text) if ord(c) <= 0xFFFF)

# ── Formatage FCFA ────────────────────────────────────────
def format_fcfa(n) -> str:
    try:
        return f"{int(n):,} FCFA".replace(",", " ")
    except Exception:
        return f"{n} FCFA"

# ── Theme global ──────────────────────────────────────────
def setup_theme():
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("green")

# ── Composants ───────────────────────────────────────────

def make_button(parent, text: str, command=None,
                color: str = VERT, hover_color: str = VERT_SOMBRE,
                width: int = 160, height: int = 38,
                size: int = 13) -> ctk.CTkButton:
    return ctk.CTkButton(
        parent,
        text=_safe(text),
        command=command,
        fg_color=color,
        hover_color=hover_color,
        width=width, height=height,
        font=ctk.CTkFont(size=size, weight="bold"),
        corner_radius=6)

def make_entry(parent, placeholder: str = "", width: int = 260,
               show: str = "") -> ctk.CTkEntry:
    kw = dict(placeholder_text=_safe(placeholder),
              width=width, height=36,
              font=ctk.CTkFont(size=12), corner_radius=6)
    if show:
        kw["show"] = show
    return ctk.CTkEntry(parent, **kw)

def make_label(parent, text: str, size: int = 12,
               bold: bool = False, color: str = NOIR_TEXTE) -> ctk.CTkLabel:
    return ctk.CTkLabel(
        parent,
        text=_safe(text),
        font=ctk.CTkFont(size=size, weight="bold" if bold else "normal"),
        text_color=color)

def make_treeview(parent, columns: tuple,
                  widths: dict = None) -> tuple:
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Pro.Treeview.Heading",
                    background=VERT, foreground=BLANC,
                    font=("Segoe UI", 10, "bold"), relief="flat")
    style.map("Pro.Treeview.Heading", background=[("active", VERT_SOMBRE)])
    style.configure("Pro.Treeview", rowheight=32,
                    font=("Segoe UI", 11), fieldbackground=BLANC)
    style.map("Pro.Treeview", background=[("selected", VERT_CLAIR)],
              foreground=[("selected", NOIR_TEXTE)])

    frame = parent
    tree = ttk.Treeview(frame, columns=columns,
                        show="headings", style="Pro.Treeview")

    if widths:
        for col in columns:
            w = widths.get(col, 100)
            tree.column(col, width=w, minwidth=w,
                        stretch=(col == columns[-1]))
            tree.heading(col, text=col.replace("_", " ").capitalize())

    tree.tag_configure("alt",     background="#F9FBE7")
    tree.tag_configure("alerte",  background="#FFF8E1", foreground="#E65100")
    tree.tag_configure("rupture", background="#FFEBEE", foreground=ROUGE)

    scr = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scr.set)

    return tree, scr
