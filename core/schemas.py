from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import hashlib
from core.tools import get_config

class Issue(BaseModel):
    hash_id: str = ""
    title: str
    desc: Optional[str] = None
    status: str = "open"
    type: Optional[str] = "task"
    priority: Optional[int] = 2
    parent: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None

    def model_post_init(self, __context):
        if not self.hash_id:
            date = self.created_at.strftime('%m-%d-%Y')
            words = [x for x in [self.title, self.type, self.desc, self.parent, date] if x is not None]
            sentence = "".join(words)
            self.hash_id = hashlib.sha256(sentence.encode()).hexdigest()[:6]

class Dependency(BaseModel):
    from_id: str
    to_id: str

class Comment(BaseModel):
    id: Optional[int] = None  # None lets sqlite assign the INTEGER PRIMARY KEY
    issue_id: str
    body: str
    author: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)

    def model_post_init(self, __context):
        if self.author is None:
            config = get_config()
            self.author = config["author"] if config["author"] else "root"

class Event(BaseModel):
    id: int
    issue_id: str
    action: str
    payload: str
    created_at: datetime = Field(default_factory=datetime.now)