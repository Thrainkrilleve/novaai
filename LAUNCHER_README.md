# Nova Launcher - GUI Executable

## Quick Start

### 1. Build the Executable

Run the build script:
```powershell
python build_launcher.py
```

This will:
- Install PyInstaller if needed
- Create a single executable file `NovaLauncher.exe` in the `dist` folder
- Include icon (if available)

### 2. Run the Launcher

After building, you can run:
```powershell
.\dist\NovaLauncher.exe
```

Or double-click the executable in Windows Explorer.

## Features

The launcher provides a graphical interface with:

- **🚀 Launch Backend** - Start the FastAPI web server (http://localhost:8000)
- **💬 Launch Discord Bot** - Start the Discord userbot
- **⚡ Launch Both** - Start both services simultaneously
- **⏹ Stop Controls** - Individual stop buttons for each service or stop all
- **📋 Console Output** - Real-time log display of all service output
- **Status Indicators** - Visual status for each service (Running/Stopped)

## Usage

### Running Services

1. Open NovaLauncher.exe
2. Click the button for the service(s) you want to start:
   - **Launch Backend** for web interface only
   - **Launch Discord Bot** for Discord functionality
   - **Launch Both** to run everything

### Stopping Services

- Use individual stop buttons to stop specific services
- Use **Stop All** to stop everything at once
- Services will automatically stop when you close the launcher

### Console Output

The bottom panel shows real-time logs from both services:
- `[Backend]` messages from the FastAPI server
- `[Discord]` messages from the Discord bot

## Distribution

After building, you can:

1. **Create Desktop Shortcut**
   - Right-click `dist\NovaLauncher.exe`
   - Select "Create shortcut"
   - Move shortcut to Desktop

2. **Pin to Taskbar**
   - Right-click `NovaLauncher.exe`
   - Select "Pin to taskbar"

3. **Share the Executable**
   - The `.exe` file is standalone
   - Copy `dist\NovaLauncher.exe` to any Windows machine
   - Note: It must be in the same location relative to the backend folder

## Technical Details

- Built with Python's tkinter (no external dependencies for GUI)
- Uses subprocess to launch services in separate console windows
- Services run independently and can be monitored/stopped through the GUI
- Automatic process cleanup on exit

## Troubleshooting

### "Python not found" error
- The launcher uses the Python interpreter from your system
- Ensure Python is installed and in your PATH

### Services don't start
- Check that `backend\main.py` and `backend\discord_bot.py` exist
- Verify all dependencies are installed (`pip install -r backend\requirements.txt`)
- Check console output for specific error messages

### Build fails
- Install PyInstaller manually: `pip install pyinstaller`
- Run build command manually: `pyinstaller --onefile --windowed backend\launcher.py`

## Customization

To modify the launcher:
1. Edit `backend\launcher.py`
2. Rebuild with `python build_launcher.py`
3. New executable will be in `dist\NovaLauncher.exe`
