"""
LibrairieCI - Script de correction automatique
Lancer ce script depuis le dossier racine du projet :
    python patch.py
"""
import os, re, sys

print("=" * 55)
print("  LibrairieCI - Patch correctif automatique")
print("=" * 55)

# ── Trouver tous les fichiers .py du projet ──────────────
py_files = []
for root, dirs, files in os.walk("."):
    # Ignorer les dossiers inutiles
    dirs[:] = [d for d in dirs if d not in ('__pycache__', '.git', 'venv', 'env')]
    for f in files:
        if f.endswith(".py"):
            py_files.append(os.path.join(root, f))

if not py_files:
    print("\nErreur : aucun fichier .py trouve.")
    print("Lance ce script depuis le dossier qui contient main.py")
    sys.exit(1)

print(f"\n{len(py_files)} fichiers Python trouves.")

# ── Etape 1 : Supprimer tous les caracteres > U+FFFF ─────
print("\n[1/3] Suppression des emojis incompatibles Windows...")
total = 0
for fpath in py_files:
    try:
        with open(fpath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception:
        continue

    bad = set(c for c in content if ord(c) > 0xFFFF)
    if bad:
        new_content = content
        for c in bad:
            new_content = new_content.replace(c, '')
        # Nettoyer les espaces doubles residuels
        new_content = re.sub(r'  +', ' ', new_content)
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        total += len(bad)
        print(f"   Corrige : {fpath}  ({len(bad)} caractere(s) retires)")

if total == 0:
    print("   Aucun caractere problematique trouve.")
else:
    print(f"   Total : {total} caracteres retires.")

# ── Etape 2 : Corriger main.py ────────────────────────────
print("\n[2/3] Correction de main.py...")
main_path = None
for fpath in py_files:
    if os.path.basename(fpath) == "main.py":
        main_path = fpath
        break

if main_path:
    with open(main_path, 'r', encoding='utf-8') as f:
        content = f.read()

    changed = False

    # Fix A : encodage UTF-8 Tk
    tk_fix = '        # Fix encodage Unicode Windows\n        try:\n            self.tk.call("encoding", "system", "utf-8")\n        except Exception:\n            pass\n'
    if 'self.tk.call("encoding", "system", "utf-8")' not in content:
        # Inserer apres super().__init__()
        content = content.replace(
            '        super().__init__()\n',
            '        super().__init__()\n\n' + tk_fix,
            1)
        changed = True
        print("   Fix A applique : encodage UTF-8 Tk")

    # Fix B : vider le contenu avant chaque navigation
    if 'for w in self._content.winfo_children():' not in content:
        old = '        if self._current_frame:\n            self._current_frame.destroy()'
        new = ('        if self._current_frame:\n'
               '            self._current_frame.destroy()\n'
               '            self._current_frame = None\n'
               '        for w in self._content.winfo_children():\n'
               '            w.destroy()')
        if old in content:
            content = content.replace(old, new, 1)
            changed = True
            print("   Fix B applique : nettoyage contenu navigation")

    if changed:
        with open(main_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"   main.py sauvegarde : {main_path}")
    else:
        print("   main.py deja a jour.")
else:
    print("   ATTENTION : main.py non trouve !")

# ── Etape 3 : Verification finale ─────────────────────────
print("\n[3/3] Verification finale...")
errors = []
for fpath in py_files:
    try:
        with open(fpath, 'r', encoding='utf-8') as f:
            content = f.read()
        bad = [c for c in content if ord(c) > 0xFFFF]
        if bad:
            errors.append((fpath, bad))
    except Exception:
        pass

if errors:
    print("   PROBLEMES RESTANTS :")
    for fpath, bad in errors:
        print(f"   {fpath} : {[hex(ord(c)) for c in bad]}")
else:
    print("   Tous les fichiers sont OK !")

print("\n" + "=" * 55)
print("  Patch termine. Relance l'application.")
print("=" * 55)
