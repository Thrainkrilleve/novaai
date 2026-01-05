from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application configuration"""
    
    # Server settings
    host: str = "0.0.0.0"  # Listen on all interfaces for VPS deployment
    port: int = 8000
    
    # Production settings (optional)
    domain: str = ""  # Your domain name (e.g., "yourdomain.com")
    frontend_url: str = ""  # Frontend URL if different (e.g., "https://app.yourdomain.com")
    
    # Ollama settings
    ollama_host: str = "http://localhost:11434"
    ollama_model: str = "llama3.2-vision"  # Vision-capable model
    ollama_temperature: float = 0.5  # Lower for faster responses
    
    # Database
    database_url: str = "sqlite+aiosqlite:///./chatbot.db"
    
    # VPS Mode (screen capture and browser disabled)
    vps_mode: bool = True
    
    # Discord bot
    discord_token: str = ""
    discord_bot_token: str = ""
    discord_command_prefix: str = "!"
    
    class Config:
        env_file = ".env"
        extra = "ignore"  # Allow extra fields from .env

settings = Settings()
