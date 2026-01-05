# Nova Web Browser API - Complete Guide

## 🌐 Overview

Nova now has **powerful web automation capabilities** using Playwright. The browser persists across restarts and supports multiple tabs, advanced interactions, and data extraction.

## ⚙️ Configuration

```python
# backend/config.py
browser_headless: bool = False          # Show browser window
browser_timeout: int = 30000            # 30 second timeout
browser_persistent: bool = True         # Keep browser open after shutdown
```

## 🎯 Core Features

### Navigation

#### Navigate to URL
```http
POST /api/web/navigate
Content-Type: application/json

{
  "url": "https://example.com"
}
```

**Response:**
```json
{
  "success": true,
  "title": "Example Domain",
  "url": "https://example.com",
  "status": 200
}
```

#### Get Page Content
```http
GET /api/web/content
```

Returns the text content of the current page (no HTML tags).

#### Get Page Info
```http
GET /api/web/info
```

**Response:**
```json
{
  "success": true,
  "title": "Page Title",
  "url": "https://example.com",
  "domain": "example.com",
  "protocol": "https:",
  "scrollHeight": 2400,
  "scrollTop": 0,
  "viewportHeight": 900,
  "viewportWidth": 1600,
  "linkCount": 45,
  "imageCount": 12,
  "formCount": 2,
  "inputCount": 8,
  "buttonCount": 5
}
```

### Search

#### Google Search
```http
GET /api/web/search?query=artificial+intelligence
```

**Response:**
```json
{
  "success": true,
  "query": "artificial intelligence",
  "results": [
    {
      "title": "Artificial Intelligence - Wikipedia",
      "url": "https://en.wikipedia.org/wiki/Artificial_intelligence"
    }
  ]
}
```

### Content Extraction

#### Get All Links
```http
GET /api/web/links
```

**Response:**
```json
{
  "success": true,
  "count": 23,
  "links": [
    {
      "text": "Home",
      "href": "https://example.com/home",
      "title": "Go to homepage"
    }
  ]
}
```

#### Extract Structured Data
```http
GET /api/web/extract
```

Extracts headings, paragraphs, and lists from the page.

**Response:**
```json
{
  "success": true,
  "headings": [
    { "level": "H1", "text": "Main Title" },
    { "level": "H2", "text": "Section 1" }
  ],
  "paragraphs": [
    "This is a paragraph with meaningful content..."
  ],
  "lists": [
    "List item 1",
    "List item 2"
  ]
}
```

### Interactions

#### Click Element by Selector
```http
POST /api/web/action
Content-Type: application/json

{
  "action": "click",
  "selector": "#login-button"
}
```

#### Click Element by Text
```http
POST /api/web/click-text?text=Sign%20In
```

Clicks any element containing "Sign In" text.

#### Type Text
```http
POST /api/web/action
Content-Type: application/json

{
  "action": "type",
  "selector": "#search-box",
  "text": "hello world"
}
```

#### Fill Form (Multiple Fields)
```http
POST /api/web/fill-form
Content-Type: application/json

{
  "fields": {
    "#email": "user@example.com",
    "#password": "secretpass",
    "#name": "John Doe"
  }
}
```

**Response:**
```json
{
  "success": true,
  "results": [
    { "selector": "#email", "success": true },
    { "selector": "#password", "success": true },
    { "selector": "#name", "success": true }
  ]
}
```

#### Press Keyboard Key
```http
POST /api/web/press-key?key=Enter
```

Supported keys: `Enter`, `Escape`, `Tab`, `ArrowDown`, `ArrowUp`, etc.

### Page Manipulation

#### Scroll
```http
POST /api/web/scroll?direction=down&amount=500
```

**Directions:**
- `down` - Scroll down by amount
- `up` - Scroll up by amount
- `bottom` - Scroll to bottom of page
- `top` - Scroll to top of page

#### Execute JavaScript
```http
POST /api/web/action
Content-Type: application/json

{
  "action": "execute",
  "script": "return document.title;"
}
```

### Tab Management

