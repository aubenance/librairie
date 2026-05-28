# -*- mode: python ; coding: utf-8 -*-
# PyInstaller .spec pour LibrairieCI Pro
# Commande : pyinstaller LibrairieCI.spec

import os
from PyInstaller.utils.hooks import collect_all

block_cipher = None

# Collecter customtkinter et toutes ses ressources
ctk_data, ctk_bins, ctk_hiddenimports = collect_all('customtkinter')

a = Analysis(
    ['main.py'],
    pathex=['.', 'frames'],
    binaries=ctk_bins,
    datas=[
        ('config.json', '.'),
        ('frames/*.py', 'frames'),
    ] + ctk_data,
    hiddenimports=[
        'customtkinter',
        'PIL',
        'PIL._tkinter_finder',
        'requests',
        'frames.login_frame',
        'frames.dashboard_frame',
        'frames.articles_frame',
        'frames.vente_frame',
        'frames.stock_frame',
        'frames.users_frame',
        'frames.rapports_frame',
    ] + ctk_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'numpy', 'pandas', 'scipy'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='LibrairieCI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,       # Pas de fenêtre console
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,           # Remplacer par 'icon.ico' si disponible
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='LibrairieCI',
)
