"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.activate = activate;
exports.deactivate = deactivate;
const vscode = __importStar(require("vscode"));
const express_1 = __importDefault(require("express"));
const chatProvider_1 = require("./chatProvider");
let server = null;
let statusBarItem;
function activate(context) {
    console.log('Nova VS Code Bridge is activating...');
    // Create status bar item
    statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
    statusBarItem.text = "$(radio-tower) Nova: Offline";
    statusBarItem.command = 'nova.showStatus';
    statusBarItem.show();
    context.subscriptions.push(statusBarItem);
    // Register chat view provider
    const chatProvider = new chatProvider_1.NovaChatProvider(context.extensionUri);
    context.subscriptions.push(vscode.window.registerWebviewViewProvider(chatProvider_1.NovaChatProvider.viewType, chatProvider));
    // Register commands
    context.subscriptions.push(vscode.commands.registerCommand('nova.startServer', () => startServer()));
    context.subscriptions.push(vscode.commands.registerCommand('nova.stopServer', () => stopServer()));
    context.subscriptions.push(vscode.commands.registerCommand('nova.showStatus', () => showStatus()));
    context.subscriptions.push(vscode.commands.registerCommand('nova.openChat', () => {
        vscode.commands.executeCommand('nova.chatView.focus');
    }));
    // Auto-start if enabled
    const config = vscode.workspace.getConfiguration('nova');
    if (config.get('autoStart', true)) {
        startServer();
    }
}
function startServer() {
    if (server) {
        vscode.window.showInformationMessage('Nova bridge server is already running');
        return;
    }
    const app = (0, express_1.default)();
    app.use(express_1.default.json({ limit: '50mb' }));
    const config = vscode.workspace.getConfiguration('nova');
    const port = config.get('serverPort', 3737);
    // CORS headers
    app.use((req, res, next) => {
        res.header('Access-Control-Allow-Origin', '*');
        res.header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE');
        res.header('Access-Control-Allow-Headers', 'Content-Type');
        next();
    });
    // Health check
    app.get('/health', (req, res) => {
        res.json({ status: 'ok', message: 'Nova VS Code Bridge is running' });
    });
    // Get active editor info
    app.get('/editor/active', (req, res) => {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            return res.status(404).json({ error: 'No active editor' });
        }
        res.json({
            fileName: editor.document.fileName,
            languageId: editor.document.languageId,
            lineCount: editor.document.lineCount,
            isDirty: editor.document.isDirty,
            selection: {
                start: editor.selection.start.line,
                end: editor.selection.end.line
            }
        });
    });
    // Read file content
    app.get('/file/read', async (req, res) => {
        const filePath = req.query.path;
        if (!filePath) {
            return res.status(400).json({ error: 'File path is required' });
        }
        try {
            const uri = vscode.Uri.file(filePath);
            const document = await vscode.workspace.openTextDocument(uri);
            res.json({
                content: document.getText(),
                languageId: document.languageId,
                lineCount: document.lineCount
            });
        }
        catch (error) {
            res.status(500).json({ error: error.message });
        }
    });
    // Write/create file
    app.post('/file/write', async (req, res) => {
        const { path, content, open = false } = req.body;
        if (!path) {
            return res.status(400).json({ error: 'File path is required' });
        }
        try {
            const uri = vscode.Uri.file(path);
            const encoder = new TextEncoder();
            await vscode.workspace.fs.writeFile(uri, encoder.encode(content || ''));
            if (open) {
                const document = await vscode.workspace.openTextDocument(uri);
                await vscode.window.showTextDocument(document);
            }
            res.json({ success: true, message: 'File written successfully' });
        }
        catch (error) {
            res.status(500).json({ error: error.message });
        }
    });
    // Open file in editor
    app.post('/file/open', async (req, res) => {
        const { path, line } = req.body;
        if (!path) {
            return res.status(400).json({ error: 'File path is required' });
        }
        try {
            const uri = vscode.Uri.file(path);
            const document = await vscode.workspace.openTextDocument(uri);
            const editor = await vscode.window.showTextDocument(document);
            if (line !== undefined) {
                const position = new vscode.Position(line, 0);
                editor.selection = new vscode.Selection(position, position);
                editor.revealRange(new vscode.Range(position, position));
            }
            res.json({ success: true, message: 'File opened successfully' });
        }
        catch (error) {
            res.status(500).json({ error: error.message });
        }
    });
    // Edit file (replace text)
    app.post('/file/edit', async (req, res) => {
        const { path, startLine, endLine, newText } = req.body;
        if (!path) {
            return res.status(400).json({ error: 'File path is required' });
        }
        try {
            const uri = vscode.Uri.file(path);
            const document = await vscode.workspace.openTextDocument(uri);
            const editor = await vscode.window.showTextDocument(document);
            await editor.edit(editBuilder => {
                const start = new vscode.Position(startLine || 0, 0);
                const end = endLine !== undefined
                    ? new vscode.Position(endLine, document.lineAt(endLine).text.length)
                    : new vscode.Position(document.lineCount - 1, document.lineAt(document.lineCount - 1).text.length);
                editBuilder.replace(new vscode.Range(start, end), newText || '');
            });
            await document.save();
            res.json({ success: true, message: 'File edited successfully' });
        }
        catch (error) {
            res.status(500).json({ error: error.message });
        }
    });
    // Get workspace folders
    app.get('/workspace/folders', (req, res) => {
        const folders = vscode.workspace.workspaceFolders?.map(folder => ({
            name: folder.name,
            path: folder.uri.fsPath
        })) || [];
        res.json({ folders });
    });
    // Execute VS Code command
    app.post('/command/execute', async (req, res) => {
        const { command, args } = req.body;
        if (!command) {
            return res.status(400).json({ error: 'Command is required' });
        }
        try {
            const result = await vscode.commands.executeCommand(command, ...(args || []));
            res.json({ success: true, result });
        }
        catch (error) {
            res.status(500).json({ error: error.message });
        }
    });
    // Show message/notification
    app.post('/notification/show', async (req, res) => {
        const { message, type = 'info' } = req.body;
        if (!message) {
            return res.status(400).json({ error: 'Message is required' });
        }
        try {
            switch (type) {
                case 'error':
                    vscode.window.showErrorMessage(message);
                    break;
                case 'warning':
                    vscode.window.showWarningMessage(message);
                    break;
                default:
                    vscode.window.showInformationMessage(message);
            }
            res.json({ success: true });
        }
        catch (error) {
            res.status(500).json({ error: error.message });
        }
    });
    // Start server
    server = app.listen(port, () => {
        console.log(`Nova bridge server running on port ${port}`);
        statusBarItem.text = `$(radio-tower) Nova: Online :${port}`;
        statusBarItem.tooltip = `Nova bridge server running on port ${port}`;
        vscode.window.showInformationMessage(`Nova bridge server started on port ${port}`);
    });
    if (server) {
        server.on('error', (error) => {
            vscode.window.showErrorMessage(`Failed to start Nova bridge server: ${error.message}`);
            statusBarItem.text = "$(radio-tower) Nova: Error";
            server = null;
        });
    }
}
function stopServer() {
    if (!server) {
        vscode.window.showInformationMessage('Nova bridge server is not running');
        return;
    }
    server.close(() => {
        console.log('Nova bridge server stopped');
        statusBarItem.text = "$(radio-tower) Nova: Offline";
        statusBarItem.tooltip = 'Nova bridge server is offline';
        vscode.window.showInformationMessage('Nova bridge server stopped');
        server = null;
    });
}
function showStatus() {
    const config = vscode.workspace.getConfiguration('nova');
    const port = config.get('serverPort', 3737);
    const autoStart = config.get('autoStart', true);
    const status = server ? `Running on port ${port}` : 'Offline';
    const message = `Nova VS Code Bridge\n\nStatus: ${status}\nAuto-start: ${autoStart}`;
    vscode.window.showInformationMessage(message);
}
function deactivate() {
    if (server) {
        server.close();
        server = null;
    }
}
//# sourceMappingURL=extension.js.map