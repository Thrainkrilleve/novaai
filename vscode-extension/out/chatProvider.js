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
exports.NovaChatProvider = void 0;
const vscode = __importStar(require("vscode"));
const axios_1 = __importDefault(require("axios"));
class NovaChatProvider {
    constructor(_extensionUri) {
        this._extensionUri = _extensionUri;
        this.ollamaUrl = 'http://localhost:11434';
        this.model = 'llama3.2-vision';
    }
    resolveWebviewView(webviewView, context, _token) {
        this._view = webviewView;
        webviewView.webview.options = {
            enableScripts: true,
            localResourceRoots: [this._extensionUri]
        };
        webviewView.webview.html = this._getHtmlForWebview(webviewView.webview);
        // Handle messages from the webview
        webviewView.webview.onDidReceiveMessage(async (data) => {
            switch (data.type) {
                case 'sendMessage':
                    await this.sendToOllama(data.message);
                    break;
                case 'insertCode':
                    this.insertCodeIntoEditor(data.code);
                    break;
            }
        });
    }
    async sendToOllama(message) {
        try {
            // Show loading state
            this._view?.webview.postMessage({
                type: 'loading',
                loading: true
            });
            const response = await axios_1.default.post(`${this.ollamaUrl}/api/generate`, {
                model: this.model,
                prompt: message,
                stream: false
            });
            const aiResponse = response.data.response;
            // Send response back to webview
            this._view?.webview.postMessage({
                type: 'response',
                message: aiResponse
            });
        }
        catch (error) {
            this._view?.webview.postMessage({
                type: 'error',
                message: `Error: ${error.message}. Make sure Ollama is running.`
            });
        }
        finally {
            this._view?.webview.postMessage({
                type: 'loading',
                loading: false
            });
        }
    }
    insertCodeIntoEditor(code) {
        const editor = vscode.window.activeTextEditor;
        if (editor) {
            editor.edit(editBuilder => {
                editBuilder.insert(editor.selection.active, code);
            });
        }
    }
    _getHtmlForWebview(webview) {
        return `<!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Nova Chat</title>
            <style>
                body {
                    padding: 10px;
                    color: var(--vscode-foreground);
                    font-family: var(--vscode-font-family);
                    font-size: var(--vscode-font-size);
                }
                #chat-container {
                    display: flex;
                    flex-direction: column;
                    height: 100vh;
                }
                #messages {
                    flex: 1;
                    overflow-y: auto;
                    margin-bottom: 10px;
                    padding: 10px;
                    background: var(--vscode-editor-background);
                    border-radius: 4px;
                }
                .message {
                    margin: 10px 0;
                    padding: 8px 12px;
                    border-radius: 6px;
                    line-height: 1.5;
                }
                .user-message {
                    background: var(--vscode-button-background);
                    color: var(--vscode-button-foreground);
                    margin-left: 20px;
                }
                .ai-message {
                    background: var(--vscode-editor-selectionBackground);
                    margin-right: 20px;
                }
                .error-message {
                    background: var(--vscode-inputValidation-errorBackground);
                    color: var(--vscode-inputValidation-errorForeground);
                    border: 1px solid var(--vscode-inputValidation-errorBorder);
                }
                pre {
                    background: var(--vscode-textCodeBlock-background);
                    padding: 10px;
                    border-radius: 4px;
                    overflow-x: auto;
                    position: relative;
                }
                code {
                    font-family: var(--vscode-editor-font-family);
                }
                .code-block {
                    position: relative;
                }
                .insert-btn {
                    position: absolute;
                    top: 5px;
                    right: 5px;
                    background: var(--vscode-button-background);
                    color: var(--vscode-button-foreground);
                    border: none;
                    padding: 4px 8px;
                    border-radius: 3px;
                    cursor: pointer;
                    font-size: 11px;
                }
                .insert-btn:hover {
                    background: var(--vscode-button-hoverBackground);
                }
                #input-container {
                    display: flex;
                    gap: 8px;
                }
                #message-input {
                    flex: 1;
                    padding: 8px;
                    background: var(--vscode-input-background);
                    color: var(--vscode-input-foreground);
                    border: 1px solid var(--vscode-input-border);
                    border-radius: 4px;
                    font-family: inherit;
                    font-size: inherit;
                }
                #send-button {
                    padding: 8px 16px;
                    background: var(--vscode-button-background);
                    color: var(--vscode-button-foreground);
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                    font-weight: 500;
                }
                #send-button:hover {
                    background: var(--vscode-button-hoverBackground);
                }
                #send-button:disabled {
                    opacity: 0.5;
                    cursor: not-allowed;
                }
                .loading {
                    display: inline-block;
                    width: 12px;
                    height: 12px;
                    border: 2px solid var(--vscode-foreground);
                    border-radius: 50%;
                    border-top-color: transparent;
                    animation: spin 1s linear infinite;
                }
                @keyframes spin {
                    to { transform: rotate(360deg); }
                }
            </style>
        </head>
        <body>
            <div id="chat-container">
                <div id="messages"></div>
                <div id="input-container">
                    <textarea id="message-input" rows="3" placeholder="Ask Nova anything..."></textarea>
                    <button id="send-button">Send</button>
                </div>
            </div>

            <script>
                const vscode = acquireVsCodeApi();
                const messagesDiv = document.getElementById('messages');
                const messageInput = document.getElementById('message-input');
                const sendButton = document.getElementById('send-button');

                function addMessage(content, isUser, isError = false) {
                    const messageDiv = document.createElement('div');
                    messageDiv.className = 'message ' + (isError ? 'error-message' : isUser ? 'user-message' : 'ai-message');
                    
                    // Parse code blocks
                    const codeBlockRegex = /\`\`\`([\\w]*)?\\n([\\s\\S]*?)\`\`\`/g;
                    let html = content;
                    
                    html = html.replace(codeBlockRegex, (match, lang, code) => {
                        return \`<div class="code-block">
                            <button class="insert-btn" onclick="insertCode(\\\`\${code.trim()}\\\`)">Insert</button>
                            <pre><code>\${escapeHtml(code.trim())}</code></pre>
                        </div>\`;
                    });
                    
                    // Handle inline code
                    html = html.replace(/\`([^\`]+)\`/g, '<code>$1</code>');
                    
                    // Handle line breaks
                    html = html.replace(/\\n/g, '<br>');
                    
                    messageDiv.innerHTML = html;
                    messagesDiv.appendChild(messageDiv);
                    messagesDiv.scrollTop = messagesDiv.scrollHeight;
                }

                function escapeHtml(text) {
                    const div = document.createElement('div');
                    div.textContent = text;
                    return div.innerHTML;
                }

                window.insertCode = function(code) {
                    vscode.postMessage({ type: 'insertCode', code });
                };

                function sendMessage() {
                    const message = messageInput.value.trim();
                    if (!message) return;

                    addMessage(message, true);
                    vscode.postMessage({ type: 'sendMessage', message });
                    messageInput.value = '';
                }

                sendButton.addEventListener('click', sendMessage);
                messageInput.addEventListener('keydown', (e) => {
                    if (e.key === 'Enter' && e.ctrlKey) {
                        sendMessage();
                    }
                });

                // Handle messages from extension
                window.addEventListener('message', event => {
                    const message = event.data;
                    switch (message.type) {
                        case 'response':
                            addMessage(message.message, false);
                            break;
                        case 'error':
                            addMessage(message.message, false, true);
                            break;
                        case 'loading':
                            sendButton.disabled = message.loading;
                            if (message.loading) {
                                const loadingDiv = document.createElement('div');
                                loadingDiv.className = 'message ai-message';
                                loadingDiv.id = 'loading-indicator';
                                loadingDiv.innerHTML = '<span class="loading"></span> Thinking...';
                                messagesDiv.appendChild(loadingDiv);
                            } else {
                                const loadingDiv = document.getElementById('loading-indicator');
                                if (loadingDiv) loadingDiv.remove();
                            }
                            break;
                    }
                });
            </script>
        </body>
        </html>`;
    }
}
exports.NovaChatProvider = NovaChatProvider;
NovaChatProvider.viewType = 'nova.chatView';
//# sourceMappingURL=chatProvider.js.map