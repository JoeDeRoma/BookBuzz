#!/usr/bin/env python3
"""
Cross-platform app builder for Book Buzz.
Builds macOS .app bundle, Windows .exe, or Linux AppImage.
"""

import os
import sys
import platform
import subprocess
from pathlib import Path


def build_app():
    base_dir = Path(__file__).parent.resolve()
    assets_dir = base_dir / "assets"
    app_py = base_dir / "app.py"
    
    # Ensure assets are extracted
    if not assets_dir.exists():
        print("Extracting assets first...")
        from extract_assets import extract_all_assets
        extract_all_assets()
    
    # Ensure icon exists
    ico_path = base_dir / "bookclub.ico"
    if not ico_path.exists():
        print("Generating icon first...")
        from create_icon import generate_icon
        generate_icon()
    
    # Common PyInstaller settings
    excluded_modules = [
        "matplotlib", "sqlalchemy", "geopandas", "playwright", "streamlit",
        "pyarrow", "scipy", "fastapi", "uvicorn", "torch", "IPython",
        "jupyter", "lxml", "docutils", "duckduckgo_search", "alembic",
        "altair", "pydeck", "primp", "pyogrio", "shapely", "cloudscraper"
    ]
    
    exclude_flags = []
    for mod in excluded_modules:
        exclude_flags.extend(["--exclude-module", mod])
    
    system = platform.system()
    
    if system == "Darwin":  # macOS
        print("🍎 Building macOS app bundle...")
        app_name = "BookBuzz"
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--noconfirm",
            "--onedir",  # Use onedir for macOS .app bundle
            "--windowed",
            f"--name={app_name}",
            f"--icon={str(ico_path)}",
            f"--add-data={str(assets_dir)}:assets",
            f"--add-data={str(ico_path)}:.",
            "--hidden-import=PySide6",
            "--hidden-import=pandas",
            "--hidden-import=numpy",
            "--hidden-import=PIL",
            "--osx-bundle-identifier=com.bookbuzz.app",
            "--codesign-identity=-",  # Ad-hoc signing
        ] + exclude_flags + [str(app_py)]
        
        result = subprocess.run(cmd, cwd=str(base_dir))
        if result.returncode != 0:
            print("Build failed!")
            sys.exit(1)
        
        app_path = base_dir / "dist" / f"{app_name}.app"
        if app_path.exists():
            size_mb = sum(f.stat().st_size for f in app_path.rglob("*")) / (1024 * 1024)
            print("\n" + "=" * 60)
            print(f"✅ SUCCESS! macOS app bundle created:")
            print(f"Path: {app_path}")
            print(f"Size: {size_mb:.1f} MB")
            print(f"To run: open {app_path}")
            print("=" * 60)
        
    elif system == "Windows":  # Windows
        print("🪟 Building Windows executable...")
        app_name = "BookBuzz"
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--noconfirm",
            "--onefile",
            "--windowed",
            f"--name={app_name}",
            f"--icon={str(ico_path)}",
            f"--add-data={str(assets_dir)}{os.pathsep}assets",
            f"--add-data={str(ico_path)}{os.pathsep}.",
            "--hidden-import=PySide6",
            "--hidden-import=pandas",
            "--hidden-import=numpy",
            "--hidden-import=PIL",
        ] + exclude_flags + [str(app_py)]
        
        result = subprocess.run(cmd, cwd=str(base_dir))
        if result.returncode != 0:
            print("Build failed!")
            sys.exit(1)
        
        exe_path = base_dir / "dist" / f"{app_name}.exe"
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print("\n" + "=" * 60)
            print(f"✅ SUCCESS! Windows executable created:")
            print(f"Path: {exe_path}")
            print(f"Size: {size_mb:.1f} MB")
            print("=" * 60)
    
    elif system == "Linux":
        print("🐧 Building Linux AppImage...")
        app_name = "BookBuzz"
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--noconfirm",
            "--onefile",
            "--windowed",
            f"--name={app_name}",
            f"--add-data={str(assets_dir)}:assets",
            f"--add-data={str(ico_path)}:.",
            "--hidden-import=PySide6",
            "--hidden-import=pandas",
            "--hidden-import=numpy",
            "--hidden-import=PIL",
        ] + exclude_flags + [str(app_py)]
        
        result = subprocess.run(cmd, cwd=str(base_dir))
        if result.returncode != 0:
            print("Build failed!")
            sys.exit(1)
        
        app_path = base_dir / "dist" / app_name
        if app_path.exists():
            size_mb = app_path.stat().st_size / (1024 * 1024)
            print("\n" + "=" * 60)
            print(f"✅ SUCCESS! Linux executable created:")
            print(f"Path: {app_path}")
            print(f"Size: {size_mb:.1f} MB")
            print("=" * 60)
    
    else:
        print(f"Unsupported platform: {system}")
        sys.exit(1)


if __name__ == "__main__":
    build_app()
