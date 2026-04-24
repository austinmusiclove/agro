from datetime import datetime

def format_time(time_str):
    """
    Attempts to parse a variety of time string formats and convert them to the 
    MySQL TIME format (HH:MM:SS). If the string cannot be parsed, returns None.
    """
    if not time_str:
        return None
        
    time_str = str(time_str).strip().lower()
    
    # Try parsing common time formats
    formats = [
        "%I:%M%p",      # 8:00pm
        "%I:%M %p",     # 8:00 pm
        "%I%p",         # 8pm
        "%I %p",        # 8 pm
        "%H:%M:%S",     # 20:00:00
        "%H:%M",        # 20:00
        "%I:%M:%S%p",   # 8:00:00pm
        "%I:%M:%S %p",  # 8:00:00 pm
    ]
    
    for fmt in formats:
        try:
            dt = datetime.strptime(time_str, fmt)
            return dt.strftime("%H:%M:%S")
        except ValueError:
            continue
            
    # If it matches none of the above, return None so it gets saved as NULL
    return None
