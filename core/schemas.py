from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import hashlib

class Issue(BaseModel):
    title: str
    desc: Optional[str] = None
    status: str = "open"
    type: Optional[str] = "task"
    priority: Optional[int] = 2
    parent: Optional[str] = None
    hash_id: str = ""
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = None

    def model_post_init(self, __context):
        if not self.hash_id:
            words = [x for x in [self.title, self.type, self.desc, self.parent] if x is not None]
            sentence = "".join(words)
            self.hash_id = hashlib.sha256(sentence.encode()).hexdigest()[:6]

