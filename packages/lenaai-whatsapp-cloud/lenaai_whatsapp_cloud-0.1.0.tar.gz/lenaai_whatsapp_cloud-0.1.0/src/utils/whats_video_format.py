import ffmpeg
import logging
from typing import Dict, Optional, Tuple

class WhatsAppVideoProcessor:
    """
    A class to handle WhatsApp video format checking and conversion.
    """
    
    def __init__(self):
        """
        Initialize the WhatsApp Video Processor.
        """
        self.logger = logging.getLogger(__name__)
    
    async def check_video_format(self, video_url: str) -> Tuple[bool, Dict[str, bool]]:
        """
        Checks if a video meets WhatsApp's format requirements.
        
        WhatsApp video requirements:
        - Container: MP4
        - Video codec: H.264
        - Audio codec: AAC
        - Max duration: 120 seconds
        - Max size: 16MB
        
        Args:
            video_url: URL or path to the video file
            
        Returns:
            Tuple containing:
            - Boolean indicating if video meets all requirements
            - Dictionary with detailed check results
        """
        try:
            # Probe video file
            probe = ffmpeg.probe(video_url)
            
            # Initialize check results
            checks = {
                'is_mp4': False,
                'is_h264': False,
                'is_aac': False,
                'duration_ok': False,
                'size_ok': False
            }
            
            # Check container format
            checks['is_mp4'] = video_url.lower().endswith('.mp4')
            
            # Get video stream info
            video_stream = next((stream for stream in probe['streams'] 
                               if stream['codec_type'] == 'video'), None)
            
            # Get audio stream info
            audio_stream = next((stream for stream in probe['streams'] 
                               if stream['codec_type'] == 'audio'), None)
            
            if video_stream:
                # Check video codec
                checks['is_h264'] = video_stream['codec_name'].lower() in ['h264', 'avc1']
                
                # Check duration (in seconds)
                duration = float(probe['format'].get('duration', 0))
                checks['duration_ok'] = duration <= 120
                
                # Check file size (in bytes, 16MB = 16*1024*1024)
                size = int(probe['format'].get('size', 0))
                checks['size_ok'] = size <= 16 * 1024 * 1024
            
            if audio_stream:
                # Check audio codec
                checks['is_aac'] = audio_stream['codec_name'].lower() == 'aac'
            
            # All checks must pass for the video to be compatible
            is_compatible = all(checks.values())
            
            self.logger.info(f"Video format check results for {video_url}: {checks}")
            return is_compatible, checks
            
        except Exception as e:
            self.logger.error(f"Error checking video format: {str(e)}")
            return False, {check: False for check in ['is_mp4', 'is_h264', 'is_aac', 'duration_ok', 'size_ok']}

    async def convert_to_whatsapp_format(self, video_url: str) -> Optional[str]:
        """
        Converts video to WhatsApp-compatible format.
        
        Args:
            video_url: URL or path to the video file
            
        Returns:
            URL/path of the converted video if successful, None otherwise
            
        Note: This is an empty implementation. Add your conversion logic here.
        """
        # TODO: Implement video conversion logic
        self.logger.warning("Video conversion not implemented")
        return None

# Create a singleton instance for easy importing
video_processor = WhatsAppVideoProcessor()

# For backward compatibility
async def check_whatsapp_video_format(video_url: str) -> Tuple[bool, Dict[str, bool]]:
    """
    Legacy function to check video format using the WhatsAppVideoProcessor class.
    """
    return await video_processor.check_video_format(video_url)

async def convert_to_whatsapp_format(video_url: str) -> Optional[str]:
    """
    Legacy function to convert video format using the WhatsAppVideoProcessor class.
    """
    return await video_processor.convert_to_whatsapp_format(video_url)