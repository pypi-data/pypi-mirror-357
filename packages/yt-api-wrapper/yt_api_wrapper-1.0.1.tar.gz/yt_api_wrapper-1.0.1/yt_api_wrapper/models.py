from typing import Optional
from dataclasses import dataclass


@dataclass
class YouTubeError:
    """Custom error class for YouTube API wrapper"""
    error_type: str
    message: str
    details: Optional[str] = None