#### List All Tabs
```http
GET /api/web/tabs
```

**Response:**
```json
{
  "success": true,
  "count": 3,
  "tabs": [
    {
      "index": 0,
      "title": "Google",
      "url": "https://google.com",
      "is_current": false
    },
    {
      "index": 1,
      "title": "GitHub",
      "url": "https://github.com",
      "is_current": true
    }
  ]
}
```

#### Open New Tab
```http
POST /api/web/tabs/new
Content-Type: application/json

{
  "url": "https://youtube.com"  # Optional
}
```

#### Switch Tab
```http
POST /api/web/tabs/switch?index=0
```

#### Close Tab
```http
DELETE /api/web/tabs/0
```

Or close current tab:
```http
DELETE /api/web/tabs
```

## 🤖 Using from Chat

Nova is now aware of all these capabilities! You can ask her naturally:

**Examples:**

- "Search Google for the latest AI news"
- "Go to reddit.com and click on the first post"
- "Open YouTube in a new tab"
- "What links are on this page?"
- "Fill out the login form with my email"
- "Scroll down and show me what you see"
- "Extract all the headings from this article"
- "Open 3 tabs: Google, GitHub, and Twitter"

Nova will use these APIs automatically based on your requests!

## 🔍 Advanced Examples

### Multi-Step Automation
```python
# 1. Search Google
POST /api/web/search?query=playwright+documentation

# 2. Navigate to first result
POST /api/web/navigate
{ "url": "https://playwright.dev" }

# 3. Extract structured content
GET /api/web/extract

# 4. Get all links
GET /api/web/links
```

### Form Automation
```python
# 1. Navigate to login page
POST /api/web/navigate
{ "url": "https://example.com/login" }

# 2. Fill form
POST /api/web/fill-form
{
  "fields": {
    "#username": "myuser",
    "#password": "mypass"
  }
}

# 3. Submit
POST /api/web/press-key?key=Enter
```

### Multi-Tab Research
```python
# 1. Open multiple research tabs
POST /api/web/tabs/new { "url": "https://arxiv.org" }
POST /api/web/tabs/new { "url": "https://scholar.google.com" }
POST /api/web/tabs/new { "url": "https://github.com/trending" }

# 2. Switch between tabs and extract data
POST /api/web/tabs/switch?index=0
GET /api/web/extract

POST /api/web/tabs/switch?index=1
GET /api/web/extract
```

## 📊 Diagnostic Logging

All browser operations now include detailed logging:

```
🌐 [Browser] Initializing Playwright...
    ✅ Playwright started
    Profile: C:\Users\...\Chrome\User Data - Automation
    Headless: False
    Persistent: True
    Launching Chrome with persistent context...
    Existing pages: 0
    ✅ Created new page
    ✅ Webdriver detection removed

✅ Browser initialized successfully (Persistent: True)

🌐 [Browser] Navigating to: https://example.com
    Loading page (timeout: 30000ms)...
    ✅ Page loaded: Example Domain
    Status: 200
```

## 🎯 Best Practices

1. **Browser Persistence**: Keep `browser_persistent = True` to maintain browser state across restarts
2. **Tab Management**: Use tabs for parallel research instead of sequential navigation
3. **Structured Extraction**: Use `/api/web/extract` for clean content instead of parsing HTML
4. **Text-Based Clicking**: Use `/api/web/click-text` when you don't know the selector
5. **Form Filling**: Use `/api/web/fill-form` for multiple fields instead of individual fills
6. **Error Handling**: All endpoints return `{"success": bool, "error": str}` format

## 🚀 Power User Tips

- **Chain Operations**: Navigate → Extract → Click → Extract for complex workflows
- **Tab Workflows**: Open multiple tabs, extract from all, then analyze results
- **JavaScript Power**: Use execute_script for custom data extraction
- **Smart Waits**: Browser automatically waits for network idle on navigation
- **Selector Flexibility**: Use CSS selectors, text content, or XPath

Nova now has enterprise-grade web automation capabilities! 🎉
