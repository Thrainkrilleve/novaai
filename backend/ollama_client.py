import aiohttp
import base64
import json
from typing import Optional, AsyncGenerator
from config import settings

class OllamaClient:
    """Client for interacting with local Ollama instance"""
    
    def __init__(self):
        self.base_url = settings.ollama_host
        self.model = settings.ollama_model
        
    async def chat(
        self, 
        message: str, 
        image_base64: Optional[str] = None,
        stream: bool = False
    ) -> str:
        """
        Send a chat message to Ollama, optionally with an image
        
        Args:
            message: The text message
            image_base64: Optional base64 encoded image
            stream: Whether to stream the response
        """
        url = f"{self.base_url}/api/generate"
        
        payload = {
            "model": self.model,
            "prompt": message,
            "stream": stream,
            "options": {
                "temperature": settings.ollama_temperature
            }
        }
        
        # Add image if provided (for vision models)
        if image_base64:
            payload["images"] = [image_base64]
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                result = await response.json()
                return result.get('response', '')
    
    async def chat_with_history(
        self,
        messages: list[dict],
        image_base64: Optional[str] = None
    ) -> str:
        """
        Chat with conversation history
        
        Args:
            messages: List of {role: "user"|"assistant", content: str}
            image_base64: Optional image for current message
        """
        url = f"{self.base_url}/api/chat"
        
        # Convert to Ollama format
        ollama_messages = []
        for msg in messages:
            ollama_msg = {
                "role": msg["role"],
                "content": msg["content"]
            }
            ollama_messages.append(ollama_msg)
        
        # Add image to last message if provided and enhance prompt
        if image_base64 and ollama_messages:
            # Prepend vision instruction to the user's message
            original_content = ollama_messages[-1]["content"]
            ollama_messages[-1]["content"] = f"[You are viewing a screenshot image] {original_content}"
            ollama_messages[-1]["images"] = [image_base64]
        
        payload = {
            "model": self.model,
            "messages": ollama_messages,
            "stream": False,
            "options": {
                "temperature": settings.ollama_temperature
            }
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                result = await response.json()
                return result.get('message', {}).get('content', '')
    
    async def chat_with_history_stream(
        self,
        messages: list[dict],
        image_base64: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """
        Chat with conversation history (streaming)
        
        Args:
            messages: List of {role: "user"|"assistant", content: str}
            image_base64: Optional image for current message
        
        Yields:
            Response chunks as they arrive
        """
        url = f"{self.base_url}/api/chat"
        
        # Convert to Ollama format
        ollama_messages = []
        for msg in messages:
            ollama_msg = {
                "role": msg["role"],
                "content": msg["content"]
            }
            ollama_messages.append(ollama_msg)
        
        # Add image to last message if provided
        if image_base64 and ollama_messages:
            original_content = ollama_messages[-1]["content"]
            ollama_messages[-1]["content"] = f"[You are viewing a screenshot image] {original_content}"
            ollama_messages[-1]["images"] = [image_base64]
        
        payload = {
            "model": self.model,
            "messages": ollama_messages,
            "stream": True,
            "options": {
                "temperature": settings.ollama_temperature
            }
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                async for line in response.content:
                    if line:
                        try:
                            chunk = json.loads(line)
                            if "message" in chunk and "content" in chunk["message"]:
                                yield chunk["message"]["content"]
                        except:
                            pass
    
    async def chat_with_vision(
        self,
        prompt: str,
        images: list[bytes]
    ) -> str:
        """
        Chat with multiple images (for video frame analysis)
        
        Args:
            prompt: The text prompt
            images: List of image bytes
        """
        url = f"{self.base_url}/api/chat"
        
        # Convert images to base64
        images_base64 = []
        for img_bytes in images:
            img_b64 = base64.b64encode(img_bytes).decode('utf-8')
            images_base64.append(img_b64)
        
        messages = [
            {
                "role": "user",
                "content": prompt,
                "images": images_base64
            }
        ]
        
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": settings.ollama_temperature
            }
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                result = await response.json()
                return result.get('message', {}).get('content', '')
    
    async def is_available(self) -> bool:
        """Check if Ollama is running and model is available"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/tags") as response:
                    if response.status == 200:
                        data = await response.json()
                        models = [m['name'] for m in data.get('models', [])]
                        return any(self.model in m for m in models)
            return False
        except:
            return False

# Global instance
ollama_client = OllamaClient()
