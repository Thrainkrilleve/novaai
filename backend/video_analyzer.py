import aiohttp
import asyncio
import tempfile
import os
import re
from pathlib import Path
from typing import Optional, List
from PIL import Image
import io

class VideoAnalyzer:
    """Analyze videos from URLs or Discord attachments"""
    
    def __init__(self):
        self.temp_dir = tempfile.gettempdir()
        self.supported_formats = ['.mp4', '.mov', '.avi', '.mkv', '.webm', '.gif']
        
    def is_video_url(self, url: str) -> bool:
        """Check if URL is a video link"""
        video_patterns = [
            r'(youtube\.com|youtu\.be)',
            r'(twitter\.com|x\.com)/.+/status/.+/video',
            r'(tiktok\.com)',
            r'(instagram\.com)/.+/reel',
            r'(reddit\.com)/.+/comments/.+',
            r'(twitch\.tv)',
        ]
        
        # Check domain patterns
        for pattern in video_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return True
        
        # Check file extension
        return any(url.lower().endswith(ext) for ext in self.supported_formats)
    
    def is_video_attachment(self, attachment) -> bool:
        """Check if Discord attachment is a video"""
        if hasattr(attachment, 'content_type'):
            if attachment.content_type and attachment.content_type.startswith('video/'):
                return True
        
        # Check filename extension
        if hasattr(attachment, 'filename'):
            return any(attachment.filename.lower().endswith(ext) for ext in self.supported_formats)
        
        return False
    
    async def download_video(self, url: str, max_size_mb: int = 50) -> Optional[str]:
        """Download video from URL to temp file"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=60)) as response:
                    if response.status != 200:
                        return None
                    
                    # Check size
                    content_length = response.headers.get('Content-Length')
                    if content_length and int(content_length) > max_size_mb * 1024 * 1024:
                        print(f"⚠️ Video too large: {int(content_length) / 1024 / 1024:.1f}MB")
                        return None
                    
                    # Determine extension
                    content_type = response.headers.get('Content-Type', '')
                    ext = '.mp4'  # default
                    if 'webm' in content_type:
                        ext = '.webm'
                    elif 'quicktime' in content_type or 'mov' in content_type:
                        ext = '.mov'
                    
                    # Download to temp file
                    temp_path = os.path.join(self.temp_dir, f"nova_video_{os.getpid()}{ext}")
                    
                    with open(temp_path, 'wb') as f:
                        async for chunk in response.content.iter_chunked(8192):
                            f.write(chunk)
                    
                    return temp_path
        except Exception as e:
            print(f"❌ Error downloading video: {e}")
            return None
    
    async def extract_frames(self, video_path: str, num_frames: int = 4) -> List[bytes]:
        """Extract frames from video using ffmpeg or Pillow"""
        frames = []
        
        try:
            # Try using ffmpeg if available
            if await self._has_ffmpeg():
                frames = await self._extract_frames_ffmpeg(video_path, num_frames)
            else:
                # Fallback: for GIF/WEBP, use Pillow
                if video_path.lower().endswith(('.gif', '.webp')):
                    frames = await self._extract_frames_pillow(video_path, num_frames)
                else:
                    print("⚠️ ffmpeg not available, cannot extract frames from video")
        except Exception as e:
            print(f"❌ Error extracting frames: {e}")
        
        return frames
    
    async def _has_ffmpeg(self) -> bool:
        """Check if ffmpeg is available"""
        try:
            process = await asyncio.create_subprocess_exec(
                'ffmpeg', '-version',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await process.communicate()
            return process.returncode == 0
        except:
            return False
    
    async def _extract_frames_ffmpeg(self, video_path: str, num_frames: int) -> List[bytes]:
        """Extract frames using ffmpeg"""
        frames = []
        
        try:
            # Get video duration
            process = await asyncio.create_subprocess_exec(
                'ffprobe', '-v', 'error', '-show_entries',
                'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1',
                video_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await process.communicate()
            duration = float(stdout.decode().strip())
            
            # Extract frames at regular intervals
            interval = duration / (num_frames + 1)
            
            for i in range(num_frames):
                timestamp = interval * (i + 1)
                
                # Extract frame to memory
                process = await asyncio.create_subprocess_exec(
                    'ffmpeg', '-ss', str(timestamp), '-i', video_path,
                    '-vframes', '1', '-f', 'image2pipe', '-vcodec', 'png', '-',
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, _ = await process.communicate()
                
                if process.returncode == 0 and stdout:
                    frames.append(stdout)
        except Exception as e:
            print(f"❌ ffmpeg extraction error: {e}")
        
        return frames
    
    async def _extract_frames_pillow(self, path: str, num_frames: int) -> List[bytes]:
        """Extract frames from animated image using Pillow"""
        frames = []
        
        try:
            img = Image.open(path)
            
            # Get total frames
            total_frames = getattr(img, 'n_frames', 1)
            
            # Calculate frame indices
            if total_frames <= num_frames:
                frame_indices = range(total_frames)
            else:
                interval = total_frames // num_frames
                frame_indices = [i * interval for i in range(num_frames)]
            
            for idx in frame_indices:
                img.seek(idx)
                
                # Convert to RGB if necessary
                frame = img.convert('RGB')
                
                # Save to bytes
                buffer = io.BytesIO()
                frame.save(buffer, format='PNG')
                frames.append(buffer.getvalue())
        except Exception as e:
            print(f"❌ Pillow extraction error: {e}")
        
        return frames
    
    def cleanup_video(self, video_path: str):
        """Delete temporary video file"""
        try:
            if os.path.exists(video_path):
                os.remove(video_path)
        except Exception as e:
            print(f"⚠️ Could not cleanup video: {e}")

# Global instance
video_analyzer = VideoAnalyzer()
