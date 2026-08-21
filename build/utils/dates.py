from datetime import datetime, timezone

def get_current_utc_time():
    return datetime.now(timezone.utc)

def format_iso_time(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

def format_date_only(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d")
