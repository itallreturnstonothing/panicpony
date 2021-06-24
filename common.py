from datetime import datetime, timezone


###############################
#    CHANGE THESE VARIABLES   #
#    for config adjustments   #
###############################

api_key = "AIzaSyA-dlBUjVQeuc4a6ZN4RkNUYDFddrVLxrA"

# const
critical_datetime = datetime(year=2017, month=1, day=2, tzinfo=timezone.utc)
# january 2 just to be safe

def parse_date_format(date_str):
    return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
