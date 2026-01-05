# VS Code Integration Setup Guide

## Quick Start

### 1. Install the Extension

The extension is located in `h:\TheAI\vscode-extension`.

**Open it in VS Code:**
```powershell
code h:\TheAI\vscode-extension
```

**Then press `F5`** to launch the Extension Development Host with the Nova bridge extension loaded.

### 2. Verify It's Running

Look for the status bar item in VS Code (bottom right):
- ✅ `Nova: Online :3737` = Working!
- ❌ `Nova: Offline` = Not started

You can also run the command:
- Open Command Palette (`Ctrl+Shift+P`)
- Type: `Nova: Show Status`

### 3. Test from Discord

In Discord, send:
```
!vscode status
```

You should see: "✅ VS Code Bridge Connected"

## Discord Commands

### Check Status
```
!vscode status          # Check if bridge is connected
!status                 # Full bot status (includes VS Code)
```

### File Operations
```
!vscode active          # See what file is currently open
!vscode read file.py    # Read a file's contents
!vscode open file.py    # Open a file in VS Code
```

### Create Files
```
!createfile test.py print("Hello, World!")
!createfile notes.txt This is a new text file
```

### Generate Code with AI
```
!codegen calculator.py Create a calculator with add, subtract, multiply, divide functions
!codegen server.js Create an Express server with routes for GET and POST
!codegen index.html Create a landing page with hero section and contact form
```

## Examples

### Example 1: Generate Python Script
```
!codegen fizzbuzz.py Write a FizzBuzz program that prints numbers 1-100, but for multiples of 3 print "Fizz", for multiples of 5 print "Buzz", and for multiples of both print "FizzBuzz"
```

Nova will:
1. Generate the Python code
2. Save it to `fizzbuzz.py`
3. Open it in VS Code automatically

### Example 2: Check Active File
```
User: !vscode active
Nova: 📝 Active Editor
      File: h:\TheAI\backend\discord_bot.py
      Language: python
      Lines: 1115
      Modified: No
```

### Example 3: Quick File Creation
```
!createfile todo.md # My Todo List\n\n- Set up Nova\n- Test VS Code integration\n- Build something awesome
```

## Advanced Usage

### Working with Nova's Context

Nova can see your screen with `!screen`, so you can:

1. Open a file in VS Code
2. Send `!screen` in Discord
3. Ask Nova: "Can you review this code and suggest improvements?"
4. Nova sees your code and can suggest changes
5. Use `!codegen` to have Nova create the improved version

### Combining Commands

```
# Read current file, ask Nova to improve it
!vscode active
!vscode read myfile.py
# (Nova sees the code)
# Then ask: "Can you optimize this code?"
```

## Troubleshooting

### "VS Code bridge is not running"
1. Make sure you opened `h:\TheAI\vscode-extension` in VS Code
2. Press `F5` to start the extension
3. Check status bar shows "Nova: Online"

### Files created in Discord don't appear in VS Code
**The Problem:** When you press `F5`, VS Code opens an "Extension Development Host" window - a separate VS Code instance for testing. Files will only open in that window, not your main VS Code window.

**Solution 1: Install the Extension Properly** (Recommended)
```powershell
# Package the extension
cd h:\TheAI\vscode-extension
npm install -g @vscode/vsce
vsce package

# This creates nova-bridge-x.x.x.vsix
# Then in VS Code: Extensions > ... > Install from VSIX > select the .vsix file
```

After installing, the bridge will run in your main VS Code window, and files will appear where you expect them.

**Solution 2: Use the Extension Development Host**
1. Press `F5` to open the Extension Development Host
2. Open your workspace folder (`h:\TheAI`) in the Extension Development Host window
3. Files created from Discord will now appear in that window
4. **Note:** Use the Extension Development Host window for your work, not the main window

### Extension won't compile
```powershell
cd h:\TheAI\vscode-extension
npm install
npm run compile
```

### Port 3737 already in use
Change the port in VS Code settings:
1. File > Preferences > Settings
2. Search for "nova.serverPort"
3. Change to a different port (e.g., 3738)
4. Restart the bridge: Command Palette > "Nova: Stop Bridge Server" then "Nova: Start Bridge Server"

### Discord bot can't connect
1. Check Windows Firewall isn't blocking port 3737
2. Test manually: Open browser to `http://localhost:3737/health`
3. Should see: `{"status":"ok","message":"Nova VS Code Bridge is running"}`

## Next Steps

- Try `!codegen` to generate different types of files (Python, JavaScript, HTML, etc.)
- Use `!screen` + VS Code to have Nova review your code
- Create complex projects by having Nova generate multiple files
- Use `!vscode open` to quickly jump to files from Discord

## Tips

- **File paths**: Use absolute paths (e.g., `h:\TheAI\test.py`) or relative to workspace
- **Code generation**: Be specific in your descriptions for better results
- **Screen + Code**: Show VS Code in screen capture for context-aware help
- **Workspace**: Open a folder in VS Code for better file organization

Enjoy having Nova as your coding assistant! 🚀
