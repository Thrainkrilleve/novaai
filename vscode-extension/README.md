# Nova VS Code Bridge Extension

This extension allows Nova (Discord AI assistant) to interact with VS Code - reading, writing, and editing files directly from Discord.

## Features

- **File Operations**: Create, read, write, and edit files
- **Editor Control**: Open files, navigate to lines, get active editor info
- **Workspace Info**: Get workspace folders and paths
- **Command Execution**: Execute VS Code commands remotely
- **Notifications**: Show messages in VS Code from Discord

## Installation

### 1. Install Dependencies

```powershell
cd h:\TheAI\vscode-extension
npm install
```

### 2. Compile TypeScript

```powershell
npm run compile
```

### 3. Install Extension in VS Code

**Option A: Debug Mode (Recommended for development)**
1. Open `h:\TheAI\vscode-extension` folder in VS Code
2. Press `F5` to launch Extension Development Host
3. The extension will start automatically

**Option B: Package and Install**
```powershell
# Install vsce if you don't have it
npm install -g @vscode/vsce

# Package the extension
vsce package

# Install the .vsix file in VS Code
# Extensions > ... > Install from VSIX
```

## Configuration

Open VS Code settings and configure:

- `nova.serverPort`: Port for the bridge server (default: 3737)
- `nova.autoStart`: Auto-start server on VS Code startup (default: true)

## Usage

### Start the Bridge Server

The server starts automatically by default. You can also control it via commands:

- **Command Palette** → `Nova: Start Bridge Server`
- **Command Palette** → `Nova: Stop Bridge Server`
- **Command Palette** → `Nova: Show Status`

The status bar shows: `Nova: Online :3737` when running.

### From Discord

Once the extension is running, use these commands in Discord:

```
!vscode status          # Check connection
!vscode active          # Get active editor info
!vscode read file.py    # Read a file
!vscode open file.py    # Open file in VS Code

!createfile test.py print("hello")
!codegen calc.py Create a calculator with basic math functions
```

## API Endpoints

The extension exposes these HTTP endpoints on `http://localhost:3737`:

### Health Check
```
GET /health
```

### Editor Operations
```
GET  /editor/active              # Get active editor info
GET  /file/read?path=<path>      # Read file content
POST /file/write                 # Write/create file
POST /file/open                  # Open file in editor
POST /file/edit                  # Edit file (replace lines)
```

### Workspace
```
GET /workspace/folders           # Get workspace folders
```

### Commands
```
POST /command/execute            # Execute VS Code command
POST /notification/show          # Show notification
```

## Example: Using from Python

```python
from vscode_client import vscode_client

# Check if available
available = await vscode_client.is_available()

# Create and open a file
await vscode_client.write_file("test.py", "print('Hello')", open_file=True)

# Read a file
content = await vscode_client.read_file("test.py")

# Open file at specific line
await vscode_client.open_file("test.py", line=10)
```

## Troubleshooting

### Server won't start
- Check if port 3737 is already in use
- Change the port in settings: `nova.serverPort`
- Check VS Code Developer Tools for errors (Help > Toggle Developer Tools)

### Commands not working from Discord
1. Check VS Code status bar shows "Nova: Online"
2. Test manually: `curl http://localhost:3737/health`
3. Ensure firewall allows localhost connections

### Extension not activating
- Check VS Code version is 1.85.0 or higher
- Look for errors in Output panel (Output > Extension Host)

## Development

### Project Structure
```
vscode-extension/
├── src/
│   └── extension.ts      # Main extension code
├── package.json          # Extension manifest
├── tsconfig.json         # TypeScript config
└── README.md            # This file
```

### Building
```powershell
npm run compile          # Compile TypeScript
npm run watch           # Watch mode for development
```

### Testing
1. Open extension folder in VS Code
2. Press `F5` to launch Extension Development Host
3. Test commands in the new window

## Security Notes

⚠️ **This extension opens an HTTP server that can control VS Code**

- Only accessible on localhost by default
- No authentication (assumes trusted local environment)
- Don't expose port 3737 externally
- Use only in development/personal environments

## License

MIT
