from pydantic import BaseModel, Field
from typing import Optional, List

class Event(BaseModel):
    title: str
    start_date: Optional[str] = Field(default=None, description="Start date of the event.")
    end_date: Optional[str] = Field(default=None, description="End date of the event, if applicable.")
    start_time: Optional[str] = Field(default=None, description="Start time of the event.")
    end_time: Optional[str] = Field(default=None, description="End time of the event, if applicable.")
    image: Optional[str] = Field(default=None, description="URL to an image or poster for the event.")
    venue_name: Optional[str] = Field(default=None, description="Name of the venue where the event is taking place.")
    venue_id: Optional[str] = Field(default=None, description="Unique identifier for the venue if available.")
    performer_names: Optional[List[str]] = Field(default=None, description="List of performer or band names.")
    is_indoors: Optional[bool] = Field(default=None, description="True if the event is indoors, False if outdoors.")
    ages: Optional[str] = Field(default=None, description="Age requirement for the event, if any.")
    price: Optional[str] = Field(default=None, description="Price or price range for the event.")
    event_list_page_url: Optional[str] = Field(default=None, description="The URL of the page where this event was listed.")
    event_page_url: str = Field(description="The absolute URL to the details page for this event.")
