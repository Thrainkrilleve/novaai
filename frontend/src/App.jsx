import { useState, useEffect, useRef } from 'react'
import axios from 'axios'
import { 
  Send, 
  Monitor, 
  Globe, 
  Trash2, 
  Check, 
  AlertCircle,
  Loader2,
  Eye,
  EyeOff
} from 'lucide-react'

const API_BASE = 'http://localhost:8000'

function App() {
  const [messages, setMessages] = useState([])
  const [inputMessage, setInputMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [includeScreen, setIncludeScreen] = useState(false)
  const [systemHealth, setSystemHealth] = useState(null)
  const [sessionId] = useState(() => `session_${Date.now()}`)
  const [showWebBrowser, setShowWebBrowser] = useState(false)
  const [webUrl, setWebUrl] = useState('')
  const [isWatchMode, setIsWatchMode] = useState(false)
  const [watchInterval, setWatchInterval] = useState(10)
  const [ws, setWs] = useState(null)
  
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)

  // Check system health on mount
  useEffect(() => {
    checkHealth()
    loadHistory()
    setupWebSocket()
    
    return () => {
      if (ws) {
        ws.close()
      }
    }
  }, [])
  
  const setupWebSocket = () => {
    const websocket = new WebSocket('ws://localhost:8000/ws/chat')
    
    websocket.onopen = () => {
      console.log('WebSocket connected')
      setWs(websocket)
    }
    
    websocket.onmessage = (event) => {
      const data = JSON.parse(event.data)
      
      if (data.type === 'proactive') {
        // AI initiated a message
        const aiMessage = {
          role: 'assistant',
          content: data.content,
          timestamp: new Date(),
          isProactive: true
        }
        setMessages(prev => [...prev, aiMessage])
        
        // Play notification sound or show alert
        if ('Notification' in window && Notification.permission === 'granted') {
          new Notification('AI Assistant', {
            body: data.content,
            icon: '/vite.svg'
          })
        }
      } else if (data.type === 'watch_status') {
        setIsWatchMode(data.watching)
      }
    }
    
    websocket.onclose = () => {
      console.log('WebSocket disconnected')
      setWs(null)
    }
  }

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const checkHealth = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/health`)
      setSystemHealth(response.data)
    } catch (error) {
      console.error('Health check failed:', error)
      setSystemHealth({ status: 'error', ollama: 'disconnected' })
    }
  }

  const loadHistory = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/history`, {
        params: { limit: 20, session_id: sessionId }
      })
      
      const formattedMessages = response.data.history.map(msg => ({
        role: msg.role,
        content: msg.content,
        timestamp: new Date(msg.timestamp)
      }))
      
      setMessages(formattedMessages)
    } catch (error) {
      console.error('Failed to load history:', error)
    }
  }

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return

    const userMessage = {
      role: 'user',
      content: inputMessage,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInputMessage('')
    setIsLoading(true)

    try {
      const response = await axios.post(`${API_BASE}/api/chat`, {
        message: inputMessage,
        include_screen: includeScreen,
        session_id: sessionId
      })

      const aiMessage = {
        role: 'assistant',
        content: response.data.response,
        timestamp: new Date(),
        hadScreenContext: response.data.had_screen_context
      }

      setMessages(prev => [...prev, aiMessage])
    } catch (error) {
      console.error('Chat error:', error)
      
      const errorMessage = {
        role: 'assistant',
        content: `Error: ${error.response?.data?.detail || error.message}`,
        timestamp: new Date(),
        isError: true
      }
      
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
      inputRef.current?.focus()
    }
  }

  const captureScreen = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/screen/capture`)
      
      const screenMessage = {
        role: 'system',
        content: 'Screen captured successfully',
        timestamp: new Date(),
        image: response.data.image
      }
      
      setMessages(prev => [...prev, screenMessage])
    } catch (error) {
      console.error('Screen capture error:', error)
    }
  }

  const navigateWeb = async () => {
    if (!webUrl.trim()) return

    try {
      const response = await axios.post(`${API_BASE}/api/web/navigate`, {
        url: webUrl
      })

      if (response.data.success) {
        const webMessage = {
          role: 'system',
          content: `Navigated to: ${response.data.title || response.data.url}`,
          timestamp: new Date()
        }
        setMessages(prev => [...prev, webMessage])
      }
    } catch (error) {
      console.error('Web navigation error:', error)
    }
  }

  const clearHistory = () => {
    setMessages([])
  }
  
  const toggleWatchMode = () => {
    if (!ws) {
      alert('WebSocket not connected')
      return
    }
    
    if (isWatchMode) {
      // Stop watching
      ws.send(JSON.stringify({ action: 'stop_watch' }))
    } else {
      // Request notification permission
      if ('Notification' in window && Notification.permission === 'default') {
        Notification.requestPermission()
      }
      
      // Start watching
      ws.send(JSON.stringify({ 
        action: 'start_watch',
        interval: watchInterval 
      }))
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  return (
    <div className="flex flex-col h-screen bg-slate-900 text-white">
      {/* Header */}
      <header className="bg-slate-800 border-b border-slate-700 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
              Local AI Assistant
            </h1>
            <p className="text-sm text-slate-400 mt-1">
              Powered by Ollama • No API Keys Required
            </p>
          </div>
          
          <div className="flex items-center gap-4">
            {/* Health Status */}
            {systemHealth && (
              <div className="flex items-center gap-2 text-sm">
                {systemHealth.ollama === 'connected' ? (
                  <>
                    <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                    <span className="text-green-400">Ollama Connected</span>
                  </>
                ) : (
                  <>
                    <AlertCircle className="w-4 h-4 text-red-400" />
                    <span className="text-red-400">Ollama Disconnected</span>
                  </>
                )}
              </div>
            )}
            
            {/* Clear History */}
            <button
              onClick={clearHistory}
              className="px-3 py-2 bg-red-500/10 hover:bg-red-500/20 text-red-400 rounded-lg transition-colors flex items-center gap-2"
            >
              <Trash2 className="w-4 h-4" />
              Clear
            </button>
          </div>
        </div>
      </header>

      {/* Main Chat Area */}
      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-slate-400">
            <div className="text-6xl mb-4">🤖</div>
            <h2 className="text-2xl font-semibold mb-2">Welcome to Local AI Assistant</h2>
            <p className="text-center max-w-md">
              Start chatting with your local AI. Enable screen sharing to let the AI see what you're doing,
              or use web browsing to navigate the internet together.
            </p>
          </div>
        ) : (
          messages.map((msg, idx) => (
            <div
              key={idx}
              className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                  msg.role === 'user'
                    ? 'bg-blue-600 text-white'
                    : msg.role === 'system'
                    ? 'bg-slate-700 text-slate-300'
                    : msg.isError
                    ? 'bg-red-500/20 text-red-300'
                    : msg.isProactive
                    ? 'bg-purple-600 text-white border-2 border-purple-400'
                    : 'bg-slate-800 text-slate-100'
                }`}
              >
                {msg.image && (
                  <img 
                    src={msg.image} 
                    alt="Screenshot" 
                    className="rounded-lg mb-2 max-w-full"
                  />
                )}
                
                <div className="whitespace-pre-wrap break-words">
                  {msg.content}
                </div>
                
                {msg.isProactive && (
                  <div className="flex items-center gap-1 mt-2 text-xs text-purple-200">
                    <AlertCircle className="w-3 h-3" />
                    AI initiated this message
                  </div>
                )}
                
                {msg.hadScreenContext && (
                  <div className="flex items-center gap-1 mt-2 text-xs text-blue-300">
                    <Eye className="w-3 h-3" />
                    Screen context included
                  </div>
                )}
                
                <div className="text-xs opacity-50 mt-1">
                  {msg.timestamp.toLocaleTimeString()}
                </div>
              </div>
            </div>
          ))
        )}
        
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-slate-800 rounded-2xl px-4 py-3 flex items-center gap-2">
              <Loader2 className="w-4 h-4 animate-spin" />
              <span className="text-slate-300">Thinking...</span>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Web Browser Panel */}
      {showWebBrowser && (
        <div className="bg-slate-800 border-t border-slate-700 px-6 py-3">
          <div className="flex items-center gap-2">
            <Globe className="w-5 h-5 text-blue-400" />
            <input
              type="text"
              value={webUrl}
              onChange={(e) => setWebUrl(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && navigateWeb()}
              placeholder="Enter URL (e.g., https://example.com)"
              className="flex-1 bg-slate-700 border border-slate-600 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              onClick={navigateWeb}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors"
            >
              Navigate
            </button>
          </div>
        </div>
      )}

      {/* Input Area */}
      <div className="bg-slate-800 border-t border-slate-700 px-6 py-4">
        {/* Action Buttons */}
        <div className="flex items-center gap-2 mb-3 flex-wrap">
          <button
            onClick={() => setIncludeScreen(!includeScreen)}
            className={`px-3 py-2 rounded-lg transition-colors flex items-center gap-2 ${
              includeScreen
                ? 'bg-blue-600 text-white'
                : 'bg-slate-700 hover:bg-slate-600 text-slate-300'
            }`}
          >
            {includeScreen ? <Eye className="w-4 h-4" /> : <EyeOff className="w-4 h-4" />}
            {includeScreen ? 'Screen Enabled' : 'Enable Screen'}
          </button>
          
          <button
            onClick={captureScreen}
            className="px-3 py-2 bg-slate-700 hover:bg-slate-600 text-slate-300 rounded-lg transition-colors flex items-center gap-2"
          >
            <Monitor className="w-4 h-4" />
            Capture Now
          </button>
          
          <button
            onClick={() => setShowWebBrowser(!showWebBrowser)}
            className={`px-3 py-2 rounded-lg transition-colors flex items-center gap-2 ${
              showWebBrowser
                ? 'bg-purple-600 text-white'
                : 'bg-slate-700 hover:bg-slate-600 text-slate-300'
            }`}
          >
            <Globe className="w-4 h-4" />
            Web Browser
          </button>
          
          <div className="flex-1"></div>
          
          <button
            onClick={toggleWatchMode}
            className={`px-3 py-2 rounded-lg transition-colors flex items-center gap-2 ${
              isWatchMode
                ? 'bg-green-600 text-white animate-pulse'
                : 'bg-slate-700 hover:bg-slate-600 text-slate-300'
            }`}
            title="AI will proactively monitor your screen and speak up when it has something useful to say"
          >
            <AlertCircle className="w-4 h-4" />
            {isWatchMode ? 'Watch Mode ON' : 'Watch Mode'}
          </button>
          
          {isWatchMode && (
            <select
              value={watchInterval}
              onChange={(e) => setWatchInterval(Number(e.target.value))}
              className="px-2 py-2 bg-slate-700 text-slate-300 rounded-lg text-sm"
            >
              <option value={1}>1s (Stream-like)</option>
              <option value={2}>2s (Near Real-time)</option>
              <option value={3}>3s (Real-time)</option>
              <option value={5}>5s (Very Fast)</option>
              <option value={10}>10s (Fast)</option>
              <option value={15}>15s</option>
              <option value={30}>30s</option>
              <option value={60}>1m</option>
              <option value={120}>2m</option>
              <option value={300}>5m</option>
            </select>
          )}
        </div>

        {/* Message Input */}
        <div className="flex items-center gap-3">
          <textarea
            ref={inputRef}
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message... (Shift+Enter for new line)"
            rows="1"
            className="flex-1 bg-slate-700 border border-slate-600 rounded-lg px-4 py-3 resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          
          <button
            onClick={sendMessage}
            disabled={isLoading || !inputMessage.trim()}
            className="px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-600 disabled:cursor-not-allowed rounded-lg transition-colors flex items-center gap-2"
          >
            {isLoading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Send className="w-5 h-5" />
            )}
          </button>
        </div>
      </div>
    </div>
  )
}

export default App
