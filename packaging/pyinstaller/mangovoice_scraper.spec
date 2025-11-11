# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for the MangoVoice Selenium scraper.

This configuration produces both one-file and one-folder bundles that share the
same analysis stage. Adjust the build command to choose the desired format.
"""

import inspect
from pathlib import Path
from PyInstaller.utils.hooks import collect_submodules

block_cipher = None

SPEC_PATH = Path(inspect.getfile(inspect.currentframe())).resolve()
PROJECT_ROOT = SPEC_PATH.parents[2]

hiddenimports = [
    mod
    for mod in (
        collect_submodules("bs4")
        + collect_submodules("webdriver_manager")
        + collect_submodules("selenium.webdriver")
    )
    if ".tests" not in mod
]

a = Analysis(
    [str(PROJECT_ROOT / "scrape_mangovoice.py")],
    pathex=[str(PROJECT_ROOT)],
    binaries=[],
    datas=[],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="MangoVoiceScraper",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="MangoVoiceScraper",
)

