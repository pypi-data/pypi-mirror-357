from datetime import datetime


def format_date(date=None, format_style="standard"):
    """
    Format a date (default: current date) in specified style.
    Styles: 'standard' (YYYY-MM-DD), 'us' (MM/DD/YYYY), 'eu' (DD/MM/YYYY).
    """
    if date is None:
        date = datetime.now()
    if not isinstance(date, datetime):
        raise TypeError("Date must be a datetime object")

    format_map = {
        "standard": "%Y-%m-%d",
        "us": "%m/%d/%Y",
        "eu": "%d/%m/%Y"
    }
    if format_style not in format_map:
        raise ValueError("Invalid format style. Choose from: standard, us, eu")
    return date.strftime(format_map[format_style])