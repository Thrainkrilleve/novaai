"""VS Code Bridge Client - Communicate with Nova VS Code extension"""
import aiohttp
from typing import Optional, Dict, Any

class VSCodeClient:
    def __init__(self, host: str = "localhost", port: int = 3737):
        self.base_url = f"http://{host}:{port}"
        
    async def is_available(self) -> bool:
        """Check if VS Code bridge is running"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/health", timeout=aiohttp.ClientTimeout(total=2)) as response:
                    return response.status == 200
        except:
            return False
    
    async def get_active_editor(self) -> Optional[Dict[str, Any]]:
        """Get information about the active editor"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/editor/active") as response:
                    if response.status == 200:
                        return await response.json()
                    return None
        except Exception as e:
            print(f"Error getting active editor: {e}")
            return None
    
    async def read_file(self, path: str) -> Optional[Dict[str, Any]]:
        """Read file content from VS Code"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/file/read", params={"path": path}) as response:
                    if response.status == 200:
                        return await response.json()
                    return None
        except Exception as e:
            print(f"Error reading file: {e}")
            return None
    
    async def write_file(self, path: str, content: str, open_file: bool = True) -> bool:
        """Write content to a file"""
        try:
            print(f"🔧 Attempting to write file: {path}")
            print(f"📝 Content length: {len(content)} chars")
            print(f"🔓 Open after write: {open_file}")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.base_url}/file/write", json={
                    "path": path,
                    "content": content,
                    "open": open_file
                }) as response:
                    status = response.status
                    response_text = await response.text()
                    print(f"✅ VS Code API Response: {status} - {response_text}")
                    return status == 200
        except Exception as e:
            print(f"❌ Error writing file: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def open_file(self, path: str, line: Optional[int] = None) -> bool:
        """Open a file in VS Code"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.base_url}/file/open", json={
                    "path": path,
                    "line": line
                }) as response:
                    return response.status == 200
        except Exception as e:
            print(f"Error opening file: {e}")
            return False
    
    async def edit_file(self, path: str, start_line: int, end_line: int, new_text: str) -> bool:
        """Edit a file by replacing lines"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.base_url}/file/edit", json={
                    "path": path,
                    "startLine": start_line,
                    "endLine": end_line,
                    "newText": new_text
                }) as response:
                    return response.status == 200
        except Exception as e:
            print(f"Error editing file: {e}")
            return False
    
    async def get_workspace_folders(self) -> list:
        """Get all workspace folders"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/workspace/folders") as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("folders", [])
                    return []
        except Exception as e:
            print(f"Error getting workspace folders: {e}")
            return []
    
    async def execute_command(self, command: str, args: Optional[list] = None) -> Optional[Any]:
        """Execute a VS Code command"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.base_url}/command/execute", json={
                    "command": command,
                    "args": args or []
                }) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("result")
                    return None
        except Exception as e:
            print(f"Error executing command: {e}")
            return None
    
    async def show_notification(self, message: str, notification_type: str = "info") -> bool:
        """Show a notification in VS Code"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.base_url}/notification/show", json={
                    "message": message,
                    "type": notification_type
                }) as response:
                    return response.status == 200
        except Exception as e:
            print(f"Error showing notification: {e}")
            return False

# Global instance
vscode_client = VSCodeClient()
