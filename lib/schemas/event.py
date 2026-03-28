from pydantic import BaseModel, Field
from typing import Optional, List, Literal

class Event(BaseModel):
    title: str
    start_date: Optional[str] = Field(default=None, description="Start date of the event.")
    end_date: Optional[str] = Field(default=None, description="End date of the event, if applicable.")
    start_time: Optional[str] = Field(default=None, description="Start time of the event.")
    end_time: Optional[str] = Field(default=None, description="End time of the event, if applicable.")
    image: Optional[str] = Field(default=None, description="URL to an image or poster for the event.")
    venue_name: Optional[str] = Field(default=None, description="Name of the venue where the event is taking place.")
    performer_names: Optional[List[str]] = Field(default=None, description="List of performer or band names.")
    indoor_outdoor: Optional[Literal["indoor", "outdoor"]] = Field(default=None, description="'indoor', 'outdoor', or None if unknown.")
    ages: Optional[Literal["21+", "18+", "All Ages"]] = Field(default=None, description="Age requirement for the event if any")
    price: Optional[str] = Field(default=None, description="Price or price range for the event.")
    event_page_url: str = Field(description="The absolute URL to the details page for this event.")

    def clean(self) -> "Event":
        self.title = self.title.replace("'", "'")
        return self
