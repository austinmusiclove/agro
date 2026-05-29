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


def validate_absolute_url(value) -> str:
    if value is None:
        return value
    if not str(value).startswith(("http://", "https://")):
        raise ValueError(f"URL must be absolute (start with http:// or https://). Got: {value}")
    return str(value)


OptionalTime = Annotated[Optional[str], BeforeValidator(normalize_time)]
AbsoluteUrl = Annotated[str, BeforeValidator(validate_absolute_url)]
OptionalAbsoluteUrl = Annotated[Optional[str], BeforeValidator(lambda v: v if v is None else validate_absolute_url(v))]


class Event(BaseModel):
    title: str
    start_date: Optional[str] = Field(default=None, description="Start date of the event.")
    end_date: Optional[str] = Field(default=None, description="End date of the event, if applicable.")
    start_time: OptionalTime = Field(default=None, description="Start time of the event.")
    end_time: OptionalTime = Field(default=None, description="End time of the event, if applicable.")
    image_url: OptionalAbsoluteUrl = Field(default=None, description="Absolute URL to an image or poster for the event. Must start with http:// or https://. Never return a relative path.")
    venue_name: Optional[str] = Field(default=None, description="Name of the venue where the event is taking place.")
    performer_names: Optional[List[str]] = Field(default=None, description="List of performer or band names.")
    indoor_outdoor: Optional[Literal["indoor", "outdoor"]] = Field(default=None, description="'indoor', 'outdoor', or None if unknown.")
    ages: Optional[Literal["21+", "18+", "All Ages"]] = Field(default=None, description="Age requirement for the event if any")
    price_range: Optional[str] = Field(default=None, description="Price or price range for the event.")
    event_page_url: OptionalAbsoluteUrl = Field(description="Absolute URL to the event details page. Must start with http:// or https://. Never return a relative path like /events/123.")
    event_type: Literal["live_music", "other"] = Field(description="Category of the event.")
    description: Optional[str] = Field(default=None, description="Description of the event.")
    ticket_url: OptionalAbsoluteUrl = Field(description="Absolute URL to the ticket purchase page. Must start with http:// or https://. Never return a relative path.")

    def clean(self) -> "Event":
        self.title = self.title.replace("’", "'")
        if self.venue_name:
            self.venue_name = self.venue_name.replace("’", "'")
        return self
