from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Attachment:
    type: str  # "pdf", "image", "document", "other"
    filename: str
    url: str
    mime_type: Optional[str] = None
    size_bytes: Optional[int] = None

@dataclass
class Message:
    text: str
    chat_id: str
    user_id: str
    attachments: List[Attachment] = None
    
    def __post_init__(self):
        if self.attachments is None:
            self.attachments = []

@dataclass
class Callback:
    text: str
    attachments: List[Attachment] = None
    
    def __post_init__(self):
        if self.attachments is None:
            self.attachments = []
