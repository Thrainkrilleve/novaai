import mss
import base64
from io import BytesIO
from PIL import Image
from typing import Optional
from config import settings

class ScreenCapture:
    """Handle screen capture and processing"""
    
    def __init__(self):
        self.sct = mss.mss()
    
    def capture_screen(self, monitor_number: int = 1) -> Optional[str]:
        """
        Capture screen and return base64 encoded image
        
        Args:
            monitor_number: Which monitor to capture (1 = primary)
            
        Returns:
            Base64 encoded JPEG image or None if error
        """
        try:
            # Get monitor
            monitor = self.sct.monitors[monitor_number]
            
            # Capture screenshot
            screenshot = self.sct.grab(monitor)
            
            # Convert to PIL Image
            img = Image.frombytes(
                'RGB',
                (screenshot.width, screenshot.height),
                screenshot.rgb
            )
            
            # Resize if too large (to save tokens/processing)
            max_dim = settings.screenshot_max_dimension
            if img.width > max_dim or img.height > max_dim:
                ratio = min(max_dim / img.width, max_dim / img.height)
                new_size = (int(img.width * ratio), int(img.height * ratio))
                img = img.resize(new_size, Image.Resampling.LANCZOS)
            
            # Convert to base64 JPEG
            buffer = BytesIO()
            img.save(buffer, format='JPEG', quality=settings.screenshot_quality)
            img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            return img_base64
            
        except Exception as e:
            print(f"Error capturing screen: {e}")
            return None
    
    def capture_region(self, x: int, y: int, width: int, height: int) -> Optional[str]:
        """
        Capture specific region of screen
        
        Args:
            x, y: Top-left coordinates
            width, height: Region dimensions
            
        Returns:
            Base64 encoded JPEG image
        """
        try:
            monitor = {"top": y, "left": x, "width": width, "height": height}
            screenshot = self.sct.grab(monitor)
            
            img = Image.frombytes(
                'RGB',
                (screenshot.width, screenshot.height),
                screenshot.rgb
            )
            
            buffer = BytesIO()
            img.save(buffer, format='JPEG', quality=settings.screenshot_quality)
            img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            return img_base64
            
        except Exception as e:
            print(f"Error capturing region: {e}")
            return None
    
    def get_monitor_count(self) -> int:
        """Get number of monitors"""
        return len(self.sct.monitors) - 1  # Exclude 'all monitors' entry

# Global instance
screen_capture = ScreenCapture()
