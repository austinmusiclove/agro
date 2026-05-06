from pydantic import BaseModel, Field
from typing import List, Optional
from lib.schemas.event import Event

class EventList(BaseModel):
    events: List[Event]
    next_page_url: Optional[str] = Field(
        default=None,
        description="The absolute URL to the next page of events in the list. Must start with http:// or https://. Never return a relative path. Set to null if there is no next page link."
    )

    def clean(self) -> "EventList":
        for event in self.events:
            event.clean()
        return self
