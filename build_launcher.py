"""
Build script to create Nova Launcher executable
Run this script to build the launcher.exe
"""
import subprocess
import sys
from pathlib import Path

def build_launcher():
    """Build the launcher executable using PyInstaller"""
    
    print("🔨 Building Nova Launcher executable...")
    print()
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
        print("✅ PyInstaller found")
    except ImportError:
        print("❌ PyInstaller not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✅ PyInstaller installed")
    
    print()
    print("📦 Building executable...")
    print()
    
    # PyInstaller command
    launcher_path = Path(__file__).parent / "backend" / "launcher.py"
    if not launcher_path.exists():
        print(f"❌ Error: launcher.py not found at {launcher_path}")
        sys.exit(1)
    
    icon_path = Path(__file__).parent / "frontend" / "favicon.ico"
    
    # Set output directory to project root dist folder
    dist_path = Path(__file__).parent / "dist"
    work_path = Path(__file__).parent / "build"
    
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--onefile",  # Single executable file
        "--windowed",  # No console window (GUI only)
        "--name=NovaLauncher",  # Output name
        "--clean",  # Clean cache
        "--noconfirm",  # Overwrite without asking
        "--distpath", str(dist_path),  # Output directory
        "--workpath", str(work_path),  # Build directory
    ]
    
    # Add icon if exists
    if icon_path.exists():
        cmd.extend(["--icon", str(icon_path)])
        print(f"🎨 Using icon: {icon_path}")
    
    cmd.append(str(launcher_path))
    
    try:
        subprocess.check_call(cmd)
        print()
        print("=" * 60)
        print("✅ BUILD SUCCESSFUL!")
        print("=" * 60)
        print()
        print("📁 Executable location: dist/NovaLauncher.exe")
        print()
        print("You can now:")
        print("  1. Run dist/NovaLauncher.exe")
        print("  2. Create a shortcut on your desktop")
        print("  3. Pin it to your taskbar")
        print()
        
    except subprocess.CalledProcessError as e:
        print()
        print("=" * 60)
        print("❌ BUILD FAILED")
        print("=" * 60)
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    build_launcher()
