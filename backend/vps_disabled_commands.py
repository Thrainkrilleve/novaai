"""
VPS Mode - Disabled command handlers for screen capture and browser features
These commands are disabled when Nova is running on a VPS without display/browser access
"""

VPS_DISABLED_MESSAGE = """
⚠️ **Feature Unavailable in VPS Mode**

This command requires local screen access or browser automation, which is disabled when Nova runs on a remote server.

**Disabled Features:**
• Screen capture (!screen, !screenshot)
• Web browser automation (!browse, !web, !search)
• Page analysis (!links, !extract, !pageinfo)
• Video analysis (!video, !watch)

**Why?** Nova is running on a VPS (Virtual Private Server) without desktop environment or browser.

**What Still Works:**
✅ Chat with Nova
✅ Discord commands (!chat, !ask)
✅ Memory and learning (!memory, !learn)
✅ Code generation (!codegen, !createfile)
✅ EVE Online helper (!eve)
✅ Voice features (!speak, !join, !leave)
✅ Autonomous features (!autonomous)

Need these features? Run Nova locally on your own computer with screen and browser access!
"""

def get_disabled_message():
    """Get the standard message for VPS-disabled features"""
    return VPS_DISABLED_MESSAGE
