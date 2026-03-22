from pydantic import BaseModel, Field
from typing import Optional

class Event(BaseModel):
    title: str
    date: Optional[str] = None
    time: Optional[str] = None
    event_page_url: str = Field(description="The absolute URL to the details page for this event.")
