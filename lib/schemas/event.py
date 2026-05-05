from datetime import timedelta, time
from pydantic import BaseModel, Field, BeforeValidator
from typing import Annotated, Optional, List, Literal
from lib.helpers.helper import format_time


def normalize_time(value) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, timedelta):
        total_seconds = int(value.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    if isinstance(value, time):
        return value.strftime("%H:%M:%S")
    return format_time(value)


OptionalTime = Annotated[Optional[str], BeforeValidator(normalize_time)]


class Event(BaseModel):
    title: str
    start_date: Optional[str] = Field(default=None, description="Start date of the event.")
    end_date: Optional[str] = Field(default=None, description="End date of the event, if applicable.")
    start_time: OptionalTime = Field(default=None, description="Start time of the event.")
    end_time: OptionalTime = Field(default=None, description="End time of the event, if applicable.")
    image_url: Optional[str] = Field(default=None, description="URL to an image or poster for the event.")
    venue_name: Optional[str] = Field(default=None, description="Name of the venue where the event is taking place.")
    performer_names: Optional[List[str]] = Field(default=None, description="List of performer or band names.")
    indoor_outdoor: Optional[Literal["indoor", "outdoor"]] = Field(default=None, description="'indoor', 'outdoor', or None if unknown.")
    ages: Optional[Literal["21+", "18+", "All Ages"]] = Field(default=None, description="Age requirement for the event if any")
    price_range: Optional[str] = Field(default=None, description="Price or price range for the event.")
    event_page_url: str = Field(description="The absolute URL to the details page for this event.")
    ticket_url: str = Field(description="The absolute URL to the page where you can buy tickets for this event.")

    def clean(self) -> "Event":
        self.title = self.title.replace("’", "'")
        if self.venue_name:
            self.venue_name = self.venue_name.replace("’", "'")
        return self
