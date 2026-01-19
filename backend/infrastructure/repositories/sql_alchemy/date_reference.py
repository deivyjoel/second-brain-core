from datetime import datetime, timezone

"""Every time we create a datetime for created_at or last_edited_at, we use this function to ensure it's in UTC."""
def get_utc_now():
    return datetime.now(timezone.utc)