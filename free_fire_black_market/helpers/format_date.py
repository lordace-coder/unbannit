from datetime import datetime, timedelta, timezone

# helper functions
get_weeks_ago:datetime = lambda x:int(x/7)
get_months_ago = lambda x:int(get_weeks_ago(x)/4)


def format_time_ago(date: datetime):
    date = date.replace(tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)
    difference = now - date

    """
        returns 'a long time ago' if  time difference exceeds a year
    """
    if get_months_ago(difference.days) >= 12:
        return "A long time ago"
    elif difference >= timedelta(weeks=4):
        return f"{get_months_ago(difference.days)} months ago"
    if difference >= timedelta(weeks=1):
        return f"{get_weeks_ago(difference.days)} weeks ago"
    elif difference >= timedelta(days=1):
        return f"{difference.days}d ago"

    else:
        return date.strftime("%I:%M %p")


def get_formatted_date(date:datetime):
    date = date.replace(tzinfo=timezone.utc)
    return date.strftime("%d %b %Y")



# if __name__ == "__main__":
#     time = datetime(2023,2,16) 
#     print(get_formatted_date(time))
