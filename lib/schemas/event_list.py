from pydantic import BaseModel, Field
from typing import List, Optional
from lib.schemas.event import Event

class EventListSchema(BaseModel):
    events: List[Event]
    next_page_url: Optional[str] = Field(
        default=None, 
        description="The absolute URL to the next page of events in the list. Set to null if there is no next page link."
    )
